"""Batch article scoring using Bedrock Haiku."""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime

from utils.bedrock import converse
from utils.config import MODELS
from utils.metrics import publish_metrics

from digest.sources.rss import Article

BATCH_SIZE = 10
MAX_CONCURRENT = 2

SCORING_SYSTEM_PROMPT = """\
你是一个技术内容策展人，正在为一份面向技术爱好者的每日精选摘要筛选文章。
请对以下文章进行三个维度的评分（1-10 整数，10 分最高），并为每篇文章分配一个分类标签和提取 2-4 个关键词。

评分维度：
1. relevance（对技术从业者的价值）
   - 10: 所有技术人员都应该知道的重大突破
   - 7-9: 对大多数技术工作者有价值
   - 4-6: 对特定技术领域有价值
   - 1-3: 技术相关性极低

2. quality（深度和写作质量）
   - 10: 深度分析，原创见解，引用充分
   - 7-9: 有深度，独特视角
   - 4-6: 准确，表达清晰
   - 1-3: 浅显或纯粹搬运

3. timeliness（当前阅读价值）
   - 10: 突发新闻或刚发布的重要工具
   - 7-9: 近期热门话题
   - 4-6: 常青内容，不过时
   - 1-3: 过时或无时效价值

分类（必须选一个）：
- ai-ml: AI, LLM, 机器学习, 深度学习
- security: 安全, 隐私, 漏洞, 加密
- engineering: 软件工程, 架构, 编程语言, 系统设计
- tools: 开发工具, 开源, 新库/框架
- opinion: 行业观点, 个人思考, 职业, 文化评论
- other: 不属于以上任何类别

关键词：2-4 个英文关键词（简短，如 "Rust", "LLM", "database", "performance"）

特别注意：与 AI、LLM、机器学习直接相关的文章，relevance 应至少给 7 分。

请以 JSON 格式返回，格式如下：
{"results": [{"index": 0, "relevance": 8, "quality": 7, "timeliness": 9, "category": "ai-ml", "keywords": ["LLM", "cost"]}]}
"""


@dataclass
class ScoredArticle:
    title: str
    link: str
    pub_date: datetime
    description: str
    source_name: str
    source_type: str
    relevance: int = 0
    quality: int = 0
    timeliness: int = 0
    category: str = "other"
    keywords: list[str] = field(default_factory=list)
    total_score: int = 0


def _call_bedrock_with_metrics(
    model_name: str,
    user_text: str,
    system_prompt: str,
    no_metrics: bool = False,
    max_tokens: int = 2048,
) -> dict:
    """Call Bedrock converse() and optionally publish CloudWatch metrics.

    Returns {"text": str, "input_tokens": int, "output_tokens": int, "cost": float}
    """
    messages = [{"role": "user", "content": [{"text": user_text}]}]
    result = converse(model_name, messages, system_prompt, max_tokens=max_tokens)

    pricing = MODELS[model_name]
    cost = (
        (result["input_tokens"] / 1000) * pricing["input_cost_per_1k"]
        + (result["output_tokens"] / 1000) * pricing["output_cost_per_1k"]
    )

    if not no_metrics:
        try:
            publish_metrics(
                model_id=model_name,
                input_tokens=result["input_tokens"],
                output_tokens=result["output_tokens"],
                cost_usd=cost,
                caller="ai-daily",
            )
        except Exception as e:
            print(f"  [CloudWatch publish failed: {e}]")

    return {**result, "cost": cost}


def _build_scoring_input(articles: list[Article]) -> str:
    """Format a batch of articles for the scoring prompt."""
    lines = []
    for i, a in enumerate(articles):
        desc = a.description[:300] if a.description else "(no description)"
        lines.append(f"[{i}] {a.source_name}\nTitle: {a.title}\nDescription: {desc}\n")
    return "\n".join(lines)


def _parse_scores(text: str) -> list[dict]:
    """Extract JSON results from LLM response, handling markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        data = json.loads(text)
        return data.get("results", data) if isinstance(data, dict) else data
    except json.JSONDecodeError:
        return []


def _score_batch(articles: list[Article], no_metrics: bool) -> tuple[list[ScoredArticle], float]:
    """Score a single batch of articles."""
    user_text = _build_scoring_input(articles)
    result = _call_bedrock_with_metrics("haiku", user_text, SCORING_SYSTEM_PROMPT, no_metrics)
    scores = _parse_scores(result["text"])

    scored = []
    for i, a in enumerate(articles):
        s = next((x for x in scores if x.get("index") == i), None)
        if s:
            relevance = s.get("relevance", 5)
            quality = s.get("quality", 5)
            timeliness = s.get("timeliness", 5)
            category = s.get("category", "other")
            keywords = s.get("keywords", [])
            bonus = 3 if category == "ai-ml" else 0
            total = relevance + quality + timeliness + bonus
        else:
            relevance = quality = timeliness = 5
            category = "other"
            keywords = []
            total = 15

        scored.append(ScoredArticle(
            title=a.title, link=a.link, pub_date=a.pub_date,
            description=a.description, source_name=a.source_name,
            source_type=a.source_type,
            relevance=relevance, quality=quality, timeliness=timeliness,
            category=category, keywords=keywords, total_score=total,
        ))
    return scored, result["cost"]


async def score_articles(
    articles: list[Article],
    no_metrics: bool = False,
) -> tuple[list[ScoredArticle], float]:
    """Score all articles using Haiku in batches. Returns (scored_articles, total_cost)."""
    batches = [articles[i:i + BATCH_SIZE] for i in range(0, len(articles), BATCH_SIZE)]
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    loop = asyncio.get_running_loop()
    total_cost = 0.0

    async def run_batch(batch):
        async with semaphore:
            return await loop.run_in_executor(None, _score_batch, batch, no_metrics)

    results = await asyncio.gather(*[run_batch(b) for b in batches])

    all_scored = []
    for scored, cost in results:
        all_scored.extend(scored)
        total_cost += cost

    all_scored.sort(key=lambda a: a.total_score, reverse=True)
    return all_scored, total_cost

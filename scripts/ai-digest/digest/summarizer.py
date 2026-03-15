"""Bilingual article summarization and trend generation using Bedrock Sonnet."""

import asyncio
from dataclasses import dataclass, field
import json
from datetime import datetime

from digest.scoring import ScoredArticle, _call_bedrock_with_metrics

BATCH_SIZE = 10

SUMMARY_SYSTEM_PROMPT = """\
你是一个技术内容摘要专家。请为以下文章完成三件事：
1. **titleZh** (中文标题): 将英文标题翻译成自然的中文。如果原标题已经是中文则保持不变。
2. **summary** (摘要): 4-6 句话的结构化摘要。
   - 结构：核心问题 → 关键论点 → 结论
   - 不要用"本文讨论了"、"这篇文章介绍了"开头
   - 保留具体的技术术语、数字和指标
   - 如有对比，要体现出来
   - 目标：读者 30 秒内决定是否值得花 10 分钟读全文
3. **reason** (推荐理由): 1 句话说明"为什么值得读"（不是"这是什么"）。要和摘要不同。

{lang_instruction}

请以 JSON 格式返回：
{{"results": [{{"index": 0, "titleZh": "...", "summary": "...", "reason": "..."}}]}}
"""

LANG_ZH = "请用中文撰写摘要和推荐理由。如果原文是英文，请翻译为中文。标题翻译也用中文。"
LANG_EN = "Write summaries, reasons, and title translations in English. Keep original English titles as-is."

TREND_SYSTEM_PROMPT = """\
根据以下今日精选技术文章列表，写一段 3-5 句话的"今日看点"总结。
要求：
- 提炼出今天技术圈的 2-3 个主要趋势或话题
- 不要逐篇列举，要做宏观归纳
- 风格简洁有力，像新闻导语

{lang_instruction}

直接返回纯文本总结，不要 JSON，不要 markdown 格式。
"""

CATEGORY_EMOJI = {
    "ai-ml": "🤖",
    "security": "🔒",
    "engineering": "⚙️",
    "tools": "🛠️",
    "opinion": "💬",
    "other": "📌",
}


@dataclass
class SummarizedArticle(ScoredArticle):
    title_zh: str = ""
    summary_zh: str = ""
    reason_zh: str = ""
    summary_en: str = ""
    reason_en: str = ""


def _build_summary_input(articles: list[ScoredArticle]) -> str:
    lines = []
    for i, a in enumerate(articles):
        desc = a.description[:800] if a.description else "(no description)"
        lines.append(
            f"[{i}] {a.source_name}\n"
            f"Title: {a.title}\n"
            f"Link: {a.link}\n"
            f"Description: {desc}\n"
        )
    return "\n".join(lines)


def _build_trend_input(articles: list[ScoredArticle]) -> str:
    lines = []
    for i, a in enumerate(articles[:10]):
        emoji = CATEGORY_EMOJI.get(a.category, "📌")
        lines.append(f"[{i}] {emoji} {a.category} | {a.title}")
    return "\n".join(lines)


def _parse_summary_results(text: str) -> list[dict]:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        data = json.loads(text)
        return data.get("results", data) if isinstance(data, dict) else data
    except json.JSONDecodeError:
        return []


async def _enrich_descriptions(articles: list[ScoredArticle]) -> None:
    """For articles with short descriptions, try to fetch full text via trafilatura."""
    try:
        import trafilatura
    except ImportError:
        return

    loop = asyncio.get_running_loop()

    def _fetch_full_text(url: str) -> str | None:
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                return trafilatura.extract(downloaded)
        except Exception:
            pass
        return None

    for a in articles:
        if len(a.description) < 100 and a.link:
            full_text = await loop.run_in_executor(None, _fetch_full_text, a.link)
            if full_text:
                a.description = full_text[:2000]


def _summarize_batch(
    articles: list[ScoredArticle],
    lang: str,
    no_metrics: bool,
) -> tuple[list[dict], float]:
    """Summarize a batch in one language. Returns (results_list, cost)."""
    lang_instruction = LANG_ZH if lang == "zh" else LANG_EN
    system_prompt = SUMMARY_SYSTEM_PROMPT.format(lang_instruction=lang_instruction)
    user_text = _build_summary_input(articles)

    result = _call_bedrock_with_metrics(
        "sonnet", user_text, system_prompt, no_metrics, max_tokens=4096,
    )
    return _parse_summary_results(result["text"]), result["cost"]


async def summarize_articles(
    articles: list[ScoredArticle],
    no_metrics: bool = False,
) -> tuple[list[SummarizedArticle], float]:
    """Summarize articles with Sonnet, bilingual. Returns (summarized, total_cost)."""
    await _enrich_descriptions(articles)

    loop = asyncio.get_running_loop()
    total_cost = 0.0

    # Chinese pass
    zh_results_all = []
    batches = [articles[i:i + BATCH_SIZE] for i in range(0, len(articles), BATCH_SIZE)]
    for batch in batches:
        results, cost = await loop.run_in_executor(
            None, _summarize_batch, batch, "zh", no_metrics
        )
        zh_results_all.extend(results)
        total_cost += cost

    # English pass
    en_results_all = []
    for batch in batches:
        results, cost = await loop.run_in_executor(
            None, _summarize_batch, batch, "en", no_metrics
        )
        en_results_all.extend(results)
        total_cost += cost

    # Merge
    summarized = []
    for i, a in enumerate(articles):
        zh = next((r for r in zh_results_all if r.get("index") == i), {})
        en = next((r for r in en_results_all if r.get("index") == i), {})

        summarized.append(SummarizedArticle(
            title=a.title, link=a.link, pub_date=a.pub_date,
            description=a.description, source_name=a.source_name,
            source_type=a.source_type,
            relevance=a.relevance, quality=a.quality, timeliness=a.timeliness,
            category=a.category, keywords=a.keywords, total_score=a.total_score,
            title_zh=zh.get("titleZh", a.title),
            summary_zh=zh.get("summary", ""),
            reason_zh=zh.get("reason", ""),
            summary_en=en.get("summary", ""),
            reason_en=en.get("reason", ""),
        ))
    return summarized, total_cost


async def generate_trends(
    articles: list[ScoredArticle],
    no_metrics: bool = False,
) -> tuple[str, str, float]:
    """Generate trend summary in both languages. Returns (zh, en, cost)."""
    loop = asyncio.get_running_loop()
    user_text = _build_trend_input(articles)
    total_cost = 0.0

    # Chinese
    zh_prompt = TREND_SYSTEM_PROMPT.format(lang_instruction="用中文回答。")
    zh_result = await loop.run_in_executor(
        None, _call_bedrock_with_metrics, "sonnet", user_text, zh_prompt, no_metrics, 1024,
    )
    total_cost += zh_result["cost"]

    # English
    en_prompt = TREND_SYSTEM_PROMPT.format(lang_instruction="Write in English.")
    en_result = await loop.run_in_executor(
        None, _call_bedrock_with_metrics, "sonnet", user_text, en_prompt, no_metrics, 1024,
    )
    total_cost += en_result["cost"]

    return zh_result["text"], en_result["text"], total_cost

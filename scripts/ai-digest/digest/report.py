"""Obsidian markdown report generation, dashboard, and archiving."""

import os
import re
import shutil
from datetime import date, timedelta
from pathlib import Path

from digest.summarizer import SummarizedArticle, CATEGORY_EMOJI

# Vault root: scripts/ai-digest/digest/ is three levels below the vault root.
_VAULT_ROOT = str(Path(__file__).resolve().parents[3])

FEED_DIR = "Feeds/AI-Daily"
ARCHIVE_DIR = "Feeds/AI-Daily/archive"
DASHBOARD_FILE = "Feeds/AI-Daily/Dashboard.md"

CATEGORY_LABELS = {
    "ai-ml": "AI / ML",
    "security": "Security",
    "engineering": "Engineering",
    "tools": "Tools",
    "opinion": "Opinion",
    "other": "Other",
}


def _relative_time(pub_date) -> str:
    from datetime import datetime, timezone

    delta = datetime.now(timezone.utc) - pub_date
    hours = int(delta.total_seconds() / 3600)
    if hours < 1:
        return "just now"
    if hours < 24:
        return f"{hours}h ago"
    return f"{hours // 24}d ago"


def _format_article_zh(i: int, a: SummarizedArticle) -> str:
    emoji = CATEGORY_EMOJI.get(a.category, "📌")
    rank = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
    tags = ", ".join(a.keywords) if a.keywords else ""
    return (
        f"> [!tip] {rank} {a.title_zh}\n"
        f"> [{a.title}]({a.link})\n"
        f"> — {a.source_name} · {_relative_time(a.pub_date)} · {emoji} {CATEGORY_LABELS.get(a.category, a.category)}\n"
        f">\n"
        f"> {a.summary_zh}\n"
        f">\n"
        f"> 💡 **为什么值得读**: {a.reason_zh}\n"
        f"> 🏷️ {tags}\n"
    )


def _format_article_en(i: int, a: SummarizedArticle) -> str:
    emoji = CATEGORY_EMOJI.get(a.category, "📌")
    rank = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
    tags = ", ".join(a.keywords) if a.keywords else ""
    return (
        f"> [!tip] {rank} {a.title}\n"
        f"> [{a.title}]({a.link})\n"
        f"> — {a.source_name} · {_relative_time(a.pub_date)} · {emoji} {CATEGORY_LABELS.get(a.category, a.category)}\n"
        f">\n"
        f"> {a.summary_en}\n"
        f">\n"
        f"> 💡 **Why read**: {a.reason_en}\n"
        f"> 🏷️ {tags}\n"
    )


def format_zh_report(
    articles: list[SummarizedArticle],
    trend_zh: str,
    stats: dict,
    today: date,
) -> str:
    lines = [
        "---",
        f"date: {today.isoformat()}",
        "tags: [ai-daily, digest]",
        "lang: zh",
        f"sources: {stats.get('sources_total', 0)} RSS (Karpathy curated)",
        f"articles_scanned: {stats.get('articles_after_dedup', 0)}",
        f"articles_selected: {stats.get('articles_selected', 0)}",
        f"bedrock_cost: ${stats.get('bedrock_cost', 0):.3f}",
        "---",
        "",
        f"# 🗞️ AI 早报 — {today.isoformat()}",
        "",
        f"> Karpathy 推荐的 {stats.get('sources_total', 90)} 个顶级技术博客 | Bedrock Haiku+Sonnet 生成",
        f"> English version: [[{today.isoformat()}-en]]",
        "",
        "## 📝 今日看点",
        "",
        trend_zh,
        "",
        "---",
        "",
        "## 🏆 今日必读",
        "",
    ]

    for i, a in enumerate(articles):
        lines.append(_format_article_zh(i, a))
        lines.append("")

    # Stats table
    lines.extend([
        "---",
        "",
        "## 📊 数据概览",
        "",
        "| 扫描源 | 抓取文章 | 去重后 | 精选 |",
        "|:---:|:---:|:---:|:---:|",
        f"| {stats.get('feeds_ok', 0)}/{stats.get('sources_total', 0)} | "
        f"{stats.get('articles_fetched', 0)} | "
        f"{stats.get('articles_after_dedup', 0)} | "
        f"**{stats.get('articles_selected', 0)}** |",
        "",
        "---",
        "",
    ])

    # Category sections
    categories = {}
    for a in articles:
        categories.setdefault(a.category, []).append(a)

    for cat, cat_articles in categories.items():
        emoji = CATEGORY_EMOJI.get(cat, "📌")
        label = CATEGORY_LABELS.get(cat, cat)
        lines.append(f"## {emoji} {label}")
        lines.append("")
        for a in cat_articles:
            lines.append(f"- [[#{a.title_zh}|{a.title_zh}]] — {a.source_name}")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append(
        f"*Bedrock: {stats.get('bedrock_calls', 0)} calls | "
        f"${stats.get('bedrock_cost', 0):.3f} → CloudWatch ✅*"
    )
    lines.append("")

    return "\n".join(lines)


def format_en_report(
    articles: list[SummarizedArticle],
    trend_en: str,
    stats: dict,
    today: date,
) -> str:
    lines = [
        "---",
        f"date: {today.isoformat()}",
        "tags: [ai-daily, digest]",
        "lang: en",
        f"sources: {stats.get('sources_total', 0)} RSS (Karpathy curated)",
        f"articles_scanned: {stats.get('articles_after_dedup', 0)}",
        f"articles_selected: {stats.get('articles_selected', 0)}",
        f"bedrock_cost: ${stats.get('bedrock_cost', 0):.3f}",
        "---",
        "",
        f"# 🗞️ AI Daily Digest — {today.isoformat()}",
        "",
        f"> {stats.get('sources_total', 90)} Karpathy-curated top tech blogs | Bedrock Haiku+Sonnet",
        f"> 中文版: [[{today.isoformat()}]]",
        "",
        "## 📝 Today's Highlights",
        "",
        trend_en,
        "",
        "---",
        "",
        "## 🏆 Top Picks",
        "",
    ]

    for i, a in enumerate(articles):
        lines.append(_format_article_en(i, a))
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 📊 Stats",
        "",
        "| Sources | Fetched | After Dedup | Selected |",
        "|:---:|:---:|:---:|:---:|",
        f"| {stats.get('feeds_ok', 0)}/{stats.get('sources_total', 0)} | "
        f"{stats.get('articles_fetched', 0)} | "
        f"{stats.get('articles_after_dedup', 0)} | "
        f"**{stats.get('articles_selected', 0)}** |",
        "",
        "---",
        f"*Bedrock: {stats.get('bedrock_calls', 0)} calls | "
        f"${stats.get('bedrock_cost', 0):.3f} → CloudWatch ✅*",
        "",
    ])

    return "\n".join(lines)


def generate_reports(
    articles: list[SummarizedArticle],
    trend_zh: str,
    trend_en: str,
    stats: dict,
    vault_path: str = _VAULT_ROOT,
    today: date | None = None,
) -> tuple[Path, Path]:
    """Generate Chinese and English Obsidian reports. Returns (zh_path, en_path)."""
    today = today or date.today()
    vault = Path(vault_path).expanduser()
    out_dir = vault / FEED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    zh_content = format_zh_report(articles, trend_zh, stats, today)
    en_content = format_en_report(articles, trend_en, stats, today)

    zh_path = out_dir / f"{today.isoformat()}.md"
    en_path = out_dir / f"{today.isoformat()}-en.md"

    zh_path.write_text(zh_content, encoding="utf-8")
    en_path.write_text(en_content, encoding="utf-8")

    return zh_path, en_path


def update_dashboard(
    vault_path: str = _VAULT_ROOT,
    today: date | None = None,
) -> Path:
    """Update the Dashboard.md index file with recent 14 days."""
    today = today or date.today()
    vault = Path(vault_path).expanduser()
    out_dir = vault / FEED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    dash_path = vault / DASHBOARD_FILE

    # Scan for existing daily reports
    date_re = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
    entries = []
    for f in out_dir.iterdir():
        m = date_re.match(f.name)
        if m:
            d = date.fromisoformat(m.group(1))
            if (today - d).days <= 14:
                entries.append(d)
    entries.sort(reverse=True)

    lines = [
        "---",
        f"date: {today.isoformat()}",
        "tags: [ai-daily, dashboard]",
        "---",
        "",
        "# AI Daily Digest",
        "",
        "## Quick Links",
        "",
    ]

    if entries:
        latest = entries[0]
        lines.append(f"- Latest: [[{latest.isoformat()}]]")
        lines.append(f"- Latest (EN): [[{latest.isoformat()}-en]]")
    else:
        lines.append("- No digests yet")

    lines.extend([
        "",
        "## Recent Digests",
        "",
        "| Date | ZH | EN |",
        "|------|----|----|",
    ])

    for d in entries:
        lines.append(f"| {d.isoformat()} | [[{d.isoformat()}]] | [[{d.isoformat()}-en]] |")

    lines.append("")
    dash_path.write_text("\n".join(lines), encoding="utf-8")
    return dash_path


def archive_old_reports(
    vault_path: str = _VAULT_ROOT,
    keep_days: int = 14,
) -> int:
    """Move reports older than keep_days to archive/. Returns count of moved files."""
    vault = Path(vault_path).expanduser()
    out_dir = vault / FEED_DIR
    archive_dir = vault / ARCHIVE_DIR
    cutoff = date.today() - timedelta(days=keep_days)

    date_re = re.compile(r"^(\d{4}-\d{2}-\d{2})(-en)?\.md$")
    moved = 0

    if not out_dir.exists():
        return 0

    for f in out_dir.iterdir():
        m = date_re.match(f.name)
        if m:
            d = date.fromisoformat(m.group(1))
            if d < cutoff:
                archive_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(f), str(archive_dir / f.name))
                moved += 1

    return moved

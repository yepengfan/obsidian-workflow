"""Assemble enriched Claude Code plugins into Obsidian markdown weekly reports.

Reads enriched JSON from TMPDIR_CC_PLUGINS, merges with state, and writes:
- ZH weekly report (YYYY-WXX.md)
- EN weekly report (YYYY-WXX-en.md)
- Dashboard.md (index of all reports)
- Updated state.json

Environment variables:
    TMPDIR_CC_PLUGINS — directory containing fetched.json and enriched.json
    WEEK             — ISO week string (e.g., 2026-W14)
    TODAY            — ISO date (e.g., 2026-04-03)
    VAULT_DIR        — path to Obsidian vault root
"""

import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
STATE_PATH = SCRIPT_DIR / "state.json"

CATEGORY_EMOJI = {
    "productivity": "\u26a1",
    "code-quality": "\U0001f50d",
    "integration": "\U0001f517",
    "knowledge": "\U0001f4da",
    "devops": "\U0001f680",
    "other": "\U0001f4e6",
}

CATEGORY_LABEL = {
    "productivity": "Productivity",
    "code-quality": "Code Quality",
    "integration": "Integration",
    "knowledge": "Knowledge",
    "devops": "DevOps",
    "other": "Other",
}

RANK_EMOJI = {1: "1\ufe0f\u20e3", 2: "2\ufe0f\u20e3", 3: "3\ufe0f\u20e3", 4: "4\ufe0f\u20e3", 5: "5\ufe0f\u20e3"}


def rank_str(rank: int) -> str:
    return RANK_EMOJI.get(rank, f"#{rank}")


def score_badge(score: float) -> str:
    """Return score with star rating."""
    return f"\u2b50 {score:.1f}"


def npm_stats(plugin: dict) -> str:
    """Format npm stats string."""
    npm = plugin.get("npm_info")
    if not npm:
        return ""
    parts = []
    if npm.get("latest_version"):
        parts.append(f"v{npm['latest_version']}")
    if npm.get("weekly_downloads"):
        dl = npm["weekly_downloads"]
        if dl >= 1000:
            parts.append(f"\U0001f4e5 {dl / 1000:.1f}k/wk")
        else:
            parts.append(f"\U0001f4e5 {dl}/wk")
    return " \u00b7 ".join(parts)


# ── Report builders (Chinese) ──────────────────────────────────────

def build_new_callout_zh(plugin: dict) -> str:
    cat_emoji = CATEGORY_EMOJI.get(plugin["category"], "\U0001f4e6")
    cat_label = CATEGORY_LABEL.get(plugin["category"], "Other")
    npm = npm_stats(plugin)
    npm_line = f" \u00b7 {npm}" if npm else ""
    tags = ", ".join(plugin.get("tags", []))
    return f"""> [!tip] {rank_str(plugin["rank"])} {plugin["name"]} {score_badge(plugin["score"])} \u00b7 {cat_emoji} {cat_label}
> [GitHub]({plugin["repo_url"]}){npm_line} \u00b7 \u2b50 {plugin["stars"]}
> `{plugin.get("install_cmd", "")}`
>
> {plugin.get("summary_zh", "")}
>
> \U0001f3f7\ufe0f {tags}"""


def build_updated_callout_zh(plugin: dict) -> str:
    cat_emoji = CATEGORY_EMOJI.get(plugin["category"], "\U0001f4e6")
    prev = plugin.get("previous_version", "?")
    curr = plugin.get("npm_info", {}).get("latest_version", "?")
    return f"""> [!info] {plugin["name"]} `{prev}` \u2192 `{curr}` \u00b7 {cat_emoji} {CATEGORY_LABEL.get(plugin["category"], "Other")}
> [GitHub]({plugin["repo_url"]})
>
> {plugin.get("summary_zh", "")}"""


# ── Report builders (English) ──────────────────────────────────────

def build_new_callout_en(plugin: dict) -> str:
    cat_emoji = CATEGORY_EMOJI.get(plugin["category"], "\U0001f4e6")
    cat_label = CATEGORY_LABEL.get(plugin["category"], "Other")
    npm = npm_stats(plugin)
    npm_line = f" \u00b7 {npm}" if npm else ""
    tags = ", ".join(plugin.get("tags", []))
    return f"""> [!tip] {rank_str(plugin["rank"])} {plugin["name"]} {score_badge(plugin["score"])} \u00b7 {cat_emoji} {cat_label}
> [GitHub]({plugin["repo_url"]}){npm_line} \u00b7 \u2b50 {plugin["stars"]}
> `{plugin.get("install_cmd", "")}`
>
> {plugin.get("summary_en", "")}
>
> \U0001f3f7\ufe0f {tags}"""


def build_updated_callout_en(plugin: dict) -> str:
    cat_emoji = CATEGORY_EMOJI.get(plugin["category"], "\U0001f4e6")
    prev = plugin.get("previous_version", "?")
    curr = plugin.get("npm_info", {}).get("latest_version", "?")
    return f"""> [!info] {plugin["name"]} `{prev}` \u2192 `{curr}` \u00b7 {cat_emoji} {CATEGORY_LABEL.get(plugin["category"], "Other")}
> [GitHub]({plugin["repo_url"]})
>
> {plugin.get("summary_en", "")}"""


# ── Full report assembly ───────────────────────────────────────────

def write_zh_report(
    new_plugins: list, updated_plugins: list, stats: dict,
    week: str, today: str, output_path: Path,
) -> None:
    total = stats.get("after_dedup", 0)
    new_count = len(new_plugins)
    updated_count = len(updated_plugins)

    new_section = ""
    if new_plugins:
        callouts = "\n\n".join(build_new_callout_zh(p) for p in new_plugins)
        new_section = f"## \U0001f195 \u65b0\u53d1\u73b0\n\n{callouts}"

    updated_section = ""
    if updated_plugins:
        callouts = "\n\n".join(build_updated_callout_zh(p) for p in updated_plugins)
        updated_section = f"## \U0001f4e6 \u7248\u672c\u66f4\u65b0\n\n{callouts}"

    report = f"""---
date: {today}
week: "{week}"
tags: [cc-plugins, digest]
lang: zh
plugins_discovered: {total}
plugins_new: {new_count}
plugins_updated: {updated_count}
generator: claude-code
---

# Claude Code Plugins \u00b7 {week}

> \u672c\u5468\u626b\u63cf {total} \u4e2a\u63d2\u4ef6\uff0c\u53d1\u73b0 {new_count} \u4e2a\u65b0\u63d2\u4ef6\uff0c{updated_count} \u4e2a\u7248\u672c\u66f4\u65b0
> English version: [[{week}-en]]

{new_section}

{updated_section}

## \U0001f4ca \u672c\u5468\u7edf\u8ba1
- \u626b\u63cf\u63d2\u4ef6: {total}
- \u65b0\u53d1\u73b0: {new_count}
- \u7248\u672c\u66f4\u65b0: {updated_count}

---
*Generated by Claude Code*
"""
    output_path.write_text(report, encoding="utf-8")


def write_en_report(
    new_plugins: list, updated_plugins: list, stats: dict,
    week: str, today: str, output_path: Path,
) -> None:
    total = stats.get("after_dedup", 0)
    new_count = len(new_plugins)
    updated_count = len(updated_plugins)

    new_section = ""
    if new_plugins:
        callouts = "\n\n".join(build_new_callout_en(p) for p in new_plugins)
        new_section = f"## \U0001f195 New Discoveries\n\n{callouts}"

    updated_section = ""
    if updated_plugins:
        callouts = "\n\n".join(build_updated_callout_en(p) for p in updated_plugins)
        updated_section = f"## \U0001f4e6 Version Updates\n\n{callouts}"

    report = f"""---
date: {today}
week: "{week}"
tags: [cc-plugins, digest]
lang: en
plugins_discovered: {total}
plugins_new: {new_count}
plugins_updated: {updated_count}
generator: claude-code
---

# Claude Code Plugins \u00b7 {week}

> Scanned {total} plugins, discovered {new_count} new, {updated_count} version updates
> \u4e2d\u6587\u7248: [[{week}]]

{new_section}

{updated_section}

## \U0001f4ca Weekly Stats
- Plugins scanned: {total}
- New discoveries: {new_count}
- Version updates: {updated_count}

---
*Generated by Claude Code*
"""
    output_path.write_text(report, encoding="utf-8")


# ── Dashboard ──────────────────────────────────────────────────────

def write_dashboard(today: str, feed_dir: Path) -> None:
    """Rebuild Dashboard.md from existing weekly report files."""
    weeks = set()
    for f in feed_dir.glob("*.md"):
        name = f.stem
        if name == "Dashboard" or name.endswith("-en"):
            continue
        # Match YYYY-WXX format
        if len(name) >= 7 and name[4] == "-" and name[5] == "W":
            weeks.add(name)

    sorted_weeks = sorted(weeks, reverse=True)[:14]

    if not sorted_weeks:
        return

    latest = sorted_weeks[0]
    rows = "\n".join(f"| {w} | [[{w}]] | [[{w}-en]] |" for w in sorted_weeks)

    dashboard = f"""---
date: {today}
tags: [cc-plugins, dashboard]
---

# Claude Code Plugins

## Quick Links

- Latest: [[{latest}]]
- Latest (EN): [[{latest}-en]]

## Weekly Reports

| Week | ZH | EN |
|------|----|----|
{rows}
"""
    (feed_dir / "Dashboard.md").write_text(dashboard, encoding="utf-8")


# ── State update ───────────────────────────────────────────────────

def update_state(all_plugins: list, week: str) -> None:
    """Update state.json with current plugin versions."""
    # Load existing state
    state = {"last_run": None, "plugins": {}}
    if STATE_PATH.exists():
        try:
            state = json.loads(STATE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    known = state.get("plugins", {})

    for plugin in all_plugins:
        url = plugin.get("repo_url", "")
        if not url:
            continue

        npm = plugin.get("npm_info") or {}
        existing = known.get(url, {})

        known[url] = {
            "name": plugin.get("name", ""),
            "npm_package": npm.get("npm_package", existing.get("npm_package", "")),
            "last_version": npm.get("latest_version", existing.get("last_version", "")),
            "first_seen": existing.get("first_seen", week),
            "last_checked": week,
            "stars": plugin.get("stars", 0),
        }

    state["last_run"] = week
    state["plugins"] = known
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print(f"[reports] State updated: {len(known)} plugins tracked.", file=sys.stderr)


# ── Main ───────────────────────────────────────────────────────────

def main() -> None:
    tmpdir = os.environ["TMPDIR_CC_PLUGINS"]
    week = os.environ["WEEK"]
    today = os.environ["TODAY"]
    vault_dir = Path(os.environ["VAULT_DIR"])
    feed_dir = vault_dir / "Feeds" / "CC-Plugins"

    feed_dir.mkdir(parents=True, exist_ok=True)

    # Load inputs
    fetched = json.loads(Path(f"{tmpdir}/fetched.json").read_text())
    enriched = json.loads(Path(f"{tmpdir}/enriched.json").read_text())

    stats = fetched.get("stats", {})
    enriched_list = enriched.get("enriched", [])

    # Build lookup from fetched plugins
    fetched_by_url: dict[str, dict] = {
        p["repo_url"]: p for p in fetched.get("plugins", [])
    }

    # Merge: start with fetched base, overlay enriched fields
    all_plugins = []
    for plugin in enriched_list:
        url = plugin.get("repo_url", "")
        base = fetched_by_url.get(url, {})
        merged = {**base, **plugin}
        all_plugins.append(merged)

    print(f"[reports] Loaded {len(all_plugins)} enriched plugins.", file=sys.stderr)

    # Split into new and updated
    new_plugins = [p for p in all_plugins if p.get("change_type") == "new"]
    updated_plugins = [p for p in all_plugins if p.get("change_type") == "updated"]

    # For new plugins, filter to score >= 6 (quality threshold)
    new_plugins = [p for p in new_plugins if p.get("score", 0) >= 6]
    new_plugins.sort(key=lambda p: p.get("score", 0), reverse=True)

    print(
        f"[reports] Report content: {len(new_plugins)} new (score>=6), "
        f"{len(updated_plugins)} updated.",
        file=sys.stderr,
    )

    # Write reports
    zh_path = feed_dir / f"{week}.md"
    write_zh_report(new_plugins, updated_plugins, stats, week, today, zh_path)
    print(f"[reports]   Wrote {zh_path}", file=sys.stderr)

    en_path = feed_dir / f"{week}-en.md"
    write_en_report(new_plugins, updated_plugins, stats, week, today, en_path)
    print(f"[reports]   Wrote {en_path}", file=sys.stderr)

    write_dashboard(today, feed_dir)
    print(f"[reports]   Wrote {feed_dir / 'Dashboard.md'}", file=sys.stderr)

    # Update state with ALL enriched plugins (not just reported ones)
    update_state(all_plugins, week)


if __name__ == "__main__":
    main()

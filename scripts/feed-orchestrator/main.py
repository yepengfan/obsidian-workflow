"""Feed Orchestrator — direct Python pipeline.

Runs all feed pipelines sequentially: check → fetch → enrich → write → archive.
No Agent SDK / Claude Code CLI dependency. Enrichment uses Anthropic SDK directly.

Usage:
    python main.py --vault-path /path/to/vault
    python main.py --vault-path /path/to/vault --feeds ai-digest,github-trending,engineering-blogs
    bash load-env.sh  # (from Obsidian Shell Commands)
"""

import argparse
import asyncio
import json
import sys
import traceback
from pathlib import Path

from feeds import (
    get_feed_config,
    check_module_enabled,
    check_report_exists,
    run_fetch,
    run_enrich,
    run_write_reports,
    archive_old_reports,
    ReportExistsError,
    FetchError,
)
from status import StatusReporter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.llm_runner import backend_summary, validate_backend_credentials  # noqa: E402

ALL_FEEDS = {
    "ai-digest": "(daily) — AI/ML news from 92 RSS feeds",
    "github-trending": "(daily) — Trending GitHub repositories",
    "engineering-blogs": "(daily) — Top company engineering blog posts",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Feed Orchestrator")
    parser.add_argument(
        "--vault-path",
        type=Path,
        required=True,
        help="Path to the Obsidian vault root",
    )
    parser.add_argument(
        "--feeds",
        type=str,
        default=None,
        help="Comma-separated feed names to run (default: all). "
        "E.g. --feeds ai-digest,github-trending,engineering-blogs",
    )
    return parser.parse_args()


async def run_feed(
    feed_name: str,
    config: dict,
    vault_path: Path,
    reporter: StatusReporter,
) -> str:
    """Run a single feed pipeline. Returns status emoji + message."""

    # 1. Check module enabled
    enabled = check_module_enabled(vault_path, config["module"])
    if not enabled:
        reporter.update_feed(feed_name, "disabled", message="Module disabled")
        return f"⛔ {feed_name}: disabled"

    # 2. Check existing report
    existing = check_report_exists(config)
    if existing:
        reporter.update_feed(
            feed_name, "skipped",
            message="Report already exists",
            output_path=str(existing),
        )
        return f"⏭️ {feed_name}: skipped (exists: {existing})"

    # 3. Fetch
    reporter.update_feed(feed_name, "running", message="Fetching...")
    try:
        fetched_json = await run_fetch(feed_name, config, vault_path)
    except ReportExistsError:
        reporter.update_feed(feed_name, "skipped", message="Report exists (fetcher check)")
        return f"⏭️ {feed_name}: skipped"
    except (FetchError, Exception) as e:
        reporter.update_feed(feed_name, "failed", error=str(e))
        return f"❌ {feed_name}: fetch failed — {e}"

    data = json.loads(fetched_json)
    items = data.get("articles", data.get("repos", []))
    print(f"[{feed_name}] Fetched {len(items)} items", file=sys.stderr)
    reporter.update_feed(feed_name, "running", message=f"Fetched {len(items)} items")

    # 4. Enrich (validate LLM backend only when there are items to enrich)
    reporter.update_feed(feed_name, "running", message="Enriching...")
    try:
        if items:
            validate_backend_credentials()
            print(f"[{feed_name}] LLM backend: {backend_summary()}", file=sys.stderr)
        enriched_json = await run_enrich(feed_name, config, fetched_json)
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[{feed_name}] Enrich error:\n{tb}", file=sys.stderr)
        reporter.update_feed(feed_name, "failed", error=str(e))
        return f"❌ {feed_name}: enrich failed — {e}"

    # Parse enrichment stats
    enriched = json.loads(enriched_json)
    if feed_name == "ai-digest":
        scored = json.loads(enriched.get("scored", "{}"))
        enrich_count = len(scored.get("top_articles", []))
    else:
        enrich_count = len(enriched.get("enriched", []))
    print(f"[{feed_name}] Enriched {enrich_count} items", file=sys.stderr)
    reporter.update_feed(feed_name, "running", message=f"Enriched {enrich_count}")

    # 5. Write report
    reporter.update_feed(feed_name, "running", message="Writing report...")
    try:
        report_path = await run_write_reports(
            feed_name, config, vault_path, fetched_json, enriched_json
        )
    except Exception as e:
        reporter.update_feed(feed_name, "failed", error=str(e))
        return f"❌ {feed_name}: write failed — {e}"

    reporter.update_feed(
        feed_name, "success",
        message="Done",
        output_path=report_path,
    )
    print(f"[{feed_name}] ✅ {report_path}", file=sys.stderr)

    # 6. Archive old reports
    try:
        archived = archive_old_reports(config)
        if archived:
            print(f"[{feed_name}] Archived {len(archived)} old reports", file=sys.stderr)
    except Exception as e:
        print(f"[{feed_name}] Archive warning: {e}", file=sys.stderr)

    return f"✅ {feed_name}: {report_path}"


async def main() -> int:
    args = parse_args()
    vault_path = args.vault_path.resolve()

    if not vault_path.exists():
        print(f"ERROR: Vault path does not exist: {vault_path}", file=sys.stderr)
        return 1

    # Parse --feeds (default: all)
    if args.feeds:
        feed_names = [f.strip() for f in args.feeds.split(",") if f.strip()]
        invalid = [f for f in feed_names if f not in ALL_FEEDS]
        if invalid:
            print(f"ERROR: Unknown feeds: {invalid}. Valid: {list(ALL_FEEDS)}", file=sys.stderr)
            return 1
    else:
        feed_names = list(ALL_FEEDS)

    # Initialize
    configs = get_feed_config(vault_path)
    reporter = StatusReporter(vault_path, feed_names=feed_names)

    # Check concurrent run lock
    if reporter.check_concurrent_lock():
        print("ERROR: Another feed run is already in progress.", file=sys.stderr)
        return 1

    reporter.write_initial()
    print(f"[orchestrator] Starting {feed_names}...", file=sys.stderr)

    # Run each feed sequentially
    results = []
    for name in feed_names:
        try:
            result = await run_feed(name, configs[name], vault_path, reporter)
            results.append(result)
        except Exception as e:
            reporter.update_feed(name, "failed", error=str(e))
            results.append(f"❌ {name}: unexpected error — {e}")
            print(f"[{name}] Unexpected: {traceback.format_exc()}", file=sys.stderr)

    # Summary
    generated = sum(1 for r in results if r.startswith("✅"))
    skipped = sum(1 for r in results if r.startswith("⏭️"))
    failed = sum(1 for r in results if r.startswith("❌"))

    summary_lines = results + [f"\nTotal: {generated} generated, {skipped} skipped, {failed} failed"]
    summary = "\n".join(summary_lines)

    reporter.write_final(summary)
    print(f"\n{summary}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

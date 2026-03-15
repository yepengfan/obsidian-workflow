"""AI Daily Digest — pipeline orchestration and CLI."""

import argparse
import asyncio
import sys
from datetime import date
from pathlib import Path

# Vault root: scripts/ai-digest/ is two levels below the vault root.
_VAULT_ROOT = str(Path(__file__).resolve().parents[2])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Daily Digest")
    parser.add_argument("--hours", type=int, default=48, help="Time window in hours")
    parser.add_argument("--top-n", type=int, default=15, help="Number of articles to summarize")
    parser.add_argument("--vault-path", default=_VAULT_ROOT, help="Obsidian vault path")
    parser.add_argument("--stdout", action="store_true", help="Print to terminal only")
    parser.add_argument("--no-metrics", action="store_true", help="Skip CloudWatch metrics")
    return parser.parse_args()


async def run_pipeline(args: argparse.Namespace) -> None:
    from digest.sources.rss import fetch_all_feeds
    from digest.dedup import deduplicate
    from digest.scoring import score_articles
    from digest.summarizer import summarize_articles, generate_trends
    from digest.report import generate_reports, update_dashboard, archive_old_reports
    from digest.feeds import RSS_FEEDS

    today = date.today()
    vault = Path(args.vault_path).expanduser()
    report_path = vault / "Feeds" / "AI-Daily" / f"{today.isoformat()}.md"

    # Idempotency check
    if not args.stdout and report_path.exists():
        print(f"Today's digest already exists: {report_path}")
        return

    stats = {
        "sources_total": len(RSS_FEEDS),
        "bedrock_cost": 0.0,
        "bedrock_calls": 0,
    }

    # Step 1: Fetch
    print(f"[digest] Fetching {len(RSS_FEEDS)} RSS feeds...")
    articles, feeds_ok = await fetch_all_feeds(hours=args.hours)
    stats["feeds_ok"] = feeds_ok
    stats["articles_fetched"] = len(articles)
    print(f"[digest] Fetched {len(articles)} articles from {feeds_ok}/{len(RSS_FEEDS)} feeds")

    if not articles:
        print("[digest] No articles found. Exiting.")
        return

    # Step 2: Dedup
    deduped = deduplicate(articles)
    stats["articles_after_dedup"] = len(deduped)
    print(f"[digest] Dedup: {len(articles)} → {len(deduped)} articles")

    # Step 3: Score
    print(f"[digest] Scoring {len(deduped)} articles with Haiku...")
    scored, score_cost = await score_articles(deduped, no_metrics=args.no_metrics)
    stats["bedrock_cost"] += score_cost
    num_score_batches = -(-len(deduped) // 10)  # ceil division
    stats["bedrock_calls"] += num_score_batches
    print(f"[digest] Scoring complete. Top score: {scored[0].total_score if scored else 0}")

    # Step 4: Select top N
    top_articles = scored[:args.top_n]
    stats["articles_selected"] = len(top_articles)

    # Step 5: Summarize
    print(f"[digest] Summarizing top {len(top_articles)} with Sonnet (zh + en)...")
    summarized, summary_cost = await summarize_articles(top_articles, no_metrics=args.no_metrics)
    stats["bedrock_cost"] += summary_cost
    num_summary_batches = -(-len(top_articles) // 10) * 2  # zh + en
    stats["bedrock_calls"] += num_summary_batches
    print("[digest] Summarization complete.")

    # Step 6: Trends
    print("[digest] Generating trend summary...")
    trend_zh, trend_en, trend_cost = await generate_trends(scored, no_metrics=args.no_metrics)
    stats["bedrock_cost"] += trend_cost
    stats["bedrock_calls"] += 2  # zh + en

    # Step 7: Output
    if args.stdout:
        from digest.report import format_zh_report
        print("\n" + format_zh_report(summarized, trend_zh, stats, today))
    else:
        zh_path, en_path = generate_reports(
            summarized, trend_zh, trend_en, stats,
            vault_path=args.vault_path, today=today,
        )
        print(f"[digest] Reports written:")
        print(f"  ZH: {zh_path}")
        print(f"  EN: {en_path}")

        # Step 8: Dashboard
        dash_path = update_dashboard(vault_path=args.vault_path, today=today)
        print(f"  Dashboard: {dash_path}")

        # Step 9: Archive
        moved = archive_old_reports(vault_path=args.vault_path)
        if moved:
            print(f"  Archived {moved} old files")

    # Summary
    print(
        f"\n[digest] Done! "
        f"{stats['bedrock_calls']} Bedrock calls | "
        f"${stats['bedrock_cost']:.3f} total cost"
    )


def main() -> None:
    args = parse_args()
    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()

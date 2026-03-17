"""Standalone RSS feed fetcher + deduplicator.

Fetches articles from all configured RSS feeds, deduplicates by title
similarity, and outputs a JSON payload to stdout for consumption by
Claude Code.

Usage:
    python fetch.py [--hours 48] [--vault-path /path/to/vault]

Exit codes:
    0 — success, JSON written to stdout
    1 — error (no articles found, fetch failure, etc.)
    2 — today's digest already exists (idempotency skip)
"""

import argparse
import asyncio
import json
import sys
from datetime import date
from pathlib import Path

# Reuse existing modules unchanged
from digest import VAULT_ROOT
from digest.feeds import RSS_FEEDS
from digest.sources.rss import fetch_all_feeds
from digest.dedup import deduplicate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and dedup RSS articles → JSON")
    parser.add_argument("--hours", type=int, default=48, help="Time window in hours (default: 48)")
    parser.add_argument("--vault-path", default=VAULT_ROOT, help="Obsidian vault path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    today = date.today()
    vault = Path(args.vault_path).expanduser()

    # Idempotency check
    digest_path = vault / "Feeds" / "AI-Daily" / f"{today.isoformat()}.md"
    if digest_path.exists():
        print(f"[fetch] Today's digest already exists: {digest_path}", file=sys.stderr)
        sys.exit(2)

    # Fetch
    print(f"[fetch] Fetching {len(RSS_FEEDS)} RSS feeds (last {args.hours}h)...", file=sys.stderr)
    articles, feeds_ok = asyncio.run(fetch_all_feeds(hours=args.hours))
    print(f"[fetch] Got {len(articles)} articles from {feeds_ok}/{len(RSS_FEEDS)} feeds", file=sys.stderr)

    if not articles:
        print("[fetch] No articles found. Exiting.", file=sys.stderr)
        sys.exit(1)

    # Dedup
    deduped = deduplicate(articles)
    print(f"[fetch] Dedup: {len(articles)} → {len(deduped)} articles", file=sys.stderr)

    # Build JSON output
    payload = {
        "date": today.isoformat(),
        "stats": {
            "sources_total": len(RSS_FEEDS),
            "feeds_ok": feeds_ok,
            "articles_fetched": len(articles),
            "articles_after_dedup": len(deduped),
        },
        "articles": [
            {
                "title": a.title,
                "link": a.link,
                "pub_date": a.pub_date.isoformat(),
                "description": a.description,
                "source_name": a.source_name,
            }
            for a in deduped
        ],
    }

    # JSON to stdout (only data on stdout; logs go to stderr)
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    print(file=sys.stdout)  # trailing newline


if __name__ == "__main__":
    main()

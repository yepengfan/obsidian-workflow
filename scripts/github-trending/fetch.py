"""Standalone GitHub Trending fetcher via GitHub REST Search API.

Fetches trending repos using three complementary queries, deduplicates by
full_name, and outputs a JSON payload to stdout for downstream processing.

Usage:
    python fetch.py [--vault-path /path/to/vault]

Exit codes:
    0 — success, JSON written to stdout
    1 — error (no repos found, API failure, network error)
    2 — today's report already exists (idempotency skip)
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path


GITHUB_API_BASE = "https://api.github.com/search/repositories"
PER_PAGE = 30
PAGES = 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch GitHub trending repos → JSON")
    parser.add_argument("--vault-path", default=".", help="Obsidian vault path")
    return parser.parse_args()


def build_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"token {token}"
        print("[fetch] Using GITHUB_TOKEN for authenticated requests.", file=sys.stderr)
    else:
        print(
            "[fetch] Warning: GITHUB_TOKEN not set. Running unauthenticated "
            "(lower rate limits apply).",
            file=sys.stderr,
        )
    return headers


def fetch_page(query: str, page: int, headers: dict) -> list[dict]:
    """Fetch a single page of search results. Returns list of repo items."""
    params = f"q={urllib.request.quote(query)}&sort=stars&order=desc&per_page={PER_PAGE}&page={page}"
    url = f"{GITHUB_API_BASE}?{params}"
    print(f"[fetch] GET {url}", file=sys.stderr)

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(
            f"[fetch] HTTP {e.code} error fetching page {page}: {error_body}",
            file=sys.stderr,
        )
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[fetch] Network error fetching page {page}: {e.reason}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(body)

    if "message" in data:
        print(f"[fetch] GitHub API error: {data['message']}", file=sys.stderr)
        if "documentation_url" in data:
            print(f"[fetch] See: {data['documentation_url']}", file=sys.stderr)
        sys.exit(1)

    items = data.get("items", [])
    print(f"[fetch] Page {page}: got {len(items)} repos", file=sys.stderr)
    return items


def fetch_query(query: str, headers: dict) -> list[dict]:
    """Fetch all pages for a single query. Returns flat list of repo items."""
    items = []
    for page in range(1, PAGES + 1):
        page_items = fetch_page(query, page, headers)
        items.extend(page_items)
        if len(page_items) < PER_PAGE:
            # No more pages available
            break
    return items


def normalize_repo(item: dict, source: str, today: date) -> dict:
    """Extract relevant fields from a GitHub API repo item."""
    stars = item.get("stargazers_count", 0)
    created_str = item.get("created_at", "")

    # Calculate age and star velocity (stars/day)
    age_days = 1
    if created_str:
        try:
            created_date = datetime.fromisoformat(
                created_str.replace("Z", "+00:00")
            ).date()
            age_days = max((today - created_date).days, 1)
        except (ValueError, TypeError):
            pass

    velocity = round(stars / age_days, 1)

    return {
        "full_name": item.get("full_name", ""),
        "description": item.get("description") or "",
        "language": item.get("language") or "",
        "stars": stars,
        "forks": item.get("forks_count", 0),
        "topics": item.get("topics") or [],
        "created_at": created_str,
        "pushed_at": item.get("pushed_at", ""),
        "url": item.get("html_url", ""),
        "source": source,
        "age_days": age_days,
        "velocity": velocity,
    }


def main() -> None:
    args = parse_args()
    today = date.today()
    vault = Path(args.vault_path).expanduser()

    # Idempotency check
    report_path = vault / "Feeds" / "GitHub-Trending" / f"{today.isoformat()}.md"
    if report_path.exists():
        print(
            f"[fetch] Today's report already exists: {report_path}",
            file=sys.stderr,
        )
        sys.exit(2)

    headers = build_headers()

    # Date windows
    seven_days_ago = (today - timedelta(days=7)).isoformat()
    thirty_days_ago = (today - timedelta(days=30)).isoformat()
    ninety_days_ago = (today - timedelta(days=90)).isoformat()

    # Query 1: brand-new repos (< 7 days) gaining traction
    q1 = f"created:>{seven_days_ago} stars:>20"
    print(f"[fetch] Query 1 (new, <7d): {q1}", file=sys.stderr)
    q1_items = fetch_query(q1, headers)
    print(f"[fetch] Query 1 total: {len(q1_items)} repos", file=sys.stderr)

    # Query 2: rising repos (< 30 days) with solid traction
    q2 = f"created:>{thirty_days_ago} stars:>100"
    print(f"[fetch] Query 2 (rising, <30d): {q2}", file=sys.stderr)
    q2_items = fetch_query(q2, headers)
    print(f"[fetch] Query 2 total: {len(q2_items)} repos", file=sys.stderr)

    # Query 3: breakout repos (< 90 days) that exploded
    q3 = f"created:>{ninety_days_ago} stars:>500"
    print(f"[fetch] Query 3 (breakout, <90d): {q3}", file=sys.stderr)
    q3_items = fetch_query(q3, headers)
    print(f"[fetch] Query 3 total: {len(q3_items)} repos", file=sys.stderr)

    total_fetched = len(q1_items) + len(q2_items) + len(q3_items)
    print(f"[fetch] Total fetched before dedup: {total_fetched}", file=sys.stderr)

    # Merge + dedup: earlier queries take priority for source label
    seen: dict[str, dict] = {}

    for item in q1_items:
        repo = normalize_repo(item, source="new", today=today)
        full_name = repo["full_name"]
        if full_name and full_name not in seen:
            seen[full_name] = repo

    for item in q2_items:
        repo = normalize_repo(item, source="rising", today=today)
        full_name = repo["full_name"]
        if full_name and full_name not in seen:
            seen[full_name] = repo

    for item in q3_items:
        repo = normalize_repo(item, source="breakout", today=today)
        full_name = repo["full_name"]
        if full_name and full_name not in seen:
            seen[full_name] = repo

    print(f"[fetch] After dedup: {len(seen)} repos", file=sys.stderr)

    if not seen:
        print("[fetch] No repos found. Exiting.", file=sys.stderr)
        sys.exit(1)

    # Sort by star velocity (stars/day), take top 30
    repos = sorted(seen.values(), key=lambda r: r["velocity"], reverse=True)[:30]
    if repos:
        print(
            f"[fetch] Top {len(repos)} repos by velocity selected "
            f"(best: {repos[0]['velocity']}⭐/day — {repos[0]['full_name']}).",
            file=sys.stderr,
        )

    # Build output payload
    payload = {
        "date": today.isoformat(),
        "repos": repos,
        "stats": {
            "total_fetched": total_fetched,
            "after_dedup": len(seen),
        },
    }

    # JSON to stdout (all logs go to stderr)
    json.dump(payload, sys.stdout, ensure_ascii=False)
    print(file=sys.stdout)  # trailing newline


if __name__ == "__main__":
    main()

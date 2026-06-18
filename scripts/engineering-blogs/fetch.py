"""Fetch company engineering blog RSS feeds, deduplicate, and output JSON.

Fetches articles from all configured engineering blog RSS feeds, deduplicates
by title similarity, and outputs a JSON payload to stdout.

Usage:
    python fetch.py [--hours 72] [--vault-path /path/to/vault]

Exit codes:
    0 — success, JSON written to stdout
    1 — error (no articles found, fetch failure, etc.)
    2 — today's report already exists (idempotency skip)
"""

import argparse
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timezone, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from xml.etree import ElementTree as ET

from feeds import RSS_FEEDS

TIMEOUT_S = 15
HOURS_DEFAULT = 72  # wider window since company blogs post less frequently

ATOM_NS = "{http://www.w3.org/2005/Atom}"
HTML_TAG_RE = re.compile(r"<[^>]+>")

DATE_FORMATS = [
    "%a, %d %b %Y %H:%M:%S %z",      # RSS 2.0
    "%a, %d %b %Y %H:%M:%S %Z",      # RSS 2.0 with TZ name
    "%Y-%m-%dT%H:%M:%S%z",            # Atom / ISO 8601
    "%Y-%m-%dT%H:%M:%SZ",             # Atom UTC
    "%Y-%m-%d %H:%M:%S%z",
    "%Y-%m-%d",
]



# ── Data model ──────────────────────────────────────────────────────

@dataclass
class Article:
    title: str
    link: str
    pub_date: datetime
    description: str
    source_name: str


# ── Parsing helpers ─────────────────────────────────────────────────

def _parse_date(text: str | None) -> datetime | None:
    if not text:
        return None
    text = text.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def _strip_html(text: str | None) -> str:
    if not text:
        return ""
    return HTML_TAG_RE.sub("", text).strip()


def _parse_feed(xml_bytes: bytes, source_name: str) -> list[Article]:
    """Parse RSS 2.0 or Atom feed XML into Article list."""
    articles = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        print(f"[fetch] {source_name}: XML parse error", file=sys.stderr)
        return []

    # Atom feed
    if root.tag == f"{ATOM_NS}feed" or root.tag == "feed":
        ns = ATOM_NS if root.tag.startswith("{") else ""
        for entry in root.findall(f"{ns}entry"):
            title = (entry.findtext(f"{ns}title") or "").strip()
            link_el = entry.find(f"{ns}link[@rel='alternate']") or entry.find(f"{ns}link")
            link = (link_el.get("href", "") if link_el is not None else "").strip()
            date_text = entry.findtext(f"{ns}published") or entry.findtext(f"{ns}updated")
            pub_date = _parse_date(date_text)
            desc = _strip_html(
                entry.findtext(f"{ns}summary") or entry.findtext(f"{ns}content") or ""
            )
            if title and pub_date:
                articles.append(Article(
                    title=title, link=link, pub_date=pub_date,
                    description=desc[:500], source_name=source_name,
                ))
        return articles

    # RSS 2.0
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = _parse_date(item.findtext("pubDate") or item.findtext("dc:date"))
        desc = _strip_html(item.findtext("description") or "")
        if title and pub_date:
            articles.append(Article(
                title=title, link=link, pub_date=pub_date,
                description=desc[:500], source_name=source_name,
            ))

    return articles


# ── Fetching ────────────────────────────────────────────────────────

def _fetch_via_curl(url: str, name: str) -> bytes | None:
    """Fallback fetcher using curl (handles incomplete TLS cert chains)."""
    curl_bin = shutil.which("curl")
    if not curl_bin:
        return None
    try:
        result = subprocess.run(
            [curl_bin, "-sf", "--max-time", str(TIMEOUT_S),
             "-H", "User-Agent: ObsidianVault/1.0", url],
            capture_output=True, timeout=TIMEOUT_S + 5,
        )
        if result.returncode == 0 and result.stdout:
            print(f"[fetch] {name}: OK (curl fallback)", file=sys.stderr)
            return result.stdout
    except (subprocess.TimeoutExpired, OSError):
        pass
    return None


def fetch_feed(feed: dict, ssl_ctx: ssl.SSLContext) -> list[Article]:
    """Fetch and parse a single RSS feed. Falls back to curl on SSL errors."""
    url = feed["xmlUrl"]
    name = feed["name"]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ObsidianVault/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT_S, context=ssl_ctx) as resp:
            if resp.status != 200:
                print(f"[fetch] {name}: HTTP {resp.status}", file=sys.stderr)
                return []
            data = resp.read()
            return _parse_feed(data, name)
    except urllib.error.URLError as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            print(f"[fetch] {name}: SSL error, trying curl fallback...", file=sys.stderr)
            data = _fetch_via_curl(url, name)
            if data:
                return _parse_feed(data, name)
        print(f"[fetch] {name}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[fetch] {name}: {e}", file=sys.stderr)
        return []


MAX_WORKERS = 16  # concurrent feed fetches (enough for all 27 in ≤2 rounds)
FETCH_WALL_TIMEOUT = 60  # hard wall-clock limit for the entire fetch phase


def fetch_all_feeds(hours: int) -> tuple[list[Article], int]:
    """Fetch all feeds concurrently, filter by time window.

    All feeds launch in parallel. A hard wall-clock timeout ensures we
    finish within FETCH_WALL_TIMEOUT seconds — slow feeds are abandoned
    and we return whatever we collected so far.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    ssl_ctx = ssl.create_default_context()
    all_articles = []
    feeds_ok = 0

    pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    futures = {
        pool.submit(fetch_feed, feed, ssl_ctx): feed["name"]
        for feed in RSS_FEEDS
    }
    try:
        for future in as_completed(futures, timeout=FETCH_WALL_TIMEOUT):
            name = futures[future]
            try:
                articles = future.result()
            except Exception as e:
                print(f"[fetch] {name}: unexpected error: {e}", file=sys.stderr)
                continue
            if articles:
                feeds_ok += 1
            filtered = [a for a in articles if a.pub_date >= cutoff]
            all_articles.extend(filtered)
    except TimeoutError:
        pending = [name for f, name in futures.items() if not f.done()]
        print(
            f"[fetch] Wall-clock timeout ({FETCH_WALL_TIMEOUT}s), "
            f"skipping {len(pending)} slow feeds: {', '.join(pending)}",
            file=sys.stderr,
        )
    finally:
        pool.shutdown(wait=False, cancel_futures=True)

    all_articles.sort(key=lambda a: a.pub_date, reverse=True)
    return all_articles, feeds_ok


# ── Deduplication ───────────────────────────────────────────────────

def deduplicate(articles: list[Article], threshold: float = 0.85) -> list[Article]:
    """Remove near-duplicate articles by title similarity."""
    seen: list[str] = []
    result: list[Article] = []
    for a in articles:
        title_lower = a.title.lower().strip()
        is_dup = False
        for s in seen:
            if SequenceMatcher(None, title_lower, s).ratio() > threshold:
                is_dup = True
                break
        if not is_dup:
            seen.append(title_lower)
            result.append(a)
    return result


# ── Main ────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch engineering blog articles → JSON")
    parser.add_argument("--hours", type=int, default=HOURS_DEFAULT, help=f"Time window in hours (default: {HOURS_DEFAULT})")
    parser.add_argument("--vault-path", default=".", help="Obsidian vault path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    today = date.today()
    vault = Path(args.vault_path).expanduser()

    # Idempotency check
    report_path = vault / "Feeds" / "Engineering-Blogs" / f"{today.isoformat()}.md"
    if report_path.exists():
        print(f"[fetch] Today's report already exists: {report_path}", file=sys.stderr)
        sys.exit(2)

    # Fetch
    print(f"[fetch] Fetching {len(RSS_FEEDS)} engineering blog feeds (last {args.hours}h)...", file=sys.stderr)
    articles, feeds_ok = fetch_all_feeds(args.hours)
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

    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    print(file=sys.stdout)
    sys.stdout.flush()

    # Force-exit to avoid blocking on abandoned slow-feed threads.
    # All output is already flushed; clean shutdown is not needed here.
    os._exit(0)


if __name__ == "__main__":
    main()

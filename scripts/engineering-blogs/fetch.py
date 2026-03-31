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
import re
import shutil
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timezone, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from xml.etree import ElementTree as ET

from feeds import RSS_FEEDS

CONCURRENCY_NOTE = "Sequential fetching (stdlib only, no aiohttp dependency)"
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

HISTORY_PATH = Path(__file__).parent / "history.json"
DECAY_WINDOW_DAYS = 7


# ── Data model ──────────────────────────────────────────────────────

@dataclass
class Article:
    title: str
    link: str
    pub_date: datetime
    description: str
    source_name: str


# ── History management ──────────────────────────────────────────────

def load_history() -> dict:
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            print("[fetch] Warning: history.json corrupted, starting fresh.", file=sys.stderr)
    return {"featured": {}}


def save_history(history: dict, selected: list, today: date) -> None:
    featured = history.get("featured", {})
    featured[today.isoformat()] = [a.get("link", "") for a in selected if a.get("link")]

    cutoff = (today - timedelta(days=14)).isoformat()
    featured = {d: links for d, links in featured.items() if d >= cutoff}

    history = {"featured": featured}
    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2))
    print(f"[fetch] History saved ({len(featured)} days).", file=sys.stderr)


def count_appearances(link: str, featured: dict, today: date) -> int:
    cutoff = (today - timedelta(days=DECAY_WINDOW_DAYS)).isoformat()
    count = 0
    for date_str, links in featured.items():
        if date_str >= cutoff and link in links:
            count += 1
    return count


def get_decay(appearances: int) -> float:
    if appearances == 0:
        return 1.0
    if appearances == 1:
        return 0.3
    return 0.1


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


def fetch_feed(feed: dict) -> list[Article]:
    """Fetch and parse a single RSS feed. Falls back to curl on SSL errors."""
    url = feed["xmlUrl"]
    name = feed["name"]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ObsidianVault/1.0"})
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=TIMEOUT_S, context=ctx) as resp:
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


def fetch_all_feeds(hours: int) -> tuple[list[Article], int]:
    """Fetch all feeds sequentially, filter by time window."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    all_articles = []
    feeds_ok = 0

    for feed in RSS_FEEDS:
        articles = fetch_feed(feed)
        if articles:
            feeds_ok += 1
        filtered = [a for a in articles if a.pub_date >= cutoff]
        all_articles.extend(filtered)

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


if __name__ == "__main__":
    main()

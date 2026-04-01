#!/usr/bin/env python3
"""Step 0: RSS feed fetcher + audio downloader.

Reads Podcasts/Feeds.md (Obsidian-native markdown config), parses each RSS
feed with feedparser, filters out already-processed episodes via state.json,
downloads new audio files to Podcasts/audio/, and writes a JSON payload to
stdout for transcribe.py.

Input:  Podcasts/Feeds.md          (markdown with [Name](RSS_URL) links)
        scripts/podcast/state.json (processed GUIDs, keyed by guid)
Output: stdout JSON  {"episodes": [...], "stats": {...}}

Each episode object:
    title, podcast_name, date, duration, description, guid,
    audio_url, audio_path, slug

Does NOT update state.json — that is write_notes.py's responsibility.

Usage:
    python fetch.py [--vault-path /path/to/vault]
"""

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

import feedparser

SCRIPT_DIR = Path(__file__).parent
DEFAULT_VAULT = SCRIPT_DIR.parent.parent  # two dirs up from script


# ── CLI args ─────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch RSS podcast feeds + download audio → JSON")
    parser.add_argument(
        "--vault-path",
        default=str(DEFAULT_VAULT),
        help="Obsidian vault root (default: two dirs up from script)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max new episodes per feed (0 = unlimited, default: 0)",
    )
    return parser.parse_args()


# ── Feeds.md parser ──────────────────────────────────────────────────

def load_feeds(feeds_md_path: Path) -> list[tuple[str, str]]:
    """Parse Podcasts/Feeds.md for markdown links. Returns [(url, name), ...].

    Supported format (standard markdown links in a bullet list):
        - [Podcast Name](https://example.com/feed.xml)

    Lines inside HTML comments (<!-- ... -->) are skipped.
    Lines without a markdown link are ignored.
    """
    text = feeds_md_path.read_text(encoding="utf-8")

    # Strip HTML comment blocks (<!-- ... -->), including multiline
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # Extract markdown links: [name](url)
    feeds = []
    for match in re.finditer(r"\[([^\]]+)\]\((https?://[^)]+)\)", text):
        name = match.group(1).strip()
        url = match.group(2).strip()
        # Auto-resolve Apple Podcasts URLs to RSS feeds
        if "podcasts.apple.com" in url:
            resolved = _resolve_apple_podcast(url)
            if resolved:
                url = resolved
            else:
                print(f"[fetch] WARNING: Could not resolve Apple Podcasts URL: {url}", file=sys.stderr)
                continue
        feeds.append((url, name))
    return feeds


def _resolve_apple_podcast(apple_url: str) -> str | None:
    """Convert an Apple Podcasts URL to its RSS feed URL via iTunes Lookup API."""
    id_match = re.search(r"id(\d+)", apple_url)
    if not id_match:
        return None
    apple_id = id_match.group(1)
    lookup_url = f"https://itunes.apple.com/lookup?id={apple_id}&entity=podcast"
    try:
        req = urllib.request.Request(lookup_url, headers={"User-Agent": "Mozilla/5.0 (podcast-pipeline/1.0)"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        if data.get("resultCount", 0) > 0:
            feed_url = data["results"][0].get("feedUrl", "")
            if feed_url:
                print(f"[fetch] Resolved Apple Podcasts id{apple_id} → {feed_url}", file=sys.stderr)
                return feed_url
    except Exception as exc:
        print(f"[fetch] WARNING: iTunes lookup failed for id{apple_id}: {exc}", file=sys.stderr)
    return None


def load_feeds_txt(feeds_path: Path) -> list[tuple[str, str]]:
    """Fallback: load from feeds.txt if Feeds.md doesn't exist."""
    urls = []
    for raw_line in feeds_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#")[0].strip()
        if line:
            urls.append((line, ""))
    return urls


# ── state.json helpers ────────────────────────────────────────────────

def load_state(state_path: Path) -> set[str]:
    """Return set of already-processed GUIDs."""
    if not state_path.exists():
        return set()
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        return set(data.get("processed", {}).keys())
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[fetch] Warning: could not read state.json — {exc}", file=sys.stderr)
        return set()


# ── slug generation ───────────────────────────────────────────────────

def make_slug(podcast_name: str, episode_title: str, max_len: int = 60) -> str:
    """Combine podcast name + episode title into a URL-safe slug (max 60 chars)."""
    combined = f"{podcast_name} {episode_title}"
    slug = combined.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)   # non-alphanumeric → hyphens
    slug = re.sub(r"-{2,}", "-", slug)          # collapse multiple hyphens
    slug = slug.strip("-")                      # strip leading/trailing hyphens
    return slug[:max_len].rstrip("-")           # truncate and clean trailing dash


# ── metadata extraction ───────────────────────────────────────────────

def _extract_duration(entry: feedparser.FeedParserDict) -> str:
    """Try itunes:duration first, fall back to enclosure length, or empty string."""
    # feedparser maps itunes:duration to itunes_duration
    itunes_dur = getattr(entry, "itunes_duration", None) or entry.get("itunes_duration", "")
    if itunes_dur:
        return str(itunes_dur).strip()
    # Try enclosure length as fallback (bytes — not ideal but better than nothing)
    for enc in getattr(entry, "enclosures", []):
        if enc.get("length"):
            return str(enc["length"])
    return ""


def _extract_enclosure(entry: feedparser.FeedParserDict) -> tuple[str, str]:
    """Return (audio_url, mime_type) from the first audio enclosure, or ('', '')."""
    for enc in getattr(entry, "enclosures", []):
        mime = enc.get("type", "")
        href = enc.get("href", "") or enc.get("url", "")
        if href and ("audio" in mime or href.lower().endswith((".mp3", ".m4a", ".ogg"))):
            return href, mime
    return "", ""


def _extract_guid(entry: feedparser.FeedParserDict) -> str:
    """Return a stable GUID for the entry."""
    # feedparser puts guid / id in entry.id
    guid = entry.get("id", "") or entry.get("guid", "")
    if not guid:
        # Fall back to link
        guid = entry.get("link", "")
    return str(guid).strip()


def _extract_description(entry: feedparser.FeedParserDict) -> str:
    """Return plain-ish description (prefer summary, fall back to content)."""
    summary = entry.get("summary", "")
    if summary:
        return summary
    content_list = entry.get("content", [])
    if content_list:
        return content_list[0].get("value", "")
    return ""


def _extract_date(entry: feedparser.FeedParserDict) -> str:
    """Return ISO-format publish date string, or empty string."""
    published = entry.get("published", "") or entry.get("updated", "")
    if not published:
        # feedparser also provides structured time
        pt = entry.get("published_parsed") or entry.get("updated_parsed")
        if pt:
            import time
            published = time.strftime("%Y-%m-%d", pt)
    # Try to normalise to YYYY-MM-DD
    if published:
        # feedparser RFC-2822 → "Mon, 01 Jan 2024 00:00:00 +0000"
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(published)
            return dt.date().isoformat()
        except Exception:
            pass
        # Already ISO-ish?
        m = re.match(r"(\d{4}-\d{2}-\d{2})", published)
        if m:
            return m.group(1)
    return ""


# ── audio download ────────────────────────────────────────────────────

def download_audio(audio_url: str, dest: Path) -> bool:
    """Download audio file to dest. Returns True on success, False on failure."""
    if dest.exists():
        print(f"[fetch] Already exists, skipping: {dest.name}", file=sys.stderr)
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"[fetch] Downloading: {dest.name}...", file=sys.stderr)
    try:
        req = urllib.request.Request(
            audio_url,
            headers={"User-Agent": "Mozilla/5.0 (podcast-pipeline/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as fh:
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                fh.write(chunk)
        return True
    except Exception as exc:
        print(f"[fetch] ERROR downloading {dest.name}: {exc}", file=sys.stderr)
        # Remove partial file if it exists
        if dest.exists():
            dest.unlink()
        return False


# ── feed parsing ──────────────────────────────────────────────────────

def parse_feed(url: str, processed_guids: set[str], audio_dir: Path, limit: int = 0) -> tuple[list[dict], bool]:
    """Parse one RSS feed. Returns (new_episodes, success_bool).

    Args:
        limit: Max new episodes to fetch from this feed (0 = unlimited).
               RSS feeds are naturally sorted newest-first, so limit=5 gets the 5 most recent.
    """
    try:
        feed = feedparser.parse(url)
    except Exception as exc:
        print(f"[fetch] ERROR parsing feed {url}: {exc}", file=sys.stderr)
        return [], False

    # feedparser swallows most errors but sets bozo=True
    if feed.bozo and not feed.entries:
        exc = getattr(feed, "bozo_exception", "unknown error")
        print(f"[fetch] ERROR (bozo) for {url}: {exc}", file=sys.stderr)
        return [], False

    podcast_name = feed.feed.get("title", "Unknown Podcast").strip()
    new_episodes: list[dict] = []

    for entry in feed.entries:
        guid = _extract_guid(entry)
        if not guid:
            continue  # can't track without a guid
        if guid in processed_guids:
            continue  # already processed

        audio_url, _ = _extract_enclosure(entry)
        if not audio_url:
            continue  # no audio attachment, skip

        title = entry.get("title", "Untitled").strip()
        slug = make_slug(podcast_name, title)
        audio_path = audio_dir / f"{slug}.mp3"

        downloaded = download_audio(audio_url, audio_path)
        if not downloaded:
            continue  # skip episodes whose audio couldn't be fetched

        new_episodes.append({
            "title": title,
            "podcast_name": podcast_name,
            "date": _extract_date(entry),
            "duration": _extract_duration(entry),
            "description": _extract_description(entry),
            "guid": guid,
            "audio_url": audio_url,
            "audio_path": str(audio_path),
            "slug": slug,
        })

        # Respect per-feed limit
        if limit > 0 and len(new_episodes) >= limit:
            break

    return new_episodes, True


# ── main ──────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()
    vault = Path(args.vault_path).expanduser().resolve()

    feeds_md_path = vault / "Podcasts" / "Feeds.md"
    feeds_txt_path = SCRIPT_DIR / "feeds.txt"
    state_path = SCRIPT_DIR / "state.json"
    audio_dir = vault / "Podcasts" / "audio"

    # Load feeds: prefer Feeds.md (Obsidian-native), fallback to feeds.txt
    if feeds_md_path.exists():
        feed_entries = load_feeds(feeds_md_path)
        print(f"[fetch] Loaded {len(feed_entries)} feeds from Podcasts/Feeds.md", file=sys.stderr)
    elif feeds_txt_path.exists():
        feed_entries = load_feeds_txt(feeds_txt_path)
        print(f"[fetch] Loaded {len(feed_entries)} feeds from feeds.txt (fallback)", file=sys.stderr)
    else:
        print("[fetch] ERROR: No feed config found. Create Podcasts/Feeds.md or scripts/podcast/feeds.txt", file=sys.stderr)
        sys.exit(1)

    if not feed_entries:
        print("[fetch] No active feeds configured.", file=sys.stderr)
        json.dump({"episodes": [], "stats": {"feeds_total": 0, "feeds_ok": 0, "new_episodes": 0, "downloaded": 0}}, sys.stdout)
        return

    processed_guids = load_state(state_path)

    limit = args.limit
    if limit > 0:
        print(f"[fetch] Fetching {len(feed_entries)} feeds (limit: {limit} episodes per feed)...", file=sys.stderr)
    else:
        print(f"[fetch] Fetching {len(feed_entries)} feeds...", file=sys.stderr)

    all_episodes: list[dict] = []
    feeds_ok = 0
    downloaded = 0

    for url, _name in feed_entries:
        episodes, ok = parse_feed(url, processed_guids, audio_dir, limit=limit)
        if ok:
            feeds_ok += 1
        all_episodes.extend(episodes)
        downloaded += len(episodes)

    print(
        f"[fetch] Done: {feeds_ok}/{len(feed_entries)} feeds OK, "
        f"{downloaded} new episodes downloaded.",
        file=sys.stderr,
    )

    result = {
        "episodes": all_episodes,
        "stats": {
            "feeds_total": len(feed_entries),
            "feeds_ok": feeds_ok,
            "new_episodes": len(all_episodes),
            "downloaded": downloaded,
        },
    }
    json.dump(result, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()

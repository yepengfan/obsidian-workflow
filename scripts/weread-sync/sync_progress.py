#!/usr/bin/env python3
"""
Sync WeRead reading progress from API to vault frontmatter.

The WeRead Obsidian plugin only updates frontmatter when new highlights are
synced. This script fills the gap by fetching current progress from the
WeRead API and patching the frontmatter `progress` field directly.

Usage:
    python3 scripts/weread-sync/sync_progress.py          # dry-run (default)
    python3 scripts/weread-sync/sync_progress.py --apply   # apply changes
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent.parent
PLUGIN_DATA = VAULT / ".obsidian/plugins/obsidian-weread-plugin/data.json"
WEREAD_DIR = VAULT / "WeRead"
API_BASE = "https://weread.qq.com/web/book/getProgress"

# readingStatus codes: 2 = 在读, 4 = 读完
READING_STATUSES = {"2", "在读"}


def load_cookies() -> str:
    config = json.loads(PLUGIN_DATA.read_text("utf-8"))
    return "; ".join(f"{c['name']}={c['value']}" for c in config["cookies"])


def find_reading_books() -> list[dict]:
    books = []
    for md in WEREAD_DIR.rglob("*.md"):
        text = md.read_text("utf-8")
        fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not fm_match:
            continue
        fm = fm_match.group(1)

        doc_type = _field(fm, "doc_type")
        if doc_type != "weread-highlights-reviews":
            continue

        status = _field(fm, "readingStatus")
        if status not in READING_STATUSES:
            continue

        book_id = _field(fm, "bookId")
        title = _field(fm, "title")
        old_prog = _field(fm, "progress")

        if book_id:
            books.append(dict(file=md, book_id=book_id, title=title, old_prog=old_prog))
    return books


def fetch_progress(book_id: str, cookie_str: str) -> int | None:
    url = f"{API_BASE}?bookId={book_id}"
    req = urllib.request.Request(url, headers={"Cookie": cookie_str, "User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("book", {}).get("progress")
    except Exception:
        return None


def update_frontmatter(file: Path, new_prog: int) -> bool:
    """Replace the progress field only within the YAML frontmatter block."""
    text = file.read_text("utf-8")
    fm_match = re.match(r"^(---\n)(.*?)(\n---)", text, re.DOTALL)
    if not fm_match:
        return False

    prefix, fm, suffix = fm_match.group(1), fm_match.group(2), fm_match.group(3)
    new_fm, count = re.subn(
        r"^progress:.*$", f"progress: {new_prog}%", fm, count=1, flags=re.MULTILINE
    )
    if count == 0:
        return False

    text = prefix + new_fm + suffix + text[fm_match.end() :]
    file.write_text(text, "utf-8")
    return True


def _field(fm: str, key: str) -> str | None:
    # key is always a hardcoded safe literal — no regex injection risk
    m = re.search(rf'^{key}:\s*["\']?([^"\'\n]*)["\']?', fm, re.MULTILINE)
    return m.group(1).strip() if m else None


def main():
    apply = "--apply" in sys.argv

    cookie_str = load_cookies()
    books = find_reading_books()
    print(f"Found {len(books)} books with 在读 status\n")

    updated = 0
    stale = 0
    for book in books:
        api_prog = fetch_progress(book["book_id"], cookie_str)
        title = (book["title"] or book["file"].stem)[:35]
        old = book["old_prog"] or "?"

        if api_prog is None:
            print(f"  ⚠️  {title}: API returned no data")
            continue

        new = f"{api_prog}%"
        if old == new:
            print(f"  ✅ {title}: {old} (up to date)")
            continue

        if apply:
            ok = update_frontmatter(book["file"], api_prog)
            status = "updated" if ok else "FAILED"
            print(f"  🔄 {title}: {old} → {new} ({status})")
            if ok:
                updated += 1
        else:
            print(f"  ❌ {title}: {old} → {new} (dry-run)")
            stale += 1

    print(f"\n{'Updated' if apply else 'Would update'}: {updated if apply else stale}/{len(books)} books")
    if not apply and stale > 0:
        print("Run with --apply to write changes.")


if __name__ == "__main__":
    main()

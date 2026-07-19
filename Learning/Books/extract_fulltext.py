#!/usr/bin/env python3
"""
extract_fulltext.py — Full-text cache extractor for the Book Learning System

Usage:
    "Learning/Books/.venv/bin/python3" Learning/Books/extract_fulltext.py \
        --book "Learning/Books/{BookTitle}"

Reads epub_path/pdf_path from {BookTitle}/meta.md frontmatter, extracts the
FULL chapter text (book_init.py only extracts a short preview for the chapter
skeleton), and writes one text file per chapter to {BookTitle}/.fulltext_cache/,
using the exact same filename stems as {BookTitle}/chapters/ so the two stay
easy to cross-reference.

This is Layer 1 of a two-layer system (see Learning/Books/CLAUDE.md →
"Full-text cache"):
  Layer 1 (this script's output)   — persistent, on-disk, per-book text cache.
  Layer 2 (AI's session search index) — ephemeral, rebuilt from Layer 1 each
           session, never written to disk.

`.fulltext_cache/` is already covered by the existing `/Learning/Books/*`
.gitignore rule — no new ignore rules are needed.

Dependencies: same as book_init.py (ebooklib, beautifulsoup4, pdfplumber)
"""

import argparse
import hashlib
import html
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import book_init  # reuse parse_epub's TOC/chapter-matching logic


def _yaml_unescape(s: str) -> str:
    """Reverse book_init.py's _yaml_escape() (which does '\\' -> '\\\\' then
    '"' -> '\\"'). A single left-to-right pass — not two sequential
    .replace() calls — so a literal backslash sitting right next to an
    escaped quote doesn't get double-unescaped incorrectly. (Every backslash
    in an escaped string is always part of an escape pair, since
    _yaml_escape doubles ALL backslashes before it escapes quotes — so
    "consume a backslash and whatever follows it" is a safe, exact inverse.)
    """
    return re.sub(r'\\(.)', lambda m: m.group(1), s)


def read_frontmatter(meta_path: Path) -> dict:
    """Minimal YAML frontmatter reader — good enough for this file's flat,
    single-line string/scalar fields (title/author/epub_path/pdf_path/...).
    Does not attempt to parse nested structures like `progress:`."""
    text = meta_path.read_text(encoding='utf-8')
    m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        kv = re.match(r'^(\w+):\s*(.*)$', line)
        if not kv:
            continue
        key, val = kv.group(1), kv.group(2).strip()
        if val.startswith('"') and val.endswith('"'):
            val = _yaml_unescape(val[1:-1])
        fm[key] = val
    return fm


def get_chapter_stems(chapters_dir: Path) -> list:
    """Chapter filename stems (no extension), in ChNN order — matches the
    exact order/numbering book_init.py originally wrote them in (zero-padded
    ChNN sorts correctly as plain strings)."""
    stems = [f.stem for f in chapters_dir.glob("Ch*.md")]
    stems.sort()
    return stems


def verify_chapter_alignment(chapter_items: list, chapter_stems: list) -> list:
    """Verify chapter_items (freshly re-parsed from the EPUB's TOC) line up
    1:1, title-for-title, with chapter_stems (existing chapters/*.md
    filenames) — using the exact same title -> filename convention
    book_init.py used when it originally created them (see its
    write_chapter()).

    A plain positional zip() can't catch a silent misalignment (e.g.
    chapters/ manually renamed/reordered, or a change in how parse_epub()
    classifies front/back matter between runs) — this catches it before any
    text is written, since a misattributed chapter would defeat the whole
    point of grounding answers in what the book actually says.

    Returns a list of (chapter_number, expected_stem, actual_stem) for every
    chapter that doesn't line up. Empty list means everything matches.
    """
    mismatches = []
    for i, (ch_title, _href, _preview) in enumerate(chapter_items):
        clean_title = re.sub(r'^\d+[\.\s]+', '', ch_title).strip()
        expected = f"Ch{i + 1:02d}_{book_init.safe_filename(clean_title)}"
        actual = chapter_stems[i] if i < len(chapter_stems) else None
        if expected != actual:
            mismatches.append((i + 1, expected, actual))
    return mismatches


def file_sha256(path: str, chunk_size: int = 1 << 20) -> str:
    """Content hash of the source ebook file. Used — instead of size/mtime
    alone — as the staleness signal: source files sync in from S3 via a
    launchd job (see .bookrc.example), and a same-content re-sync can still
    touch mtime without the book's actual content changing, which would
    otherwise trigger a spurious "rebuild needed" prompt."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)
    return h.hexdigest()


class _BlockTextExtractor:
    """Extracts text with real blank-line paragraph breaks, so downstream
    tools that chunk on blank lines (e.g. the search index) get sensible
    per-paragraph/per-heading sections instead of one giant blob.

    Deliberately NOT BeautifulSoup.get_text(separator=' ') — that inserts a
    space between *every* text node, including around manually-appended '\n'
    markers, which turns paragraph breaks into ' \n ' (space-newline-space)
    instead of a real blank line ('\n\n'). HTMLParser concatenates parts
    directly with no inserted separator, so consecutive block-tag boundaries
    correctly produce '\n\n'.
    """

    class _Parser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts = []
            self.skip = False

        def handle_starttag(self, tag, attrs):
            if tag in ("script", "style"):
                self.skip = True
            if tag in ("p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6"):
                self.parts.append("\n")

        def handle_endtag(self, tag):
            if tag in ("script", "style"):
                self.skip = False
            if tag in ("p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6"):
                self.parts.append("\n")

        def handle_data(self, data):
            if not self.skip:
                self.parts.append(data)

    @classmethod
    def extract(cls, raw_html: str) -> str:
        parser = cls._Parser()
        parser.feed(raw_html)
        text = "".join(parser.parts)
        text = html.unescape(text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


def full_text_from_epub_item(items_by_name: dict, href: str) -> str:
    """items_by_name: {epub item name -> EpubItem}, built once per book by
    the caller (not per-chapter — building it fresh for every chapter would
    mean rebuilding the same dict N times for an N-chapter book)."""
    item = items_by_name.get(href.split('#')[0])
    if not item:
        return ""
    raw = item.get_content()
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8', errors='replace')
    return _BlockTextExtractor.extract(raw)


def main():
    ap = argparse.ArgumentParser(description="Extract full chapter text cache for a book.")
    ap.add_argument('--book', required=True, help='Path to Learning/Books/{BookTitle}')
    ap.add_argument('--force', action='store_true', help='Rebuild even if cache looks current')
    args = ap.parse_args()

    book_dir = Path(args.book)
    meta_path = book_dir / 'meta.md'
    chapters_dir = book_dir / 'chapters'
    cache_dir = book_dir / '.fulltext_cache'
    manifest_path = cache_dir / '_manifest.json'

    if not meta_path.exists():
        sys.exit(f"❌  {meta_path} not found")
    if not chapters_dir.exists():
        sys.exit(f"❌  {chapters_dir} not found — run book_init.py first")

    fm = read_frontmatter(meta_path)
    source_path = fm.get('epub_path') or fm.get('pdf_path')
    if not source_path:
        sys.exit("❌  meta.md has no epub_path/pdf_path — nothing to extract "
                  "(WeRead-only book?)")
    source_path = os.path.expanduser(source_path)
    if not os.path.exists(source_path):
        sys.exit(f"❌  Source file not found on disk: {source_path}")

    ext = Path(source_path).suffix.lower()
    st = os.stat(source_path)
    print("🔍  Hashing source file to check staleness...")
    new_manifest = {
        'source_path': source_path,
        'source_size': st.st_size,      # informational only — see file_sha256()
        'source_mtime': st.st_mtime,    # informational only — see file_sha256()
        'source_sha256': file_sha256(source_path),
    }

    if manifest_path.exists() and not args.force:
        old = json.loads(manifest_path.read_text(encoding='utf-8'))
        # Compare by content hash, not size/mtime: mtime can change on a
        # same-content S3 re-sync without the book's actual content changing.
        if old.get('source_sha256') == new_manifest['source_sha256']:
            print(f"✅  Cache up to date: {cache_dir} (use --force to rebuild anyway)")
            return

    chapter_stems = get_chapter_stems(chapters_dir)

    if ext == '.epub':
        # parse_epub() first: it wraps ebooklib/bs4 imports in a friendly
        # "pip install ..." message on ImportError (see book_init.py). Doing
        # our own `from ebooklib import epub` before this would bypass that
        # guard and surface a raw ModuleNotFoundError traceback instead.
        title, author, parts, chapter_items = book_init.parse_epub(source_path)
        import ebooklib
        from ebooklib import epub

        if len(chapter_items) != len(chapter_stems):
            sys.exit(
                f"❌  Chapter count mismatch: EPUB TOC parse found {len(chapter_items)} "
                f"chapters, chapters/ has {len(chapter_stems)}. Refusing to guess pairing — "
                f"investigate before retrying (did chapters/ get manually edited, or did "
                f"book_init.py's chapter-detection change?)."
            )

        mismatches = verify_chapter_alignment(chapter_items, chapter_stems)
        if mismatches:
            detail = "\n".join(
                f"  #{i}: expected '{expected}', chapters/ actually has '{actual}'"
                for i, expected, actual in mismatches
            )
            sys.exit(
                "❌  Chapter alignment check failed — refusing to write a cache that could "
                "silently attribute one chapter's text to a different chapter's file:\n"
                f"{detail}\n"
                "This usually means chapters/ was manually renamed/reordered, or a re-run "
                "of book_init.py's chapter-detection produced a different result than when "
                "chapters/ was first generated. Investigate before retrying."
            )

        book = epub.read_epub(source_path)
        items_by_name = {
            item.get_name(): item
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        }
        cache_dir.mkdir(exist_ok=True)
        written = 0
        for (ch_title, href, _preview), stem in zip(chapter_items, chapter_stems):
            text = full_text_from_epub_item(items_by_name, href)
            (cache_dir / f"{stem}.txt").write_text(text, encoding='utf-8')
            written += 1
        print(f"✅  {written}/{len(chapter_stems)} chapter text files written to {cache_dir}")
    elif ext == '.pdf':
        sys.exit("❌  PDF full-text extraction isn't implemented yet — book_init.py's PDF "
                  "chapter detection is page-heuristic and not reliable enough to map back "
                  "to chapters/ automatically. Use EPUB if available.")
    else:
        sys.exit(f"❌  Unsupported source extension: {ext}")

    manifest_path.write_text(json.dumps(new_manifest, indent=2), encoding='utf-8')
    print(f"✅  Manifest written: {manifest_path}")


if __name__ == '__main__':
    main()

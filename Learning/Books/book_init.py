#!/usr/bin/env python3
"""
book_init.py — Book Learning System Initializer
Usage:
    python3 book_init.py --file "/path/to/book.epub" --output "/path/to/Notes/Books"

Generates a ready-to-use Obsidian note structure for deep reading:
    {output}/{Book Title}/
    ├── meta.md         (frontmatter includes epub_path/pdf_path -> resolved
    │                    absolute path of the --file source, keyed by its
    │                    format, so the note always knows where its source
    │                    ebook lives on disk)
    ├── MOC.md
    ├── chapters/
    │   ├── Ch01_{title}.md
    │   └── ...
    ├── notes/
    └── understanding.md   (per-chapter capture record: AI map + your understanding)

Dependencies:
    pip install ebooklib beautifulsoup4 pdfplumber
"""

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path

# This script always lives at "{vault}/Learning/Books/book_init.py", regardless of
# how the caller's --output argument is spelled (relative, absolute, differently
# depthed) — so derive the vault root from the script's own location rather than
# from --output. (--output's parent was previously assumed to *be* the vault root,
# which broke find_weread/find_ibooks/cover-path resolution whenever --output was
# anything other than exactly "{vault}/Books".)
VAULT_ROOT = Path(__file__).resolve().parent.parent.parent


# ── Helpers ───────────────────────────────────────────────────────────────────

def safe_filename(title: str) -> str:
    """Strip characters that are problematic in filenames."""
    return re.sub(r'[^\w\u4e00-\u9fff \-]', '', title).strip()


def clean_preview(text: str, n_words: int = 60, n_chars_cjk: int = 120) -> str:
    """
    Extract a clean preview from raw chapter text.
    Strips footnote noise and leading title repetition.
    Uses character count for CJK text, word count for Latin text.
    """
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Drop leading chapter-heading pattern (Chinese: "第 3 章 ...")
    text = re.sub(r'^第\s*\d+\s*章\s*[\w\s，、。？！]*?(?=\S{4})', '', text).strip()
    # Drop leading "Chapter N." or "Chapter N: " prefix (English)
    text = re.sub(r'^Chapter\s+\d+[\.\:]\s*', '', text, flags=re.I).strip()
    # CJK text: use character limit (words aren't space-separated)
    if re.search(r'[\u4e00-\u9fff]', text):
        return text[:n_chars_cjk]
    words = text.split()
    return ' '.join(words[:n_words])


# ── WeRead integration ────────────────────────────────────────────────────────

def find_weread(vault_dir: Path, book_title: str):
    """
    Find matching WeRead file and extract chapter headings.
    Returns (weread_filename_stem, set_of_chapter_headings) or (None, set()).
    """
    weread_dir = vault_dir / "WeRead"
    if not weread_dir.exists():
        return None, set()

    # Try exact match first, then fuzzy
    candidates = [f for f in weread_dir.iterdir() if f.is_dir()]
    # Sort: exact match first, then by longest name (more specific = better)
    candidates.sort(key=lambda f: (f.name != book_title, -len(f.name)))
    for folder in candidates:
        if book_title in folder.name or folder.name in book_title:
            md_files = list(folder.glob("*.md"))
            if not md_files:
                continue
            weread_file = md_files[0]
            weread_name = weread_file.stem

            # Extract chapter headings from the WeRead file
            content = weread_file.read_text(encoding='utf-8')
            headings = set()
            for m in re.finditer(r'^#{2,4}\s+(.+)$', content, re.MULTILINE):
                headings.add(m.group(1).strip())
            return weread_name, headings

    return None, set()


def match_weread_heading(chapter_title: str, weread_headings: set) -> str | None:
    """Find a matching WeRead heading for a chapter title."""
    # Exact match
    if chapter_title in weread_headings:
        return chapter_title
    # Try without leading number (e.g. "1. Introduction" -> "Introduction")
    clean = re.sub(r'^\d+[\.\s]+', '', chapter_title).strip()
    if clean in weread_headings:
        return clean
    # Fuzzy: check if any heading contains the chapter title or vice versa
    for h in weread_headings:
        if chapter_title in h or h in chapter_title:
            return h
    return None


# ── iBooks integration ────────────────────────────────────────────────────────

def find_ibooks(vault_dir: Path, book_title: str) -> str | None:
    """
    Find a matching Apple Books highlights export in ibooks-highlights/.
    Unlike WeRead's per-book folder, this plugin exports one flat .md file per
    book (no per-chapter headings), so there's nothing to link chapters
    against — this only returns the vault-relative path for meta.md's
    `ibooks_source` field.
    """
    ibooks_dir = vault_dir / "ibooks-highlights"
    if not ibooks_dir.exists():
        return None

    candidates = list(ibooks_dir.glob("*.md"))
    candidates.sort(key=lambda f: (f.stem != book_title, -len(f.stem)))
    for f in candidates:
        if book_title in f.stem or f.stem in book_title:
            return f"ibooks-highlights/{f.name}"
    return None


# ── EPUB parsing ──────────────────────────────────────────────────────────────

def parse_epub(filepath: str):
    """
    Returns:
        title (str), author (str),
        parts (dict[part_title -> list[chapter_title]]),
        chapter_items (list[(chapter_title, href)])
    """
    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup
    except ImportError:
        print("❌  Missing dependencies. Run: pip install ebooklib beautifulsoup4")
        sys.exit(1)

    book = epub.read_epub(filepath)

    # Metadata
    title_meta = book.get_metadata('DC', 'title')
    author_meta = book.get_metadata('DC', 'creator')
    title = title_meta[0][0] if title_meta else Path(filepath).stem
    author = author_meta[0][0] if author_meta else "Unknown"

    # Build item lookup
    items_by_name = {
        item.get_name(): item
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
    }

    def get_preview(href: str) -> str:
        name = href.split('#')[0]
        item = items_by_name.get(name)
        if not item:
            return ""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(item.get_content(), 'html.parser')
        for tag in soup.find_all(['sup', 'aside']):
            tag.decompose()
        return clean_preview(soup.get_text(separator=' ', strip=True))

    # Return the (title, href) of each direct child of a TOC list — no recursion.
    def top_level_entries(toc):
        entries = []
        for item in toc:
            if isinstance(item, epub.Link):
                entries.append((item.title, item.href))
            elif isinstance(item, tuple):
                section, _children = item
                entries.append((section.title, section.href))
        return entries

    # Flatten TOC (recursive)
    def flatten_toc(toc):
        result = []
        for item in toc:
            if isinstance(item, epub.Link):
                result.append((item.title, item.href))
            elif isinstance(item, tuple):
                section, children = item
                result.append((section.title, section.href))
                result.extend(flatten_toc(children))
        return result

    flat_toc = flatten_toc(book.toc)

    # Separate parts and chapters
    parts = {}           # part_title -> [chapter_title, ...]
    chapter_items = []   # [(chapter_title, href), ...]
    current_part = None

    for chapter_title, href in flat_toc:
        if '部分' in chapter_title or chapter_title.lower().startswith('part'):
            current_part = chapter_title
            parts[current_part] = []
        elif '章' in chapter_title or re.match(r'^(chapter|ch\.?\s*\d|\d+\.)', chapter_title, re.I):
            if current_part is None:
                current_part = "Chapters"
                parts[current_part] = []
            parts[current_part].append(chapter_title)
            chapter_items.append((chapter_title, href, get_preview(href)))

    # Fallback 1: no parts detected, treat all chapters as one flat list
    if not parts and chapter_items:
        parts["Contents"] = [t for t, _, _ in chapter_items]

    # Fallback 2: pattern-based detection found nothing. This happens when the
    # book's chapters have plain titles with no "Chapter N" / "第N章" prefix
    # (e.g. "Architecting for Innovation"). Fall back to the top-level TOC
    # structure — each top-level entry is a chapter — and skip common
    # front/back matter so chapter numbering starts at the real Chapter 1.
    #
    # Known limitation: this only fires when the pattern pass finds *zero*
    # chapters. A book that mixes numbered chapters with plain-titled sections
    # keeps the (partial) pattern result and never reaches here.
    if not chapter_items:
        # Match whole front/back-matter titles only. Anchored at both ends (with
        # an optional trailing subtitle after ':' / '—') so a real chapter like
        # "Indexing Strategies" or "Content Delivery Networks" is NOT dropped by
        # a bare prefix collision with "index" / "contents".
        skip_matter = re.compile(
            r'^\s*('
            r'preface|foreword|contents|table of contents|index|'
            r'about the authors?|other books[\w\s]*|copyright|dedication|'
            r'acknowledge?ments?|glossary|references|bibliography|'
            r'前言|序言?|目录|索引|致谢|版权|参考文献'
            r')\s*([:：—-].*)?$',
            re.I,
        )
        kept, skipped = [], []
        for ch_title, href in top_level_entries(book.toc):
            if not ch_title or skip_matter.match(ch_title.strip()):
                skipped.append(ch_title)
                continue
            kept.append((ch_title, href))
        for ch_title, href in kept:
            chapter_items.append((ch_title, href, get_preview(href)))
        if chapter_items:
            parts["Contents"] = [t for t, _, _ in chapter_items]
            print(f"ℹ️   No numbered chapters found; using top-level TOC "
                  f"sections ({len(chapter_items)} chapters).")
            if skipped:
                print("     skipped front/back matter (eyeball these): "
                      + ", ".join(repr(s) for s in skipped))

    return title, author, parts, chapter_items


def extract_epub_cover(filepath: str, out_dir: Path) -> str | None:
    """
    Extract the embedded cover image from an EPUB and save it as
    {out_dir}/cover.{ext}. Tries, in order:
      1. EPUB3 `properties="cover-image"` item (ebooklib.ITEM_COVER)
      2. EPUB2 `<meta name="cover" content="{id}"/>` in the OPF
      3. Any image item whose filename contains "cover"
    Returns the saved file's path (str) relative to nothing in particular —
    caller is responsible for turning it into a vault-relative path. None if
    no cover could be found.
    """
    import ebooklib
    from ebooklib import epub

    book = epub.read_epub(filepath)

    cover_item = next(iter(book.get_items_of_type(ebooklib.ITEM_COVER)), None)

    if cover_item is None:
        cover_meta = book.get_metadata('OPF', 'cover')
        cover_id = cover_meta[0][1].get('content') if cover_meta else None
        if cover_id:
            cover_item = book.get_item_with_id(cover_id)

    if cover_item is None:
        for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
            if 'cover' in item.get_name().lower():
                cover_item = item
                break

    if cover_item is None:
        return None

    ext = Path(cover_item.get_name()).suffix or '.jpg'
    cover_path = out_dir / f'cover{ext}'
    cover_path.write_bytes(cover_item.get_content())
    return str(cover_path)


# ── PDF parsing ───────────────────────────────────────────────────────────────

def parse_pdf(filepath: str):
    """
    Returns same shape as parse_epub.
    Uses pdfplumber; TOC extraction is best-effort.
    """
    try:
        import pdfplumber
    except ImportError:
        print("❌  Missing dependency. Run: pip install pdfplumber")
        sys.exit(1)

    title = Path(filepath).stem
    author = "Unknown"
    parts = {}
    chapter_items = []

    with pdfplumber.open(filepath) as pdf:
        # Try to extract TOC from metadata
        info = pdf.metadata or {}
        if info.get('Title'):
            title = info['Title']
        if info.get('Author'):
            author = info['Author']

        # Heuristic: scan first 20 pages for chapter headings
        heading_pattern = re.compile(
            r'^(第\s*\d+\s*章|Chapter\s+\d+|CHAPTER\s+\d+|\d+\.\s+[A-Z\u4e00-\u9fff])',
            re.MULTILINE
        )
        current_part = "Contents"
        parts[current_part] = []
        chapter_texts = {}

        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            for match in heading_pattern.finditer(text):
                heading = match.group(0).strip()
                # Grab ~60 words after the heading as preview
                after = text[match.end():match.end() + 400]
                preview = clean_preview(after)
                parts[current_part].append(heading)
                chapter_items.append((heading, f"page_{i+1}", preview))

    if not chapter_items:
        print("⚠️  Could not extract chapter structure from PDF automatically.")
        print("    Consider providing an EPUB version for better results.")

    return title, author, parts, chapter_items


# ── File generators ───────────────────────────────────────────────────────────

def _yaml_escape(s: str) -> str:
    """Escape backslashes and double quotes so a value stays a valid
    double-quoted YAML scalar (titles/authors/paths can contain either)."""
    return s.replace('\\', '\\\\').replace('"', '\\"')


def write_meta(out_dir: Path, title: str, author: str,
               source_path: str = None, source_key: str = "epub_path",
               cover_path: str = None, ibooks_source: str = None):
    source_line = f'\n{source_key}: "{_yaml_escape(source_path)}"' if source_path else ""
    cover_line = f'\ncover: "{_yaml_escape(cover_path)}"' if cover_path else ""
    ibooks_line = f'\nibooks_source: "{_yaml_escape(ibooks_source)}"' if ibooks_source else ""
    content = f"""---
title: "{_yaml_escape(title)}"
author: "{_yaml_escape(author)}"
archetype:
output_target:
reading_channel:{source_line}{cover_line}{ibooks_line}
status: reading
started: {date.today()}
finished:
progress: {{}}
---

# {title} — Meta

## 这本书要解决什么问题？


## 作者的核心主张是什么？


## 我读这本书想得到什么？


## 跨章回顾
> 读完整本书后填写（AI 问，你答，记录要点）

## 全局连接
> 读完整本后的宏观 differentiation

## 读后感
> 你自己写——这本书改变了什么？值不值得推荐？

## 整体评价

"""
    (out_dir / "meta.md").write_text(content, encoding='utf-8')


def write_moc(out_dir: Path, title: str, parts: dict, filenames: dict):
    lines = [
        f'---',
        f'title: "{_yaml_escape(title)} — Map of Content"',
        f'---',
        f'',
        f'# {title} — Map of Content',
        f'',
        f'## Meta',
        f'- [[meta]]',
        f'',
        f'## Chapters',
        f'',
    ]
    for part, chapters in parts.items():
        lines.append(f'### {part}')
        for ch in chapters:
            fname = filenames.get(ch)
            if fname:
                lines.append(f'- [[chapters/{fname}|{ch}]]')
            else:
                lines.append(f'- {ch}')
        lines.append('')

    lines += [
        '## Working Notes',
        '',
        '## Understanding',
        '- [[understanding]]',
        '',
        '## WeRead',
        '> WeRead 划线和批注见 `WeRead/` 对应书目',
        '',
    ]
    (out_dir / "MOC.md").write_text('\n'.join(lines), encoding='utf-8')


def chapter_filename_stem(chapter_num: int, title: str) -> str:
    """Build a chapter's filename stem (no extension) from its number and
    title — e.g. (1, "1. Architecting for Innovation") -> "Ch01_Architecting
    for Innovation".

    Single source of truth for this convention: write_chapter() below uses
    it to create chapters/*.md, and extract_fulltext.py's
    verify_chapter_alignment() calls it too, to re-derive the same stem from
    a freshly re-parsed EPUB TOC and catch silent chapter misalignment
    (e.g. chapters/ manually renamed/reordered). Keeping this in one place
    means the two can't drift apart — a change here automatically propagates
    to both.
    """
    # Strip leading "N. " or "N " from title so filename isn't "Ch01_1 Title"
    clean_title = re.sub(r'^\d+[\.\s]+', '', title).strip()
    return f"Ch{chapter_num:02d}_{safe_filename(clean_title)}"


def write_chapter(chapters_dir: Path, chapter_num: int, title: str, preview: str,
                  weread_name: str = None, weread_heading: str = None):
    fname = chapter_filename_stem(chapter_num, title)

    weread_section = ""
    if weread_name and weread_heading:
        weread_section = f"""
## WeRead
> 📌 **划线** → [[{weread_name}#{weread_heading}]]
> 💭 **读书笔记** → [[{weread_name}#读书笔记]]
"""

    content = f"""---
title: "{_yaml_escape(title)}"
chapter: {chapter_num}
status: unread
---

# {title}

> **一句话：** {preview}…
{weread_section}
"""
    (chapters_dir / f"{fname}.md").write_text(content, encoding='utf-8')
    return fname


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Initialize Obsidian book notes from EPUB or PDF.')
    parser.add_argument('--file',   required=True, help='Path to the EPUB or PDF file')
    parser.add_argument('--output', required=True, help='Path to the Books notes directory')
    parser.add_argument('--title',  default=None,  help='Override book title (use when metadata is bad)')
    args = parser.parse_args()

    filepath = args.file
    output_root = Path(args.output)

    if not os.path.exists(filepath):
        print(f"❌  File not found: {filepath}")
        sys.exit(1)

    ext = Path(filepath).suffix.lower()
    print(f"📖  Parsing {ext.upper()} file...")

    if ext == '.epub':
        title, author, parts, chapter_items = parse_epub(filepath)
    elif ext == '.pdf':
        title, author, parts, chapter_items = parse_pdf(filepath)
    else:
        print(f"❌  Unsupported format: {ext}. Only .epub and .pdf are supported.")
        sys.exit(1)

    # Override title if provided
    if args.title:
        title = args.title

    # Create output directories
    out_dir = output_root / title
    chapters_dir = out_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    # Check for WeRead notes
    vault_dir = VAULT_ROOT
    weread_name, weread_headings = find_weread(vault_dir, title)
    weread_matched = 0
    if weread_name:
        print(f"📚  Found WeRead notes: {weread_name}")

    # Check for Apple Books (iBooks) highlights export
    ibooks_source = find_ibooks(vault_dir, title)
    if ibooks_source:
        print(f"📚  Found iBooks highlights: {ibooks_source}")

    # Extract embedded cover image (EPUB only — PDF cover extraction isn't
    # reliable enough to bother with, matching the fulltext-cache limitation)
    cover_rel_path = None
    if ext == '.epub':
        cover_abs_path = extract_epub_cover(filepath, out_dir)
        if cover_abs_path:
            cover_path = Path(cover_abs_path)
            if cover_path.is_absolute():
                try:
                    cover_rel_path = str(cover_path.relative_to(vault_dir))
                except ValueError:
                    # Cover landed outside VAULT_ROOT (e.g. --output outside the vault) —
                    # skip the cover: field rather than aborting onboarding mid-flight.
                    cover_rel_path = None
            else:
                cover_rel_path = cover_abs_path
            if cover_rel_path:
                print(f"🖼️   Cover extracted: {cover_rel_path}")

    # Generate chapter files and collect filenames for map links
    filenames = {}  # chapter_title -> filename stem
    ch_num = 1
    for ch_title, _href, preview in chapter_items:
        # Try to match this chapter to a WeRead heading
        wr_heading = None
        if weread_name:
            wr_heading = match_weread_heading(ch_title, weread_headings)
            if wr_heading:
                weread_matched += 1
        fname = write_chapter(chapters_dir, ch_num, ch_title, preview,
                             weread_name=weread_name,
                             weread_heading=wr_heading)
        filenames[ch_title] = fname
        ch_num += 1

    abs_source_path = str(Path(filepath).expanduser().resolve())
    source_key = "epub_path" if ext == '.epub' else "pdf_path"
    write_meta(out_dir, title, author, source_path=abs_source_path, source_key=source_key,
               cover_path=cover_rel_path, ibooks_source=ibooks_source)
    write_moc(out_dir, title, parts, filenames)

    # Create notes/ directory and the understanding.md capture record placeholder
    (out_dir / "notes").mkdir(exist_ok=True)
    understanding_file = out_dir / "understanding.md"
    if not understanding_file.exists():
        understanding_file.write_text(
            f"# {title} — Understanding\n\n"
            "> 每章一条记录：AI 生成的结构地图 + 核心概念，加上你自己的话的理解。\n"
            "> 机制见 `Learning/Books/CLAUDE.md` → \"The capture loop\"。\n",
            encoding="utf-8",
        )

    # Summary
    n_chapters = len(chapter_items)
    n_parts = len(parts)
    print(f"\n✅  {n_chapters} chapter files generated")
    print(f"✅  MOC.md  ({n_chapters} chapters across {n_parts} part(s))")
    print(f"✅  meta.md ready to fill")
    if weread_name:
        print(f"✅  WeRead linked: {weread_matched}/{n_chapters} chapters")
    if ibooks_source:
        print(f"✅  iBooks source linked: {ibooks_source}")
    if cover_rel_path:
        print(f"✅  Cover image: {cover_rel_path}")
    print(f"\n📁  Output: {out_dir}")
    print(f"\n👉  Next: open meta.md in Obsidian and fill in your reading goals.")


if __name__ == '__main__':
    main()

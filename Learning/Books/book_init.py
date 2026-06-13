#!/usr/bin/env python3
"""
book_init.py — Book Learning System Initializer
Usage:
    python3 book_init.py --file "/path/to/book.epub" --output "/path/to/Notes/Books"

Generates a ready-to-use Obsidian note structure for deep reading:
    {output}/{Book Title}/
    ├── 00_meta.md
    ├── 00_map.md
    └── chapters/
        ├── Ch01_{title}.md
        └── ...

Dependencies:
    pip install ebooklib beautifulsoup4 pdfplumber
"""

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path


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

    # Flatten TOC
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

    # Fallback: no parts detected, treat all chapters as one flat list
    if not parts and chapter_items:
        parts["Contents"] = [t for t, _, _ in chapter_items]

    return title, author, parts, chapter_items


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

def write_meta(out_dir: Path, title: str, author: str):
    content = f"""---
title: "{title}"
author: "{author}"
status: reading
started: {date.today()}
finished:
tags: [book]
---

# {title} — Meta

## 这本书要解决什么问题？
<!-- 读前填写 -->

## 作者的核心主张是什么？
<!-- 读前填写，读中随时更新 -->

## 我读这本书想得到什么？
<!-- 读前填写 -->

## 读完后的整体评价
<!-- 读完后填写 -->
"""
    (out_dir / "00_meta.md").write_text(content, encoding='utf-8')


def write_map(out_dir: Path, title: str, parts: dict, filenames: dict):
    lines = [
        f'---',
        f'title: "{title} — Full Map"',
        f'updated: {date.today()}',
        f'---',
        f'',
        f'# {title} — Full Map',
        f'',
        f'> 用来追踪整本书的结构和章节间的关系。随阅读进度持续更新。',
        f'',
    ]
    for part, chapters in parts.items():
        lines.append(f'## {part}')
        for ch in chapters:
            fname = filenames.get(ch)
            if fname:
                lines.append(f'- [[chapters/{fname}|{ch}]]')
            else:
                lines.append(f'- {ch}')
        lines.append('')

    lines += [
        '## 核心概念网络',
        '<!-- 读完后在这里用 [[wikilinks]] 连接跨章节的重复概念 -->',
        '',
    ]
    (out_dir / "00_map.md").write_text('\n'.join(lines), encoding='utf-8')


def write_chapter(chapters_dir: Path, chapter_num: int, title: str, preview: str,
                  book_title: str = "", weread_name: str = None, weread_heading: str = None):
    # Strip leading "N. " or "N " from title so filename isn't "Ch01_1 Title"
    clean_title = re.sub(r'^\d+[\.\s]+', '', title).strip()
    fname = f"Ch{chapter_num:02d}_{safe_filename(clean_title)}"

    weread_section = ""
    if weread_name and weread_heading:
        weread_section = f"""
## WeRead
> 📌 **划线** → [[{weread_name}#{weread_heading}]]
> 💭 **读书笔记** → [[{weread_name}#读书笔记]]
"""

    content = f"""---
title: "{title}"
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
    vault_dir = output_root.parent  # Books/ -> vault root
    weread_name, weread_headings = find_weread(vault_dir, title)
    weread_matched = 0
    if weread_name:
        print(f"📚  Found WeRead notes: {weread_name}")

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
                             book_title=title, weread_name=weread_name,
                             weread_heading=wr_heading)
        filenames[ch_title] = fname
        ch_num += 1

    write_meta(out_dir, title, author)
    write_map(out_dir, title, parts, filenames)

    # Summary
    n_chapters = len(chapter_items)
    n_parts = len(parts)
    print(f"\n✅  {n_chapters} chapter files generated")
    print(f"✅  00_map.md  ({n_chapters} chapters across {n_parts} part(s))")
    print(f"✅  00_meta.md ready to fill")
    if weread_name:
        print(f"✅  WeRead linked: {weread_matched}/{n_chapters} chapters")
    print(f"\n📁  Output: {out_dir}")
    print(f"\n👉  Next: open 00_meta.md in Obsidian and fill in your reading goals.")


if __name__ == '__main__':
    main()

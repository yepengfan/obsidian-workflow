#!/usr/bin/env python3
"""
test_extract_fulltext.py — Unit tests for extract_fulltext.py's pure functions

Usage:
    "Learning/Books/.venv/bin/python3" -m unittest Learning/Books/test_extract_fulltext.py -v
    # or, from inside Learning/Books/:
    ".venv/bin/python3" -m unittest test_extract_fulltext -v

Covers the logic that's had manual, ad hoc verification across PR #147's
review rounds — codified here so future changes to extract_fulltext.py or
book_init.py get automatic regression coverage instead of requiring a fresh
manual pass each time:

  - _yaml_unescape()          — exact inverse of book_init._yaml_escape()
  - file_sha256()             — content-based (not size/mtime-based) change
                                 detection
  - verify_chapter_alignment() — catches silent chapter misattribution
  - chapter_filename_stem()   — the single naming convention shared by
                                 book_init.write_chapter() and
                                 extract_fulltext.verify_chapter_alignment()

No EPUB/network/filesystem fixtures needed — every function under test here
is a pure function over plain strings/lists, by design (see each function's
own docstring for why it was kept that way).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import book_init
from extract_fulltext import _yaml_unescape, file_sha256, verify_chapter_alignment


class TestYamlUnescape(unittest.TestCase):
    """_yaml_unescape() must be the exact inverse of book_init._yaml_escape(),
    for every string book_init.py might plausibly write into a meta.md
    frontmatter value (titles, authors, absolute file paths)."""

    def _round_trip(self, original: str):
        escaped = book_init._yaml_escape(original)
        return _yaml_unescape(escaped)

    def test_plain_string_unchanged(self):
        s = "Software Architecture Patterns for Serverless Systems"
        self.assertEqual(self._round_trip(s), s)

    def test_embedded_double_quotes(self):
        s = 'Title with "embedded quotes"'
        self.assertEqual(self._round_trip(s), s)

    def test_windows_style_backslash_path(self):
        s = r"C:\Users\test\Some Book.epub"
        self.assertEqual(self._round_trip(s), s)

    def test_macos_absolute_path_no_special_chars(self):
        # The actual shape of path this script reads from meta.md day to day.
        s = "/Users/tedfan/Library/ebooks/Some Book -- Author -- Ed 2, 2024.epub"
        self.assertEqual(self._round_trip(s), s)

    def test_backslash_immediately_before_quote(self):
        # The edge case a naive two-pass .replace() implementation gets
        # wrong: a literal backslash sitting right next to an escaped quote.
        s = r'edge: backslash right before quote \"like this\"'
        self.assertEqual(self._round_trip(s), s)

    def test_multiple_consecutive_backslashes(self):
        s = r"a\\b\\\c"
        self.assertEqual(self._round_trip(s), s)


class TestFileSha256(unittest.TestCase):
    """Content hash must detect real content changes and ignore everything
    else (this is the whole point of using it instead of size/mtime for
    staleness detection — see file_sha256()'s docstring)."""

    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _write(self, name: str, content: bytes) -> str:
        p = self.dir / name
        p.write_bytes(content)
        return str(p)

    def test_identical_content_same_hash(self):
        a = self._write("a.bin", b"hello world" * 10000)
        b = self._write("b.bin", b"hello world" * 10000)
        self.assertEqual(file_sha256(a), file_sha256(b))

    def test_one_byte_difference_changes_hash(self):
        a = self._write("a.bin", b"hello world" * 10000)
        c = self._write("c.bin", b"hello world" * 10000 + b"X")
        self.assertNotEqual(file_sha256(a), file_sha256(c))

    def test_mtime_change_alone_does_not_change_hash(self):
        # The exact regression this function exists to prevent: a
        # same-content S3 re-sync touches mtime but not bytes.
        import os
        import time
        a = self._write("a.bin", b"stable content")
        h_before = file_sha256(a)
        os.utime(a, (time.time() + 1000, time.time() + 1000))
        h_after = file_sha256(a)
        self.assertEqual(h_before, h_after)


class TestChapterAlignment(unittest.TestCase):
    """verify_chapter_alignment() must stay silent when chapters/ genuinely
    matches the EPUB's TOC, and must precisely flag any chapter that
    doesn't — this is the guard against silently writing one chapter's text
    into a different chapter's cache file."""

    CHAPTER_ITEMS = [
        ("Architecting for Innovation", "href1", "preview1"),
        ("Defining Boundaries and Letting Go", "href2", "preview2"),
        ("Taming the Presentation Tier", "href3", "preview3"),
    ]

    def test_aligned_chapters_report_no_mismatches(self):
        stems = [
            book_init.chapter_filename_stem(i + 1, title)
            for i, (title, _href, _preview) in enumerate(self.CHAPTER_ITEMS)
        ]
        self.assertEqual(verify_chapter_alignment(self.CHAPTER_ITEMS, stems), [])

    def test_single_renamed_chapter_is_flagged_precisely(self):
        stems = [
            book_init.chapter_filename_stem(i + 1, title)
            for i, (title, _href, _preview) in enumerate(self.CHAPTER_ITEMS)
        ]
        # Simulate a manual rename/reorder of chapters/Ch02_*.md
        stems[1] = "Ch02_SOMETHING ELSE ENTIRELY"

        mismatches = verify_chapter_alignment(self.CHAPTER_ITEMS, stems)

        self.assertEqual(len(mismatches), 1)
        chapter_num, expected, actual = mismatches[0]
        self.assertEqual(chapter_num, 2)
        self.assertEqual(expected, "Ch02_Defining Boundaries and Letting Go")
        self.assertEqual(actual, "Ch02_SOMETHING ELSE ENTIRELY")

    def test_missing_stem_reported_as_none_not_a_crash(self):
        # chapters/ has fewer files than the EPUB TOC found — must report
        # the gap, not raise an IndexError.
        stems = ["Ch01_Architecting for Innovation"]
        mismatches = verify_chapter_alignment(self.CHAPTER_ITEMS, stems)
        reported_chapters = [m[0] for m in mismatches]
        self.assertIn(2, reported_chapters)
        self.assertIn(3, reported_chapters)
        missing = next(m for m in mismatches if m[0] == 2)
        self.assertIsNone(missing[2])  # actual_stem is None, not an exception


class TestChapterFilenameStemSharedConvention(unittest.TestCase):
    """Guards the DRY fix itself: book_init.chapter_filename_stem() is the
    single source of truth write_chapter() and verify_chapter_alignment()
    both depend on — this pins its behavior so a future edit to it is a
    deliberate, visible decision instead of an accidental drift."""

    def test_strips_leading_numeric_prefix(self):
        self.assertEqual(
            book_init.chapter_filename_stem(1, "1. Architecting for Innovation"),
            "Ch01_Architecting for Innovation",
        )

    def test_no_numeric_prefix_unaffected(self):
        self.assertEqual(
            book_init.chapter_filename_stem(3, "Taming the Presentation Tier"),
            "Ch03_Taming the Presentation Tier",
        )

    def test_zero_pads_chapter_number(self):
        self.assertEqual(
            book_init.chapter_filename_stem(9, "Some Title"),
            "Ch09_Some Title",
        )
        self.assertEqual(
            book_init.chapter_filename_stem(13, "Some Title"),
            "Ch13_Some Title",
        )


if __name__ == '__main__':
    unittest.main()

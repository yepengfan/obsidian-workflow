#!/usr/bin/env python3
"""Detect which Book Summaries need updating based on WeRead file changes.

Compares modification times: if a WeRead source file is newer than its
corresponding Book Summary, that summary needs regeneration. Also detects
new WeRead books that have no summary yet.

Output format (machine-readable):
  ALL_SYNCED                        — nothing to do
  NEEDS_UPDATE:<weread_source>|<summary_filename>
  NEW_BOOK:<weread_source>
"""

import os
import re
import glob
import sys

VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SUMMARIES_DIR = os.path.join(VAULT_ROOT, "Book Summaries")
WEREAD_DIR = os.path.join(VAULT_ROOT, "WeRead")


def get_source_from_summary(filepath):
    """Extract the WeRead source path from a summary's frontmatter."""
    with open(filepath, "r", encoding="utf-8") as f:
        in_frontmatter = False
        for line in f:
            if line.strip() == "---":
                if in_frontmatter:
                    break
                in_frontmatter = True
                continue
            if in_frontmatter:
                match = re.search(r'source:\s*"\[\[(.+?)\]\]"', line)
                if match:
                    return match.group(1)
    return None


def count_highlights(filepath):
    """Rough count of highlights in a WeRead file (lines starting with >)."""
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("> ") or line.startswith(">◆"):
                count += 1
    return count


def main():
    summary_files = glob.glob(os.path.join(SUMMARIES_DIR, "*.md"))
    summary_files = [f for f in summary_files if "Index" not in os.path.basename(f)]

    # Map WeRead source paths to their summary files
    source_to_summary = {}
    for sf in summary_files:
        source = get_source_from_summary(sf)
        if source:
            source_to_summary[source] = sf

    results = set()

    # Check existing summaries for updates
    for source, summary_path in source_to_summary.items():
        weread_path = os.path.join(VAULT_ROOT, source + ".md")
        if os.path.exists(weread_path):
            real_weread = os.path.realpath(weread_path)
            weread_mtime = os.path.getmtime(real_weread)
            summary_mtime = os.path.getmtime(summary_path)
            if weread_mtime > summary_mtime:
                results.add(f"NEEDS_UPDATE:{source}|{os.path.basename(summary_path)}")

    # Check for new WeRead books without summaries
    all_weread_sources = set()
    seen_real_paths = set()
    for root, dirs, files in os.walk(WEREAD_DIR, followlinks=False):
        for f in files:
            if f.endswith(".md"):
                full_path = os.path.join(root, f)
                real_path = os.path.realpath(full_path)
                if real_path in seen_real_paths:
                    continue
                seen_real_paths.add(real_path)
                rel = os.path.relpath(full_path, VAULT_ROOT)
                rel_no_ext = os.path.splitext(rel)[0]
                all_weread_sources.add(rel_no_ext)

    covered_sources = set(source_to_summary.keys())
    uncovered = all_weread_sources - covered_sources

    for source in sorted(uncovered):
        weread_path = os.path.join(VAULT_ROOT, source + ".md")
        if os.path.exists(weread_path):
            highlights = count_highlights(weread_path)
            if highlights >= 3:
                results.add(f"NEW_BOOK:{source}")

    if not results:
        print("ALL_SYNCED")
        return 0

    updates = [r for r in results if r.startswith("NEEDS_UPDATE:")]
    new_books = [r for r in results if r.startswith("NEW_BOOK:")]
    print(f"SUMMARY: {len(updates)} updated, {len(new_books)} new")
    for r in sorted(results):
        print(r)
    return 1


if __name__ == "__main__":
    sys.exit(main())

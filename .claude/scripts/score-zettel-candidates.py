#!/usr/bin/env python3
"""
Promote zettel: growing → candidate

Scans all growing zettel and promotes those that meet evergreen criteria:
  - Related links >= MIN_LINKS
  - Unique topics across all related zettel >= MIN_TOPICS

Run manually:
  python3 .claude/scripts/score-zettel-candidates.py
  python3 .claude/scripts/score-zettel-candidates.py --dry-run
"""

import re
import os
import sys
import argparse

VAULT = os.path.join(os.path.dirname(__file__), "..", "..", "Zettelkasten")
MIN_LINKS = 5
MIN_TOPICS = 3


def parse_frontmatter(content):
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^(\w+):\s*(.+)", line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip()
        # parse topics list: topics: [a, b, c]
        topics_m = re.match(r"^topics:\s*\[(.+)\]", line)
        if topics_m:
            fm["topics"] = [t.strip() for t in topics_m.group(1).split(",")]
    return fm


def get_related_links(content):
    m = re.search(r"^Related::(.*)", content, re.MULTILINE)
    if not m:
        return []
    return re.findall(r"\[\[([^\]|#]+?)(?:\|[^\]]+)?\]\]", m.group(1))


def load_zettel(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_index(zettel_dir):
    """Map note title → file path for all zettel."""
    index = {}
    for fname in os.listdir(zettel_dir):
        if fname.endswith(".md") and fname != "Zettelkasten Index.md":
            title = fname[:-3]
            index[title] = os.path.join(zettel_dir, fname)
    return index


def score(content, index, min_links=MIN_LINKS, min_topics=MIN_TOPICS):
    links = get_related_links(content)
    if len(links) < min_links:
        return len(links), set(), False

    # Collect topics from all related zettel
    cross_topics = set()
    for link in links:
        related_path = index.get(link)
        if related_path and os.path.exists(related_path):
            related_content = load_zettel(related_path)
            fm = parse_frontmatter(related_content)
            for t in fm.get("topics", []):
                cross_topics.add(t)

    qualified = len(cross_topics) >= min_topics
    return len(links), cross_topics, qualified


def promote(path, dry_run):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = re.sub(
        r"^status:\s*growing", "status: candidate", content, flags=re.MULTILINE
    )
    if not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show results without modifying files")
    parser.add_argument("--min-links", type=int, default=MIN_LINKS)
    parser.add_argument("--min-topics", type=int, default=MIN_TOPICS)
    args = parser.parse_args()

    min_links = args.min_links
    min_topics = args.min_topics

    zettel_dir = os.path.abspath(VAULT)
    index = build_index(zettel_dir)

    promoted = []
    skipped = []

    for title, path in sorted(index.items()):
        content = load_zettel(path)
        fm = parse_frontmatter(content)
        if fm.get("status") != "growing":
            continue

        link_count, cross_topics, qualified = score(content, index, min_links, min_topics)

        if qualified:
            promoted.append((title, link_count, cross_topics))
            promote(path, args.dry_run)
        else:
            skipped.append((title, link_count, len(cross_topics)))

    tag = "[dry-run] " if args.dry_run else ""

    print(f"\n{tag}=== Promoted to candidate: {len(promoted)} ===")
    for title, links, topics in promoted:
        print(f"  ✓ {title}")
        print(f"    {links} links · {len(topics)} cross-topics: {', '.join(sorted(topics)[:5])}{'…' if len(topics) > 5 else ''}")

    print(f"\n{tag}=== Skipped (growing, below threshold): {len(skipped)} ===")
    for title, links, topic_count in skipped:
        print(f"  · {title} ({links} links, {topic_count} topics)")

    print(f"\nThresholds: links >= {min_links}, cross-topics >= {min_topics}")
    if args.dry_run:
        print("Dry run — no files modified.")


if __name__ == "__main__":
    main()

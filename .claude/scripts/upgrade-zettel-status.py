#!/usr/bin/env python3
"""
Auto-upgrade zettel status: seedling → growing
Triggered by PostToolUse hook (Write/Edit) via CLAUDE_TOOL_INPUT on stdin.

Upgrades the saved file only if:
  - It lives in Zettelkasten/ (not the Index)
  - Its current status is 'seedling'
  - Its Related:: line contains 2+ [[wikilinks]]
"""

import json, re, sys, os


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    file_path = data.get("file_path", "")

    if "Zettelkasten/" not in file_path or "Index" in file_path:
        sys.exit(0)

    if not os.path.exists(file_path):
        sys.exit(0)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    status_match = re.search(r"^status:\s*(\w+)", content, re.MULTILINE)
    if not status_match or status_match.group(1) != "seedling":
        sys.exit(0)

    related_match = re.search(r"^Related::(.*)", content, re.MULTILINE)
    if not related_match:
        sys.exit(0)

    links = re.findall(r"\[\[", related_match.group(1))
    if len(links) < 2:
        sys.exit(0)

    new_content = re.sub(
        r"^status:\s*seedling", "status: growing", content, flags=re.MULTILINE
    )
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    name = os.path.basename(file_path)
    print(f"[zettel] Upgraded seedling → growing: {name}")


if __name__ == "__main__":
    main()

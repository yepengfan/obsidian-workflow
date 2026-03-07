#!/bin/bash
# Auto-upgrade zettel status: seedling → growing when Related:: has 2+ links
# Triggered by PostToolUse hook after writes to Zettelkasten/

ZETTEL_DIR="/Users/tedfan/Vaults/Workspace/Zettelkasten"

python3 - <<'EOF'
import re, os, glob, sys

zettel_dir = "/Users/tedfan/Vaults/Workspace/Zettelkasten"
upgraded = []

for path in glob.glob(f"{zettel_dir}/*.md"):
    if "Index" in path:
        continue
    with open(path, 'r') as f:
        content = f.read()

    status_match = re.search(r'^status:\s*(\w+)', content, re.MULTILINE)
    if not status_match or status_match.group(1) != 'seedling':
        continue

    related_match = re.search(r'^Related::(.*)', content, re.MULTILINE)
    if not related_match:
        continue

    links = re.findall(r'\[\[', related_match.group(1))
    if len(links) >= 2:
        new_content = re.sub(r'^status:\s*seedling', 'status: growing', content, flags=re.MULTILINE)
        with open(path, 'w') as f:
            f.write(new_content)
        upgraded.append(os.path.basename(path))

if upgraded:
    print(f"[zettel] Upgraded {len(upgraded)} seedling → growing: {', '.join(upgraded)}")
EOF

#!/bin/bash
# Auto-sync hook: runs after Edit/Write, commits tracked system files to git
# Called by Claude Code PostToolUse hook with JSON on stdin

# Derive vault path from script location: .claude/scripts/ -> vault root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Read the edited file path from hook stdin
FILE=$(cat | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$FILE" ] && exit 0

# Only sync if the file is a tracked system file
case "$FILE" in
  */CLAUDE.md|*/README.md|*/Home.md|*/.claude/*|*/Templates/*|*/Books/book_init.py|*/Books/Books\ Index.md|*/Books/.bookrc.example)
    ;;
  *)
    exit 0
    ;;
esac

# Auto-commit and push from the vault repo
cd "$VAULT" || exit 0
if ! git diff --quiet HEAD 2>/dev/null || [ -n "$(git ls-files --others --exclude-standard)" ]; then
  git add -A
  git commit -q -m "Auto-sync: $(basename "$FILE") updated"
  git push -q origin main 2>/dev/null
fi

exit 0

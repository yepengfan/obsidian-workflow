#!/bin/bash
# Auto-sync hook: runs after Edit/Write, only syncs if a config file changed
# Called by Claude Code PostToolUse hook with JSON on stdin

# Derive vault path from script location: .claude/scripts/ -> vault root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP="$HOME/obsidian-config"

# Read the edited file path from hook stdin
FILE=$(cat | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$FILE" ] && exit 0

# Only sync if the file is one we back up
case "$FILE" in
  */CLAUDE.md|*/Home.md|*/.claude/*|*/.obsidian/*|*/Templates/*|*/Work/Work\ Dashboard.md)
    ;;
  *)
    exit 0
    ;;
esac

# Run sync silently
"$BACKUP/sync.sh" > /dev/null 2>&1

# Auto-commit if there are changes
cd "$BACKUP" || exit 0
if ! git diff --quiet HEAD 2>/dev/null || [ -n "$(git ls-files --others --exclude-standard)" ]; then
  git add -A
  git commit -q -m "Auto-sync: $(basename "$FILE") updated"
  git push -q origin main 2>/dev/null
fi

exit 0

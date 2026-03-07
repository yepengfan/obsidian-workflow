#!/bin/bash
# Auto-sync hook: runs after Edit/Write, commits tracked system files to git
# Uses a persistent auto-sync branch + single open PR to avoid PR spam.
# Called by Claude Code PostToolUse hook with JSON on stdin

BRANCH="auto-sync"

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

cd "$VAULT" || exit 0

# Check for changes
git diff --quiet HEAD 2>/dev/null && [ -z "$(git ls-files --others --exclude-standard)" ] && exit 0

# Ensure we're on main, then branch
CURRENT=$(git branch --show-current)
if [ "$CURRENT" != "$BRANCH" ]; then
  # Update main and create/reset auto-sync branch from it
  git fetch -q origin main 2>/dev/null
  git checkout -q main 2>/dev/null
  git reset -q --hard origin/main 2>/dev/null

  # Create or switch to auto-sync branch
  if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    git checkout -q "$BRANCH"
    git merge -q main --no-edit 2>/dev/null
  else
    git checkout -q -b "$BRANCH"
  fi
fi

# Stage and commit
git add -A
git commit -q -m "Auto-sync: $(basename "$FILE") updated"
git push -q origin "$BRANCH" 2>/dev/null

# Create PR if none exists
OPEN_PR=$(gh pr list --head "$BRANCH" --state open --json number --jq '.[0].number' 2>/dev/null)
if [ -z "$OPEN_PR" ]; then
  gh pr create --head "$BRANCH" --base main \
    --title "Auto-sync: system file updates" \
    --body "Automated PR from auto-sync hook. Merge when ready." \
    2>/dev/null
fi

# Switch back to main for normal work
git checkout -q main 2>/dev/null

exit 0

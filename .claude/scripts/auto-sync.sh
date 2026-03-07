#!/bin/bash
# Auto-sync hook: runs after Edit/Write, commits tracked system files to git
# Uses a temporary worktree to avoid branch switching in the working directory.
# Maintains a single open PR on the auto-sync branch.
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

# Fetch latest remote state
git fetch -q origin 2>/dev/null

# Clean up stale local auto-sync branch if remote was deleted (PR merged)
if git show-ref --verify --quiet "refs/heads/$BRANCH" && \
   ! git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
  git branch -q -D "$BRANCH" 2>/dev/null
fi

# Create auto-sync branch from main if it doesn't exist
if ! git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git branch "$BRANCH" origin/main 2>/dev/null
fi

# Clean up any stale worktrees from previous runs
git worktree prune 2>/dev/null

# Set up temporary worktree for the auto-sync branch
WORK_DIR=$(mktemp -d)
trap 'git worktree remove --force "$WORK_DIR" 2>/dev/null; rm -rf "$WORK_DIR"' EXIT
git worktree add -q "$WORK_DIR" "$BRANCH" 2>/dev/null || exit 0

# Copy changed tracked files to worktree
git diff --name-only HEAD 2>/dev/null | while read -r f; do
  mkdir -p "$WORK_DIR/$(dirname "$f")"
  cp "$VAULT/$f" "$WORK_DIR/$f"
done
git ls-files --others --exclude-standard 2>/dev/null | while read -r f; do
  mkdir -p "$WORK_DIR/$(dirname "$f")"
  cp "$VAULT/$f" "$WORK_DIR/$f"
done

# Commit in the worktree
cd "$WORK_DIR"
git add -A
git diff --cached --quiet && exit 0
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

exit 0

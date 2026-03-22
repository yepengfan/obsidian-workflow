#!/usr/bin/env bash
# AI Daily Digest — hybrid Python + Claude Code pipeline (phased).
#
# Step 0: Python fetches & deduplicates RSS feeds → JSON
# Step 1: Python scores articles in parallel (claude -p per batch) → JSON
# Step 2: Python summarizes in parallel (claude -p per batch) → JSON
# Step 3: Python assembles & writes Obsidian reports (~1s)
# Step 4: Bash archives old reports (>14 days)
#
# Designed for unattended background execution via Obsidian Shell Commands.
set -euo pipefail

# Ensure common tool paths are available (Obsidian Shell Commands has a minimal PATH)
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

# Log stderr to file (tee preserves console output for interactive callers)
LOG_FILE="$(cd "$(dirname "$0")" && pwd)/digest.log"
exec 2> >(tee -a "$LOG_FILE" >&2)
echo "[digest] ── Run started at $(date '+%Y-%m-%d %H:%M:%S') ──" >&2

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
FEED_DIR="$VAULT_DIR/Feeds/AI-Daily"
DIGEST_FILE="$FEED_DIR/$TODAY.md"
PYTHON="$SCRIPT_DIR/.venv/bin/python"

# ── Pre-flight checks ───────────────────────────────────────────────
if [ -f "$DIGEST_FILE" ]; then
    echo "[digest] Today's digest already exists: $DIGEST_FILE"
    exit 0
fi

if ! command -v claude &>/dev/null; then
    echo "[digest] ERROR: 'claude' CLI not found on PATH." >&2
    exit 1
fi

# ── Step 0: Fetch + Dedup (Python) ──────────────────────────────────
echo "[digest] Step 0: Fetching RSS feeds..."
ARTICLES=$("$PYTHON" "$SCRIPT_DIR/fetch.py" --vault-path "$VAULT_DIR") || {
    exit_code=$?
    if [ $exit_code -eq 2 ]; then
        echo "[digest] Digest already exists (fetcher check). Skipping."
        exit 0
    fi
    echo "[digest] Fetch failed (exit $exit_code)" >&2
    exit 1
}
echo "[digest] Step 0 complete."

# ── Step 1: Score & Select top 15 (parallel Python) ─────────────────
echo "[digest] Step 1: Scoring articles..."
SCORED=$(echo "$ARTICLES" | "$PYTHON" "$SCRIPT_DIR/score.py") || {
    echo "[digest] ERROR: Phase 1 (scoring) failed." >&2
    exit 1
}

if ! echo "$SCORED" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'top_articles' in d" 2>/dev/null; then
    echo "[digest] ERROR: Phase 1 did not return valid scored JSON." >&2
    exit 1
fi
echo "[digest] Step 1 complete: $(echo "$SCORED" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['top_articles']),'articles selected')")"

# ── Step 2: Bilingual Summarization (parallel Python) ───────────────
echo "[digest] Step 2: Summarizing articles..."
SUMMARIES=$(echo "$SCORED" | "$PYTHON" "$SCRIPT_DIR/summarize.py") || {
    echo "[digest] ERROR: Phase 2 (summarization) failed." >&2
    exit 1
}

if ! echo "$SUMMARIES" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'summaries' in d and 'trend_zh' in d" 2>/dev/null; then
    echo "[digest] ERROR: Phase 2 did not return valid summaries JSON." >&2
    exit 1
fi
echo "[digest] Step 2 complete: $(echo "$SUMMARIES" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['summaries']),'summaries generated')")"

# ── Step 3: Assemble & Write Reports (Python templating) ────────────
echo "[digest] Step 3: Writing reports..."

export TMPDIR_DIGEST=$(mktemp -d)
trap 'rm -rf "$TMPDIR_DIGEST"' EXIT
export TODAY VAULT_DIR
echo "$SCORED" > "$TMPDIR_DIGEST/scored.json"
echo "$SUMMARIES" > "$TMPDIR_DIGEST/summaries.json"
echo "$ARTICLES" > "$TMPDIR_DIGEST/articles.json"

python3 "$SCRIPT_DIR/write_reports.py"
echo "[digest] Step 3 complete."

# ── Step 4: Archive old reports ─────────────────────────────────────
echo "[digest] Step 4: Archiving reports older than 14 days..."
mkdir -p "$FEED_DIR/archive"

find "$FEED_DIR" -maxdepth 1 -name "*.md" -not -name "Dashboard.md" | while read -r f; do
    fname=$(basename "$f")
    fdate="${fname%%-en.md}"
    fdate="${fdate%.md}"
    if [[ "$fdate" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        days_old=$(( ( $(date -j -f "%Y-%m-%d" "$TODAY" +%s 2>/dev/null || date -d "$TODAY" +%s) \
                     - $(date -j -f "%Y-%m-%d" "$fdate" +%s 2>/dev/null || date -d "$fdate" +%s) ) / 86400 ))
        if [ "$days_old" -gt 14 ]; then
            mv "$f" "$FEED_DIR/archive/"
            echo "[digest]   Archived: $fname"
        fi
    fi
done

echo "[digest] Done!"

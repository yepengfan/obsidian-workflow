#!/usr/bin/env bash
# GitHub Trending — hybrid Python + Claude Code pipeline.
#
# Step 0: Python fetches trending repos → JSON
# Step 1: Python enriches repos via Claude CLI → JSON
# Step 2: Python assembles & writes Obsidian reports
# Step 3: Bash archives old reports (>14 days)
#
# Designed for unattended background execution via Obsidian Shell Commands.
set -euo pipefail

# Ensure common tool paths are available (Obsidian Shell Commands has a minimal PATH)
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

# Log stderr to file (tee preserves console output for interactive callers)
LOG_FILE="$(cd "$(dirname "$0")" && pwd)/trending.log"
exec 2> >(tee -a "$LOG_FILE" >&2)
echo "[trending] ── Run started at $(date '+%Y-%m-%d %H:%M:%S') ──" >&2

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
FEED_DIR="$VAULT_DIR/Feeds/GitHub-Trending"
REPORT_FILE="$FEED_DIR/$TODAY.md"

# ── Module toggle guard ─────────────────────────────────────────────
MODULE_FILE="$VAULT_DIR/system/modules/feeds-github-trending/module.md"
if grep -q "enabled: false" "$MODULE_FILE" 2>&1; then
    echo "[trending] Module feeds-github-trending is disabled, skipping." >&2
    exit 0
fi

# ── Pre-flight checks ───────────────────────────────────────────────
if [ -f "$REPORT_FILE" ]; then
    echo "[trending] Today's report already exists: $REPORT_FILE"
    exit 0
fi

if ! command -v claude &>/dev/null; then
    echo "[trending] ERROR: 'claude' CLI not found on PATH." >&2
    exit 1
fi

# ── Step 0: Fetch Trending Repos (Python) ───────────────────────────
echo "[trending] Step 0: Fetching trending repos..."
FETCHED=$(python3 "$SCRIPT_DIR/fetch.py" --vault-path "$VAULT_DIR") || {
    exit_code=$?
    if [ $exit_code -eq 2 ]; then
        echo "[trending] Report already exists (fetcher check). Skipping."
        exit 0
    fi
    echo "[trending] Fetch failed (exit $exit_code)" >&2
    exit 1
}
echo "[trending] Step 0 complete."

# ── Step 1: Enrich Repos via Claude CLI (Python) ────────────────────
echo "[trending] Step 1: Enriching repos..."
ENRICHED=$(echo "$FETCHED" | python3 "$SCRIPT_DIR/enrich.py") || {
    echo "[trending] ERROR: Step 1 (enrichment) failed." >&2
    exit 1
}

if ! echo "$ENRICHED" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'enriched' in d" 2>/dev/null; then
    echo "[trending] ERROR: Step 1 did not return valid enriched JSON." >&2
    exit 1
fi
echo "[trending] Step 1 complete: $(echo "$ENRICHED" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['enriched']),'repos enriched')")"

# ── Step 2: Assemble & Write Reports (Python templating) ────────────
echo "[trending] Step 2: Writing reports..."

TMPDIR_TRENDING=$(mktemp -d)
trap 'rm -rf "$TMPDIR_TRENDING"' EXIT
export TMPDIR_TRENDING TODAY VAULT_DIR
echo "$FETCHED" > "$TMPDIR_TRENDING/fetched.json"
echo "$ENRICHED" > "$TMPDIR_TRENDING/enriched.json"

python3 "$SCRIPT_DIR/write_reports.py"
echo "[trending] Step 2 complete."

# ── Step 3: Archive old reports ─────────────────────────────────────
echo "[trending] Step 3: Archiving reports older than 14 days..."
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
            echo "[trending]   Archived: $fname"
        fi
    fi
done

echo "[trending] Done!"

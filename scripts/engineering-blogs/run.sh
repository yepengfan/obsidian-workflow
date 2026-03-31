#!/usr/bin/env bash
# Engineering Blogs — hybrid Python + Claude Code pipeline.
#
# Step 0: Python fetches engineering blog RSS feeds → JSON
# Step 1: Python enriches articles via Claude CLI → JSON
# Step 2: Python assembles & writes Obsidian reports
# Step 3: Bash archives old reports (>14 days)
#
# No external Python dependencies — stdlib only.
set -euo pipefail

# Ensure common tool paths are available (Obsidian Shell Commands has a minimal PATH)
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

# Log stderr to file (tee preserves console output for interactive callers)
LOG_FILE="$(cd "$(dirname "$0")" && pwd)/engineering-blogs.log"
exec 2> >(tee -a "$LOG_FILE" >&2)
echo "[eng-blogs] ── Run started at $(date '+%Y-%m-%d %H:%M:%S') ──" >&2

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
FEED_DIR="$VAULT_DIR/Feeds/Engineering-Blogs"
REPORT_FILE="$FEED_DIR/$TODAY.md"

# ── Module toggle guard ─────────────────────────────────────────────
MODULE_FILE="$VAULT_DIR/system/modules/feeds-engineering-blogs/module.md"
if [ -f "$MODULE_FILE" ] && grep -q "enabled: false" "$MODULE_FILE"; then
    echo "[eng-blogs] Module feeds-engineering-blogs is disabled, skipping." >&2
    exit 0
fi

# ── Pre-flight checks ───────────────────────────────────────────────
if [ -f "$REPORT_FILE" ]; then
    echo "[eng-blogs] Today's report already exists: $REPORT_FILE"
    exit 0
fi

if ! command -v claude &>/dev/null; then
    echo "[eng-blogs] ERROR: 'claude' CLI not found on PATH." >&2
    exit 1
fi

# ── Step 0: Fetch Articles (Python) ─────────────────────────────────
echo "[eng-blogs] Step 0: Fetching engineering blog articles..."
FETCHED=$(python3 "$SCRIPT_DIR/fetch.py" --vault-path "$VAULT_DIR") || {
    exit_code=$?
    if [ $exit_code -eq 2 ]; then
        echo "[eng-blogs] Report already exists (fetcher check). Skipping."
        exit 0
    fi
    echo "[eng-blogs] Fetch failed (exit $exit_code)" >&2
    exit 1
}
echo "[eng-blogs] Step 0 complete."

# ── Step 1: Enrich Articles via Claude CLI (Python) ─────────────────
echo "[eng-blogs] Step 1: Enriching articles..."
ENRICHED=$(echo "$FETCHED" | python3 "$SCRIPT_DIR/enrich.py") || {
    echo "[eng-blogs] ERROR: Step 1 (enrichment) failed." >&2
    exit 1
}

if ! echo "$ENRICHED" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'enriched' in d" 2>/dev/null; then
    echo "[eng-blogs] ERROR: Step 1 did not return valid enriched JSON." >&2
    exit 1
fi
echo "[eng-blogs] Step 1 complete: $(echo "$ENRICHED" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['enriched']),'articles enriched')")"

# ── Step 2: Assemble & Write Reports (Python) ───────────────────────
echo "[eng-blogs] Step 2: Writing reports..."

TMPDIR_ENGBLOGS=$(mktemp -d)
trap 'rm -rf "$TMPDIR_ENGBLOGS"' EXIT
export TMPDIR_ENGBLOGS TODAY VAULT_DIR
echo "$FETCHED" > "$TMPDIR_ENGBLOGS/fetched.json"
echo "$ENRICHED" > "$TMPDIR_ENGBLOGS/enriched.json"

python3 "$SCRIPT_DIR/write_reports.py"
echo "[eng-blogs] Step 2 complete."

# ── Step 3: Archive old reports ─────────────────────────────────────
echo "[eng-blogs] Step 3: Archiving reports older than 14 days..."
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
            echo "[eng-blogs]   Archived: $fname"
        fi
    fi
done

echo "[eng-blogs] Done!"

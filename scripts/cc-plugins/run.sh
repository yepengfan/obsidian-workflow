#!/usr/bin/env bash
# Claude Code Plugins — weekly discovery + version tracking pipeline.
#
# Step 0: Python fetches plugin repos from GitHub + npm → JSON
# Step 1: Python enriches via Claude Haiku (classify, score, summarize) → JSON
# Step 2: Python assembles Obsidian weekly reports + updates state
# Step 3: Bash archives old reports (>14 weeks)
#
# Cadence: weekly (manual via /feeds/cc-plugins)
set -euo pipefail

# Ensure common tool paths are available (Obsidian Shell Commands has a minimal PATH)
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

# Log stderr to file (tee preserves console output for interactive callers)
LOG_FILE="$(cd "$(dirname "$0")" && pwd)/cc-plugins.log"
exec 2> >(tee -a "$LOG_FILE" >&2)
echo "[cc-plugins] ── Run started at $(date '+%Y-%m-%d %H:%M:%S') ──" >&2

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
WEEK=$(date +%G-W%V)
FEED_DIR="$VAULT_DIR/Feeds/CC-Plugins"
REPORT_FILE="$FEED_DIR/$WEEK.md"

# ── Module toggle guard ─────────────────────────────────────────────
MODULE_FILE="$VAULT_DIR/system/modules/feeds-cc-plugins/module.md"
if [ -f "$MODULE_FILE" ] && grep -q "enabled: false" "$MODULE_FILE"; then
    echo "[cc-plugins] Module feeds-cc-plugins is disabled, skipping." >&2
    exit 0
fi

# ── Pre-flight checks ───────────────────────────────────────────────
if [ -f "$REPORT_FILE" ]; then
    echo "[cc-plugins] This week's report already exists: $REPORT_FILE"
    exit 2
fi

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "[cc-plugins] ERROR: ANTHROPIC_API_KEY not set. Required for enrichment." >&2
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    echo "[cc-plugins] ERROR: 'python3' not found on PATH." >&2
    exit 1
fi

if [ -z "${GITHUB_TOKEN:-}" ]; then
    echo "[cc-plugins] Warning: GITHUB_TOKEN not set. Unauthenticated rate limit is 10 req/min." >&2
    echo "[cc-plugins]   Set GITHUB_TOKEN for reliability: export GITHUB_TOKEN=ghp_..." >&2
fi

# ── Step 0: Fetch Plugin Repos (Python) ─────────────────────────────
echo "[cc-plugins] Step 0: Fetching plugin repos from GitHub + npm..."
FETCHED=$(python3 "$SCRIPT_DIR/fetch.py" --vault-path "$VAULT_DIR") || {
    exit_code=$?
    if [ $exit_code -eq 2 ]; then
        echo "[cc-plugins] Report already exists (fetcher check). Skipping."
        exit 2
    fi
    echo "[cc-plugins] Fetch failed (exit $exit_code)" >&2
    exit 1
}
echo "[cc-plugins] Step 0 complete."

# ── Step 1: Enrich via Anthropic API (Python) ───────────────────────
echo "[cc-plugins] Step 1: Classifying and enriching plugins..."
ENRICHED=$(echo "$FETCHED" | python3 "$SCRIPT_DIR/enrich.py") || {
    echo "[cc-plugins] ERROR: Step 1 (enrichment) failed." >&2
    exit 1
}

if ! echo "$ENRICHED" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'enriched' in d" 2>/dev/null; then
    echo "[cc-plugins] ERROR: Step 1 did not return valid enriched JSON." >&2
    exit 1
fi
echo "[cc-plugins] Step 1 complete: $(echo "$ENRICHED" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['enriched']),'plugins classified')")"

# ── Step 2: Assemble & Write Reports (Python) ───────────────────────
echo "[cc-plugins] Step 2: Writing weekly reports..."

TMPDIR_CC_PLUGINS=$(mktemp -d)
trap 'rm -rf "$TMPDIR_CC_PLUGINS"' EXIT
export TMPDIR_CC_PLUGINS WEEK TODAY VAULT_DIR
echo "$FETCHED" > "$TMPDIR_CC_PLUGINS/fetched.json"
echo "$ENRICHED" > "$TMPDIR_CC_PLUGINS/enriched.json"

python3 "$SCRIPT_DIR/write_reports.py"
echo "[cc-plugins] Step 2 complete."

# ── Step 3: Archive old reports ──────────────────────────────────────
echo "[cc-plugins] Step 3: Archiving reports older than 14 weeks..."
mkdir -p "$FEED_DIR/archive"

CURRENT_WEEK_NUM=$(date +%V)
CURRENT_YEAR=$(date +%G)

find "$FEED_DIR" -maxdepth 1 -name "*.md" -not -name "Dashboard.md" | while read -r f; do
    fname=$(basename "$f")
    # Extract week from filename (e.g., 2026-W14.md → 2026, 14)
    if [[ "$fname" =~ ^([0-9]{4})-W([0-9]{2})(-en)?\.md$ ]]; then
        file_year="${BASH_REMATCH[1]}"
        file_week="${BASH_REMATCH[2]}"
        # Calculate week difference (approximate)
        week_diff=$(( (CURRENT_YEAR - file_year) * 52 + (10#$CURRENT_WEEK_NUM - 10#$file_week) ))
        if [ "$week_diff" -gt 14 ]; then
            mv "$f" "$FEED_DIR/archive/"
            echo "[cc-plugins]   Archived: $fname"
        fi
    fi
done

echo "[cc-plugins] Done!"

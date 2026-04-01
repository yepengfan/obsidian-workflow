#!/usr/bin/env bash
# Podcast Pipeline — hybrid Python + Whisper + Claude Code pipeline.
#
# Step 0: Python fetches RSS feeds + downloads new episode audio → JSON
# Step 1: Python transcribes audio locally with mlx-whisper → JSON + .srt
# Step 2: Python scores + summarizes via Claude CLI → JSON
# Step 3: Python generates Obsidian episode notes + recommendation page
# Step 4: Python runs lifecycle management (archive + cleanup)
#
# Designed for manual execution via `/feeds/podcast` slash command.
set -euo pipefail

# Ensure common tool paths are available (Obsidian Shell Commands has a minimal PATH)
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

# Log stderr to file (tee preserves console output for interactive callers)
LOG_FILE="$(cd "$(dirname "$0")" && pwd)/podcast.log"
exec 2> >(tee -a "$LOG_FILE" >&2)
echo "[podcast] ── Run started at $(date '+%Y-%m-%d %H:%M:%S') ──" >&2

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
PYTHON="$SCRIPT_DIR/.venv/bin/python"

# ── Module toggle guard ─────────────────────────────────────────────
MODULE_FILE="$VAULT_DIR/system/modules/feeds-podcast/module.md"
if [ -f "$MODULE_FILE" ] && grep -q "enabled: false" "$MODULE_FILE"; then
    echo "[podcast] Module feeds-podcast is disabled, skipping." >&2
    exit 0
fi

# ── Pre-flight checks ───────────────────────────────────────────────
if ! command -v claude &>/dev/null; then
    echo "[podcast] ERROR: 'claude' CLI not found on PATH." >&2
    exit 1
fi

if [ ! -f "$PYTHON" ]; then
    echo "[podcast] ERROR: Python venv not found. Run 'bash scripts/podcast/setup.sh' first." >&2
    exit 1
fi

FEEDS_MD="$VAULT_DIR/Podcasts/Feeds.md"
FEEDS_TXT="$SCRIPT_DIR/feeds.txt"
if [ ! -f "$FEEDS_MD" ] && [ ! -f "$FEEDS_TXT" ]; then
    echo "[podcast] ERROR: No feed config found. Create Podcasts/Feeds.md or scripts/podcast/feeds.txt" >&2
    exit 1
fi

# ── Pass through extra args (e.g. --limit 5) ──────────────────────
EXTRA_ARGS=("$@")

# ── Step 0: Fetch + Download (Python) ──────────────────────────────
echo "[podcast] Step 0: Fetching RSS feeds + downloading audio..."
EPISODES=$("$PYTHON" "$SCRIPT_DIR/fetch.py" --vault-path "$VAULT_DIR" "${EXTRA_ARGS[@]}") || {
    exit_code=$?
    echo "[podcast] Fetch failed (exit $exit_code)" >&2
    exit 1
}

# Check if there are new episodes to process
NEW_COUNT=$(echo "$EPISODES" | "$PYTHON" -c "import sys,json; d=json.load(sys.stdin); print(d.get('stats',{}).get('new_episodes',0))" 2>/dev/null || echo "0")
if [ "$NEW_COUNT" = "0" ]; then
    echo "[podcast] No new episodes to process. All feeds up to date."
    # Still run lifecycle even if no new episodes
    echo "[podcast] Step 4: Running lifecycle management..."
    "$PYTHON" "$SCRIPT_DIR/lifecycle.py" --vault-path "$VAULT_DIR" || true
    echo "[podcast] Done!"
    exit 0
fi
echo "[podcast] Step 0 complete: $NEW_COUNT new episodes found."

# ── Step 1: Transcribe (Python + mlx-whisper) ─────────────────────
echo "[podcast] Step 1: Transcribing audio with Whisper..."
TRANSCRIBED=$(echo "$EPISODES" | "$PYTHON" "$SCRIPT_DIR/transcribe.py") || {
    echo "[podcast] ERROR: Step 1 (transcription) failed." >&2
    exit 1
}

if ! echo "$TRANSCRIBED" | "$PYTHON" -c "import sys,json; d=json.load(sys.stdin); assert 'episodes' in d" 2>/dev/null; then
    echo "[podcast] ERROR: Step 1 did not return valid JSON." >&2
    exit 1
fi
echo "[podcast] Step 1 complete."

# ── Step 2: Enrich — Score + Summarize (Python + Claude CLI) ──────
echo "[podcast] Step 2: Scoring + summarizing with Claude..."
ENRICHED=$(echo "$TRANSCRIBED" | "$PYTHON" "$SCRIPT_DIR/enrich.py") || {
    echo "[podcast] ERROR: Step 2 (enrichment) failed." >&2
    exit 1
}

if ! echo "$ENRICHED" | "$PYTHON" -c "import sys,json; d=json.load(sys.stdin); assert 'episodes' in d" 2>/dev/null; then
    echo "[podcast] ERROR: Step 2 did not return valid enriched JSON." >&2
    exit 1
fi
echo "[podcast] Step 2 complete."

# ── Step 3: Write Notes (Python templating) ────────────────────────
echo "[podcast] Step 3: Generating Obsidian notes..."

TMPDIR_PODCAST=$(mktemp -d)
trap 'rm -rf "$TMPDIR_PODCAST"' EXIT
export TMPDIR_PODCAST TODAY VAULT_DIR
echo "$ENRICHED" > "$TMPDIR_PODCAST/enriched.json"

"$PYTHON" "$SCRIPT_DIR/write_notes.py" || {
    echo "[podcast] ERROR: Step 3 (note generation) failed." >&2
    exit 1
}
echo "[podcast] Step 3 complete."

# ── Step 4: Lifecycle Management ───────────────────────────────────
echo "[podcast] Step 4: Running lifecycle management..."
"$PYTHON" "$SCRIPT_DIR/lifecycle.py" --vault-path "$VAULT_DIR" || {
    echo "[podcast] WARNING: Lifecycle management encountered errors (non-fatal)." >&2
}

echo "[podcast] Done! Processed $NEW_COUNT new episodes."

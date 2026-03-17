#!/usr/bin/env bash
# AI Daily Digest — hybrid Python + Claude Code pipeline (phased).
#
# Step 0: Python fetches & deduplicates RSS feeds → JSON
# Step 1: Claude (haiku) scores & selects top 15 → JSON
# Step 2: Claude (haiku) summarizes bilingually → JSON
# Step 3: Python assembles & writes Obsidian reports (~1s)
# Step 4: Bash archives old reports (>14 days)
#
# Designed for unattended background execution via Obsidian Shell Commands.
set -euo pipefail

# Ensure common tool paths are available (Obsidian Shell Commands has a minimal PATH)
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
TODAY=$(date +%Y-%m-%d)
FEED_DIR="$VAULT_DIR/Feeds/AI-Daily"
DIGEST_FILE="$FEED_DIR/$TODAY.md"

CLAUDE_COMMON="--permission-mode bypassPermissions --no-session-persistence"

# Helper: strip markdown fences and extract valid JSON from Claude output.
# Handles: code fences, leading/trailing text, unescaped quotes in strings.
extract_json() {
    python3 -c "
import sys, re, json

raw = sys.stdin.read().strip()

# Remove markdown code fences
raw = re.sub(r'^\s*\`\`\`(?:json)?\s*\n', '', raw)
raw = re.sub(r'\n\s*\`\`\`\s*$', '', raw)

# Find the JSON object (first { to last })
start = raw.find('{')
end = raw.rfind('}')
if start == -1 or end == -1:
    print(raw, file=sys.stderr)
    sys.exit(1)
raw = raw[start:end+1]

# Try parsing directly
try:
    obj = json.loads(raw)
    json.dump(obj, sys.stdout, ensure_ascii=False)
    sys.exit(0)
except json.JSONDecodeError:
    pass

# Repair: fix unescaped double-quotes inside JSON string values.
# Strategy: walk character-by-character tracking whether we're inside a string.
chars = list(raw)
i = 0
in_string = False
result = []
while i < len(chars):
    c = chars[i]
    if c == '\\\\' and in_string:
        result.append(c)
        i += 1
        if i < len(chars):
            result.append(chars[i])
        i += 1
        continue
    if c == '\"':
        if not in_string:
            in_string = True
            result.append(c)
        else:
            # Look ahead: if next non-whitespace is : , ] } or end, this closes the string
            rest = raw[i+1:].lstrip()
            if not rest or rest[0] in ':,]}':
                in_string = False
                result.append(c)
            else:
                # Unescaped interior quote — escape it
                result.append('\\\\\"')
        i += 1
        continue
    result.append(c)
    i += 1

repaired = ''.join(result)
try:
    obj = json.loads(repaired)
    json.dump(obj, sys.stdout, ensure_ascii=False)
except json.JSONDecodeError as e:
    print(f'JSON repair failed: {e}', file=sys.stderr)
    print(repaired[:500], file=sys.stderr)
    sys.exit(1)
"
}

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
ARTICLES=$("$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/fetch.py" --vault-path "$VAULT_DIR" 2>/dev/null) || {
    exit_code=$?
    if [ $exit_code -eq 2 ]; then
        echo "[digest] Digest already exists (fetcher check). Skipping."
        exit 0
    fi
    echo "[digest] Fetch failed (exit $exit_code)" >&2
    exit 1
}
echo "[digest] Step 0 complete."

# ── Step 1: Score & Select top 15 (Haiku, stdout JSON) ──────────────
echo "[digest] Step 1: Scoring articles..."
SCORED=$(echo "$ARTICLES" | claude -p \
    "Score and rank the articles from the JSON on stdin. Output ONLY valid JSON." \
    --system-prompt "$(cat "$PROMPTS_DIR/score.md")" \
    --model haiku \
    --max-budget-usd 0.25 \
    $CLAUDE_COMMON | extract_json)

# Validate we got JSON back
if ! echo "$SCORED" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'top_articles' in d" 2>/dev/null; then
    echo "[digest] ERROR: Phase 1 did not return valid scored JSON." >&2
    echo "[digest] Output: $(echo "$SCORED" | head -5)" >&2
    exit 1
fi
echo "[digest] Step 1 complete: $(echo "$SCORED" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['top_articles']),'articles selected')")"

# ── Step 2: Bilingual Summarization (Haiku, stdout JSON) ────────────
echo "[digest] Step 2: Summarizing articles..."
SUMMARIES=$(echo "$SCORED" | claude -p \
    "Summarize the ranked articles from the JSON on stdin. Output ONLY the raw JSON object — no markdown fences, no commentary." \
    --system-prompt "$(cat "$PROMPTS_DIR/summarize.md")" \
    --model haiku \
    --max-budget-usd 0.25 \
    $CLAUDE_COMMON | extract_json)

# Validate summaries JSON
if ! echo "$SUMMARIES" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'summaries' in d and 'trend_zh' in d" 2>/dev/null; then
    echo "[digest] ERROR: Phase 2 did not return valid summaries JSON." >&2
    echo "[digest] Output: $(echo "$SUMMARIES" | head -5)" >&2
    exit 1
fi
echo "[digest] Step 2 complete: $(echo "$SUMMARIES" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['summaries']),'summaries generated')")"

# ── Step 3: Assemble & Write Reports (Python templating) ────────────
echo "[digest] Step 3: Writing reports..."

# Save phase outputs for the Python assembler
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
    # Extract date from filename (handles both YYYY-MM-DD.md and YYYY-MM-DD-en.md)
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

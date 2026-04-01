#!/usr/bin/env bash
# Podcast Pipeline — First-time setup script.
#
# Creates Python virtual environment and installs dependencies.
# Run this once before using /feeds/podcast.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🎧 Podcast Pipeline Setup"
echo "========================="
echo ""

# ── Python venv ─────────────────────────────────────────────────────
echo "1. Creating Python virtual environment..."
if [ -d "$SCRIPT_DIR/.venv" ]; then
    echo "   ✅ .venv already exists, skipping."
else
    python3 -m venv "$SCRIPT_DIR/.venv"
    echo "   ✅ Created .venv"
fi

PYTHON="$SCRIPT_DIR/.venv/bin/python"
PIP="$SCRIPT_DIR/.venv/bin/pip"

# ── Install dependencies ────────────────────────────────────────────
echo ""
echo "2. Installing Python dependencies..."
"$PIP" install --quiet --upgrade pip
"$PIP" install --quiet mlx-whisper feedparser
echo "   ✅ Installed: mlx-whisper, feedparser"

# ── Check ffmpeg ────────────────────────────────────────────────────
echo ""
echo "3. Checking ffmpeg..."
if command -v ffmpeg &>/dev/null; then
    echo "   ✅ ffmpeg found: $(ffmpeg -version 2>&1 | head -1)"
else
    echo "   ⚠️  ffmpeg not found. Some audio formats may not work."
    echo "      Install with: brew install ffmpeg"
fi

# ── Check Claude CLI ────────────────────────────────────────────────
echo ""
echo "4. Checking Claude CLI..."
if command -v claude &>/dev/null; then
    echo "   ✅ claude CLI found"
else
    echo "   ❌ claude CLI not found on PATH."
    echo "      The pipeline needs Claude CLI for scoring and summarization."
    exit 1
fi

# ── Check ANTHROPIC_API_KEY ─────────────────────────────────────────
echo ""
echo "5. Checking ANTHROPIC_API_KEY..."
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    echo "   ✅ ANTHROPIC_API_KEY is set"
else
    echo "   ⚠️  ANTHROPIC_API_KEY not set in current shell."
    echo "      Make sure it's available when running the pipeline."
fi

# ── Pre-download Whisper model ──────────────────────────────────────
echo ""
echo "6. Pre-downloading Whisper model (this may take a few minutes on first run)..."
"$PYTHON" -c "
try:
    from huggingface_hub import snapshot_download
    snapshot_download('mlx-community/whisper-large-v3-turbo', local_files_only=False)
    print('   ✅ Model downloaded/cached')
except Exception as e:
    print(f'   ⚠️  Model will be downloaded on first transcription run: {e}')
"

# ── Summary ─────────────────────────────────────────────────────────
echo ""
echo "========================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Add RSS feeds to: scripts/podcast/feeds.txt"
echo "  2. Install Media Extended plugin in Obsidian (for audio + subtitle sync)"
echo "  3. Run /feeds/podcast to process your first episodes"

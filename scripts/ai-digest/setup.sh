#!/usr/bin/env bash
# Bootstrap the AI Daily Digest environment.
# Usage: cd scripts/ai-digest && bash setup.sh

set -euo pipefail

cd "$(dirname "$0")"

# Check for claude CLI
if ! command -v claude &>/dev/null; then
    echo "[setup] WARNING: 'claude' CLI not found on PATH."
    echo "  Install it from https://docs.anthropic.com/en/docs/claude-code"
    echo "  The pipeline requires 'claude' for scoring and summarization."
fi

echo "[setup] Creating virtual environment..."
python3 -m venv .venv

echo "[setup] Installing dependencies..."
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -e .

echo "[setup] Done!  Run with:"
echo "  bash scripts/ai-digest/run.sh"

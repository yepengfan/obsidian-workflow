#!/usr/bin/env bash
# Bootstrap the AI Daily Digest environment.
# Usage: cd scripts/ai-digest && bash setup.sh

set -euo pipefail

cd "$(dirname "$0")"

echo "[setup] Creating virtual environment..."
python3 -m venv .venv

echo "[setup] Installing dependencies..."
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -e .

echo "[setup] Done!  Run with:"
echo "  cd scripts/ai-digest && .venv/bin/python -m digest"

#!/usr/bin/env bash
# Feed Orchestrator — env wrapper for Obsidian Shell Commands.
#
# Sources login shell env (ANTHROPIC_API_KEY, GITHUB_TOKEN, etc.) then
# execs the orchestrator via its own venv Python.  Obsidian's stripped
# environment doesn't carry these vars, so we load them here.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SHARED_DIR="$(cd "$SCRIPT_DIR/../shared" && pwd)"

# Extract only export lines from zshrc (sourcing full zshrc hangs in non-interactive bash)
if [ -f "$HOME/.zshrc" ]; then
  eval "$(grep '^export ' "$HOME/.zshrc" 2>/dev/null)" 2>/dev/null || true
fi

# Fallback: vault-level .env file
[ -f "$VAULT_DIR/.env" ] && set -a && source "$VAULT_DIR/.env" && set +a || true

# Augment PATH for Cursor CLI discovery (Obsidian strips ~/.local/bin, etc.)
# shellcheck source=../shared/cursor-paths.sh
source "$SHARED_DIR/cursor-paths.sh"
export PATH="$(cursor_augment_path)"

# Default LLM backend when unset: prefer credentials over hardcoded cursor
if [ -z "${FEED_LLM_BACKEND:-}" ]; then
  if [ -n "${ANTHROPIC_API_KEY:-}" ] || [ -n "${ANTHROPIC_AUTH_TOKEN:-}" ]; then
    export FEED_LLM_BACKEND=anthropic
  elif cursor_cli_available; then
    export FEED_LLM_BACKEND=cursor
  fi
  # else: leave unset — orchestrator validates credentials at enrich time
fi
export FEED_CURSOR_MODEL="${FEED_CURSOR_MODEL:-composer-2.5}"

# Exec orchestrator with venv Python (absolute path — no PATH dependency)
exec "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/main.py" --vault-path "$VAULT_DIR" "$@"

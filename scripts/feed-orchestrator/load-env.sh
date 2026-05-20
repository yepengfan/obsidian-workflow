#!/usr/bin/env bash
# Feed Orchestrator — env wrapper for Obsidian Shell Commands.
#
# Sources login shell env (ANTHROPIC_API_KEY, GITHUB_TOKEN, etc.) then
# execs the orchestrator via its own venv Python.  Obsidian's stripped
# environment doesn't carry these vars, so we load them here.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source login shell env
[ -f "$HOME/.zshrc" ] && source "$HOME/.zshrc" 2>/dev/null || true

# Fallback: vault-level .env file
[ -f "$VAULT_DIR/.env" ] && set -a && source "$VAULT_DIR/.env" && set +a || true

# Exec orchestrator with venv Python (absolute path — no PATH dependency)
exec "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/main.py" --vault-path "$VAULT_DIR" "$@"

"""Cursor CLI PATH augmentation and binary discovery.

Shared by load-env.sh (via cursor-paths.sh mirror) and Python feed runners.
"""

from __future__ import annotations

import os
import shutil

# Keep in sync with scripts/shared/cursor-paths.sh
CURSOR_CLI_SEARCH_DIRS: tuple[str, ...] = (
    "~/.local/bin",
    "~/.cursor/bin",
    "~/bin",
    "~/.npm-global/bin",
    "/usr/local/bin",
    "/opt/homebrew/bin",
)


def _expand(path: str) -> str:
    return os.path.expanduser(path)


def cursor_cli_search_dirs() -> list[str]:
    return [_expand(path) for path in CURSOR_CLI_SEARCH_DIRS]


def augmented_path(path: str | None = None) -> str:
    """Return PATH with known Cursor CLI install dirs prepended."""
    extra = ":".join(cursor_cli_search_dirs())
    current = path if path is not None else os.environ.get("PATH", "")
    return f"{extra}:{current}" if current else extra


def find_agent_binary(path: str | None = None) -> str | None:
    """Resolve agent or cursor-agent using augmented PATH."""
    search_path = augmented_path(path)
    for name in ("agent", "cursor-agent"):
        found = shutil.which(name, path=search_path)
        if found:
            return found
    return None


def cursor_cli_available(path: str | None = None) -> bool:
    return find_agent_binary(path) is not None


def resolve_default_feed_backend() -> str:
    """Infer FEED_LLM_BACKEND when unset (matches load-env.sh).

    Prefers Cursor CLI (subscription auth, doesn't expire) over Anthropic
    credentials, which are often a proxy token that can silently expire.
    """
    if cursor_cli_available():
        return "cursor"
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return "anthropic"
    raise RuntimeError(
        "No LLM backend available. Install Cursor CLI (agent on PATH), "
        "or set ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN."
    )

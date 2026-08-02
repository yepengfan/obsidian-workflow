"""Pluggable LLM backend for feed enrichment.

Switch backends via ``FEED_LLM_BACKEND``:
  - ``anthropic`` — Anthropic SDK Haiku (default when API key/token is set)
  - ``cursor`` — Cursor CLI ``agent -p`` (default when no Anthropic creds but CLI on PATH)
"""

from __future__ import annotations

import asyncio
import os
import sys

import anthropic

from shared.cursor_runner import resolve_cursor_model, run_cursor

BACKEND_CURSOR = "cursor"
BACKEND_ANTHROPIC = "anthropic"


def _resolve_default_backend() -> str:
    """Pick backend from available credentials when FEED_LLM_BACKEND is unset."""
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return BACKEND_ANTHROPIC
    import shutil

    if shutil.which("agent") or shutil.which("cursor-agent"):
        return BACKEND_CURSOR
    return BACKEND_ANTHROPIC

# Anthropic model auto-detection (proxy needs "anthropic." prefix)
_MODEL_DIRECT = "claude-sonnet-4-6-20250514"
_MODEL_PROXY = "anthropic.claude-4-6-sonnet"

_anthropic_client: anthropic.AsyncAnthropic | None = None
_haiku_model: str | None = os.environ.get("FEED_HAIKU_MODEL")


def get_backend() -> str:
    """Return normalized backend name. Infers from credentials when unset."""
    raw = os.environ.get("FEED_LLM_BACKEND", "").strip().lower()
    backend = _resolve_default_backend() if not raw else raw
    if backend not in (BACKEND_CURSOR, BACKEND_ANTHROPIC):
        raise ValueError(
            f"Unknown FEED_LLM_BACKEND={backend!r}. "
            f"Valid: {BACKEND_CURSOR}, {BACKEND_ANTHROPIC}"
        )
    return backend


def uses_cursor_consolidation() -> bool:
    """Cursor backend uses fewer, larger LLM calls (e.g. ai-digest score-all)."""
    return get_backend() == BACKEND_CURSOR


def validate_backend_credentials() -> None:
    """Fail fast if the selected backend lacks required credentials."""
    backend = get_backend()
    if backend == BACKEND_ANTHROPIC:
        if not (
            os.environ.get("ANTHROPIC_API_KEY")
            or os.environ.get("ANTHROPIC_AUTH_TOKEN")
        ):
            raise RuntimeError(
                "FEED_LLM_BACKEND=anthropic requires ANTHROPIC_API_KEY "
                "or ANTHROPIC_AUTH_TOKEN"
            )
    elif backend == BACKEND_CURSOR:
        import shutil

        if not (shutil.which("agent") or shutil.which("cursor-agent")):
            raise RuntimeError(
                "FEED_LLM_BACKEND=cursor requires Cursor CLI (agent) on PATH. "
                "Install: curl https://cursor.com/install -fsS | bash"
            )


def _get_anthropic_client() -> anthropic.AsyncAnthropic:
    global _anthropic_client, _haiku_model
    if _anthropic_client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
        if api_key:
            _anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)
            if _haiku_model is None:
                _haiku_model = _MODEL_DIRECT
        elif auth_token:
            _anthropic_client = anthropic.AsyncAnthropic(auth_token=auth_token)
            if _haiku_model is None:
                _haiku_model = _MODEL_PROXY
        else:
            raise RuntimeError(
                "Neither ANTHROPIC_API_KEY nor ANTHROPIC_AUTH_TOKEN is set."
            )
        print(f"[anthropic] Using model: {_haiku_model}", file=sys.stderr)
    return _anthropic_client


async def _call_anthropic(system: str, user: str, retries: int = 3) -> str:
    client = _get_anthropic_client()
    for attempt in range(retries):
        try:
            response = await client.messages.create(
                model=_haiku_model,
                max_tokens=16384,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            text = response.content[0].text if response.content else ""
            if not text.strip():
                raise ValueError("Empty response from Haiku")
            return text
        except (anthropic.RateLimitError, anthropic.APIConnectionError) as e:
            if attempt < retries - 1:
                wait = 2 ** (attempt + 1)
                print(
                    f"[anthropic] Retry {attempt + 1}/{retries} after {wait}s: {e}",
                    file=sys.stderr,
                )
                await asyncio.sleep(wait)
            else:
                raise
    return ""  # unreachable


async def call_llm(
    system: str,
    user: str,
    *,
    task: str = "default",
    retries: int = 3,
) -> str:
    """Call the configured LLM backend with system + user content."""
    backend = get_backend()
    if backend == BACKEND_CURSOR:
        model = resolve_cursor_model(task)
        return await run_cursor(
            system,
            user,
            model=model,
            retries=retries,
        )
    return await _call_anthropic(system, user, retries=retries)


# Re-export for startup logging
def backend_summary() -> str:
    backend = get_backend()
    if backend == BACKEND_CURSOR:
        return f"cursor (model={resolve_cursor_model('default')})"
    return f"anthropic (model={_haiku_model or 'auto'})"

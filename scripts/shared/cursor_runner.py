"""Shared async Cursor CLI subprocess runner for feed enrichment.

Invokes ``agent -p`` in read-only ask mode for structured JSON tasks.
Uses Cursor subscription auth (``agent login`` session or ``CURSOR_API_KEY``).
"""

from __future__ import annotations

import asyncio
import os
import shutil
import sys


DEFAULT_MODEL = "composer-2.5"
DEFAULT_TIMEOUT = 600.0

AGENT_BIN = shutil.which("agent") or shutil.which("cursor-agent") or "agent"

USER_INSTRUCTION = (
    "Process the input according to your system instructions. "
    "Output ONLY valid JSON — no markdown fences, no explanation."
)


def _build_prompt(system: str, user: str) -> str:
    """Combine system + user into a single -p argument.

    Cursor CLI does not reliably consume stdin when spawned as a subprocess;
    the full prompt must be passed via ``-p``.
    """
    return (
        f"{USER_INSTRUCTION}\n\n"
        f"{system.rstrip()}\n\n"
        f"---\nINPUT:\n{user}"
    )


def _agent_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = (
        f"{os.path.expanduser('~')}/.local/bin:"
        f"{os.path.expanduser('~')}/.npm-global/bin:"
        f"/usr/local/bin:/opt/homebrew/bin:"
        f"{env.get('PATH', '')}"
    )
    return env


def resolve_cursor_model(task: str = "default") -> str:
    """Resolve model for a task. Task-specific env overrides global default."""
    task_key = f"FEED_CURSOR_MODEL_{task.upper()}"
    return (
        os.environ.get(task_key)
        or os.environ.get("FEED_CURSOR_MODEL")
        or DEFAULT_MODEL
    )


async def run_cursor(
    system: str,
    user: str,
    *,
    model: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    retries: int = 3,
) -> str:
    """Call Cursor agent with system + user content, return stdout text.

    The full system prompt and user payload are combined in the agent prompt
    body (Cursor CLI does not support a separate --system-prompt flag like
    ``claude -p``).
    """
    model = model or resolve_cursor_model("default")
    full_prompt = _build_prompt(system, user)

    for attempt in range(retries):
        proc = await asyncio.create_subprocess_exec(
            AGENT_BIN,
            "-p",
            full_prompt,
            "--model",
            model,
            "--output-format",
            "text",
            "--force",
            "--mode",
            "ask",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=_agent_env(),
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            if attempt < retries - 1:
                wait = 2 ** (attempt + 1)
                print(
                    f"[cursor] Timeout, retry {attempt + 1}/{retries} after {wait}s",
                    file=sys.stderr,
                )
                await asyncio.sleep(wait)
                continue
            raise RuntimeError(f"cursor agent timed out after {timeout}s")

        if proc.returncode != 0:
            err = stderr.decode().strip()
            if attempt < retries - 1:
                wait = 2 ** (attempt + 1)
                print(
                    f"[cursor] Exit {proc.returncode}, retry {attempt + 1}/{retries} "
                    f"after {wait}s: {err[:200]}",
                    file=sys.stderr,
                )
                await asyncio.sleep(wait)
                continue
            raise RuntimeError(f"cursor agent exited {proc.returncode}: {err}")

        result = stdout.decode()
        if not result.strip():
            err = stderr.decode().strip()
            raise RuntimeError(
                f"cursor agent returned empty output (stderr: {err[:200]})"
            )

        print(f"[cursor] model={model} response_len={len(result)}", file=sys.stderr)
        return result

    raise RuntimeError("cursor agent failed after all retries")  # unreachable

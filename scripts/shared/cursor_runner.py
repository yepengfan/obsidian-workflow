"""Shared async Cursor CLI subprocess runner for feed enrichment.

Invokes ``agent -p`` in read-only ask mode for structured JSON tasks.
Uses Cursor subscription auth (``agent login`` session or ``CURSOR_API_KEY``).
"""

from __future__ import annotations

import asyncio
import os
import sys

from shared.cursor_paths import augmented_path, find_agent_binary

DEFAULT_MODEL = "composer-2.5"
DEFAULT_TIMEOUT = 600.0

USER_INSTRUCTION = (
    "Process the input according to your system instructions. "
    "Output ONLY valid JSON — no markdown fences, no explanation."
)


def _build_prompt(system: str, user: str) -> str:
    """Combine system + user into the agent prompt body."""
    return (
        f"{USER_INSTRUCTION}\n\n"
        f"{system.rstrip()}\n\n"
        f"---\nINPUT:\n{user}"
    )


def _agent_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = augmented_path(env.get("PATH"))
    return env


def _agent_argv(agent_bin: str, model: str) -> list[str]:
    """Build agent CLI argv for headless feed enrichment."""
    argv = [
        agent_bin,
        "-p",
        "--trust",
        "--model",
        model,
        "--output-format",
        "text",
        "--force",
        "--mode",
        "ask",
    ]
    workspace = os.environ.get("FEED_VAULT_PATH")
    if workspace:
        argv.extend(["--workspace", workspace])
    return argv


def _agent_cwd() -> str | None:
    workspace = os.environ.get("FEED_VAULT_PATH")
    if workspace and os.path.isdir(workspace):
        return workspace
    return None


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

    Large prompts are sent on stdin to avoid OS ``execve`` argument size limits
    (``E2BIG``) when scoring full ai-digest payloads.
    """
    agent_bin = find_agent_binary()
    if not agent_bin:
        raise RuntimeError(
            "Cursor CLI (agent) not found. Install: curl https://cursor.com/install -fsS | bash"
        )

    model = model or resolve_cursor_model("default")
    full_prompt = _build_prompt(system, user)

    for attempt in range(retries):
        proc = await asyncio.create_subprocess_exec(
            *_agent_argv(agent_bin, model),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=_agent_env(),
            cwd=_agent_cwd(),
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=full_prompt.encode()),
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

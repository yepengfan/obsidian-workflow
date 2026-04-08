"""Shared async Claude CLI subprocess runner.

All feed pipelines that invoke the Claude CLI as a subprocess share the same
boilerplate: spawn ``claude -p``, pipe stdin, enforce a timeout, detect
non-zero exits, and guard against empty stdout.  This module consolidates
that logic so fixes (e.g. new error checks) are applied in one place.
"""

from __future__ import annotations

import asyncio


async def run_claude(
    user_prompt: str,
    stdin_data: str,
    *,
    system_prompt: str,
    claude_bin: str,
    claude_flags: list[str],
    semaphore: asyncio.Semaphore | None = None,
    timeout: int = 300,
) -> str:
    """Spawn ``claude -p`` as a subprocess and return its stdout.

    Parameters
    ----------
    user_prompt : str
        The ``-p`` prompt text.
    stdin_data : str
        Data piped to the process's stdin.
    system_prompt : str
        The ``--system-prompt`` value.
    claude_bin : str
        Path to the ``claude`` binary.
    claude_flags : list[str]
        Additional CLI flags (model, budget, etc.).
    semaphore : asyncio.Semaphore | None
        Optional concurrency limiter.  When provided the subprocess is only
        started after the semaphore is acquired.
    timeout : int
        Maximum seconds to wait for the process (default 300).

    Raises
    ------
    RuntimeError
        On timeout, non-zero exit, or empty stdout.
    """

    async def _invoke() -> str:
        proc = await asyncio.create_subprocess_exec(
            claude_bin, "-p", user_prompt,
            "--system-prompt", system_prompt,
            *claude_flags,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=stdin_data.encode()),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            raise RuntimeError(f"claude timed out after {timeout}s")
        if proc.returncode != 0:
            err = stderr.decode().strip()
            raise RuntimeError(f"claude exited {proc.returncode}: {err}")
        result = stdout.decode()
        if not result.strip():
            err = stderr.decode().strip()
            raise RuntimeError(f"claude returned empty output (stderr: {err[:200]})")
        return result

    if semaphore is not None:
        async with semaphore:
            return await _invoke()
    return await _invoke()

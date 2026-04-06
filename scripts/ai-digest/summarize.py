#!/usr/bin/env python3
"""Phase 2: Parallel bilingual summarization.

Replaces the single monolithic `claude -p` call with N parallel subprocess calls —
one per batch of BATCH_SIZE articles — then one sequential trend call.

Expected speedup: ~5× (from ~90s → ~20s for 15 articles in 5 parallel batches).

Input  (stdin): scored JSON  { "top_articles": [...] }
Output (stdout): summaries JSON  { "trend_zh": "...", "trend_en": "...", "summaries": [...] }
"""

import asyncio
import json
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR.parent))
from shared.json_helpers import extract_json_array, extract_json_object  # noqa: E402
SYSTEM_PROMPT = (SCRIPT_DIR / "prompts" / "summarize.md").read_text()

BATCH_SIZE = 3  # articles per parallel call (5 batches for 15 articles)
CLAUDE_BIN = shutil.which("claude") or "claude"
CLAUDE_FLAGS = [
    "--model", "haiku",
    "--max-budget-usd", "1.00",
    "--permission-mode", "bypassPermissions",
    "--no-session-persistence",
    "--bare",
]


# ── Claude subprocess runner ─────────────────────────────────────────

async def run_claude(user_prompt: str, stdin_data: str) -> str:
    """Spawn a claude -p subprocess, feed it stdin_data, return stdout."""
    proc = await asyncio.create_subprocess_exec(
        CLAUDE_BIN, "-p", user_prompt,
        "--system-prompt", SYSTEM_PROMPT,
        *CLAUDE_FLAGS,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=stdin_data.encode()),
            timeout=300,
        )
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError("claude timed out after 300s")
    if proc.returncode != 0:
        err = stderr.decode().strip()
        raise RuntimeError(f"claude exited {proc.returncode}: {err}")
    return stdout.decode()


# ── Phase tasks ──────────────────────────────────────────────────────

async def summarize_batch(articles: list, batch_idx: int, max_retries: int = 2) -> list:
    """Summarize one batch of articles in parallel. Returns summary dicts.

    Retries up to *max_retries* times when the LLM returns malformed output.
    """
    user_prompt = (
        f"Summarize these {len(articles)} articles.\n"
        "Output ONLY a JSON array — no wrapper object, no trend fields, no markdown fences.\n"
        "Each element must have exactly: rank, title, title_zh, summary_zh, reason_zh, "
        "summary_en, reason_en."
    )
    stdin_data = json.dumps(articles, ensure_ascii=False)
    last_err: Exception = RuntimeError("no attempts made")
    for attempt in range(1 + max_retries):
        try:
            raw = await run_claude(user_prompt, stdin_data)
            result = extract_json_array(raw, fallback_keys=("summaries",))
            print(f"[summarize] Batch {batch_idx + 1}: {len(result)} summaries", file=sys.stderr)
            return result
        except (ValueError, json.JSONDecodeError, RuntimeError) as e:
            last_err = e
            if attempt < max_retries:
                print(
                    f"[summarize] Batch {batch_idx + 1} attempt {attempt + 1} failed "
                    f"({e}), retrying...",
                    file=sys.stderr,
                )
    raise last_err


async def generate_trend(summaries: list, max_retries: int = 2) -> dict:
    """Generate trend_zh and trend_en after all batches complete.

    Retries up to *max_retries* times when the LLM returns malformed output.
    """
    user_prompt = (
        "Based on these article summaries, write the Today's Highlights section.\n"
        "Output ONLY a JSON object with exactly two fields: trend_zh and trend_en.\n"
        "3–5 sentences each. Synthesize macro themes — do NOT list articles one by one."
    )
    stdin_data = json.dumps(summaries, ensure_ascii=False)
    last_err: Exception = RuntimeError("no attempts made")
    for attempt in range(1 + max_retries):
        try:
            raw = await run_claude(user_prompt, stdin_data)
            return extract_json_object(raw)
        except (ValueError, json.JSONDecodeError, RuntimeError) as e:
            last_err = e
            if attempt < max_retries:
                print(
                    f"[summarize] Trend attempt {attempt + 1} failed ({e}), retrying...",
                    file=sys.stderr,
                )
    raise last_err


# ── Main ─────────────────────────────────────────────────────────────

async def main() -> None:
    scored_data = json.load(sys.stdin)
    articles = scored_data["top_articles"]

    batches = [articles[i : i + BATCH_SIZE] for i in range(0, len(articles), BATCH_SIZE)]
    print(
        f"[summarize] {len(articles)} articles → {len(batches)} parallel batches "
        f"(batch size {BATCH_SIZE})",
        file=sys.stderr,
    )

    # All batches run concurrently
    try:
        batch_results = await asyncio.gather(
            *[summarize_batch(batch, i) for i, batch in enumerate(batches)]
        )
    except Exception as e:
        print(f"[summarize] ERROR: Batch summarization failed — {e}", file=sys.stderr)
        sys.exit(1)

    # Flatten and restore original rank order
    all_summaries = [s for batch in batch_results for s in batch]
    all_summaries.sort(key=lambda x: x.get("rank", 999))

    # Trend is sequential (needs full picture)
    print("[summarize] Generating trend summary...", file=sys.stderr)
    try:
        trend = await generate_trend(all_summaries)
    except Exception as e:
        print(f"[summarize] ERROR: Trend generation failed — {e}", file=sys.stderr)
        sys.exit(1)

    result = {
        "trend_zh": trend["trend_zh"],
        "trend_en": trend["trend_en"],
        "summaries": all_summaries,
    }
    json.dump(result, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())

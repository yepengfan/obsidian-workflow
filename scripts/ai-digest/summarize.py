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
import re
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SYSTEM_PROMPT = (SCRIPT_DIR / "prompts" / "summarize.md").read_text()

BATCH_SIZE = 3  # articles per parallel call (5 batches for 15 articles)
CLAUDE_BIN = shutil.which("claude") or "claude"
CLAUDE_FLAGS = [
    "--model", "haiku",
    "--max-budget-usd", "0.25",
    "--permission-mode", "bypassPermissions",
    "--no-session-persistence",
]


# ── JSON helpers ─────────────────────────────────────────────────────

def _strip_fences(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^\s*```(?:json)?\s*\n", "", raw)
    raw = re.sub(r"\n\s*```\s*$", "", raw)
    return raw


def extract_json_array(raw: str) -> list:
    raw = _strip_fences(raw)
    start = raw.find("[")
    if start != -1:
        end = raw.rfind("]")
        if end != -1:
            return json.loads(raw[start : end + 1])
    # Fallback: might be wrapped in an object
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        obj = json.loads(raw[start : end + 1])
        if "summaries" in obj:
            return obj["summaries"]
    raise ValueError(f"No JSON array found in output:\n{raw[:400]}")


def extract_json_object(raw: str) -> dict:
    raw = _strip_fences(raw)
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in output:\n{raw[:400]}")
    return json.loads(raw[start : end + 1])


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
    stdout, stderr = await proc.communicate(input=stdin_data.encode())
    if proc.returncode != 0:
        err = stderr.decode().strip()
        raise RuntimeError(f"claude exited {proc.returncode}: {err}")
    return stdout.decode()


# ── Phase tasks ──────────────────────────────────────────────────────

async def summarize_batch(articles: list, batch_idx: int) -> list:
    """Summarize one batch of articles in parallel. Returns summary dicts."""
    user_prompt = (
        f"Summarize these {len(articles)} articles.\n"
        "Output ONLY a JSON array — no wrapper object, no trend fields, no markdown fences.\n"
        "Each element must have exactly: rank, title, title_zh, summary_zh, reason_zh, "
        "summary_en, reason_en."
    )
    raw = await run_claude(user_prompt, json.dumps(articles, ensure_ascii=False))
    result = extract_json_array(raw)
    print(f"[summarize] Batch {batch_idx + 1}: {len(result)} summaries", file=sys.stderr)
    return result


async def generate_trend(summaries: list) -> dict:
    """Generate trend_zh and trend_en after all batches complete."""
    user_prompt = (
        "Based on these article summaries, write the Today's Highlights section.\n"
        "Output ONLY a JSON object with exactly two fields: trend_zh and trend_en.\n"
        "3–5 sentences each. Synthesize macro themes — do NOT list articles one by one."
    )
    raw = await run_claude(user_prompt, json.dumps(summaries, ensure_ascii=False))
    return extract_json_object(raw)


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
    batch_results = await asyncio.gather(
        *[summarize_batch(batch, i) for i, batch in enumerate(batches)]
    )

    # Flatten and restore original rank order
    all_summaries = [s for batch in batch_results for s in batch]
    all_summaries.sort(key=lambda x: x.get("rank", 999))

    # Trend is sequential (needs full picture)
    print("[summarize] Generating trend summary...", file=sys.stderr)
    trend = await generate_trend(all_summaries)

    result = {
        "trend_zh": trend["trend_zh"],
        "trend_en": trend["trend_en"],
        "summaries": all_summaries,
    }
    json.dump(result, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())

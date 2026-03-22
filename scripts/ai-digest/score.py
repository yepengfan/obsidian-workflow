#!/usr/bin/env python3
"""Phase 1: Parallel article scoring + global ranking.

Splits raw articles into batches, scores each batch concurrently via claude -p
subprocesses, then merges and globally ranks the results in Python.

Key insight: scoring is per-article (embarrassingly parallel); ranking is global
(O(n log n) sort, trivial in Python after scores are collected).

Input  (stdin): raw articles JSON from fetch.py
Output (stdout): scored JSON  { "top_articles": [...] }  — same contract as before
"""

import asyncio
import json
import re
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SYSTEM_PROMPT = (SCRIPT_DIR / "prompts" / "score.md").read_text()

BATCH_SIZE = 4   # articles per parallel call (~4 batches for 14-16 articles)
TOP_N = 15       # articles to select after global ranking
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
    # Might be wrapped: {"top_articles": [...]}
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        obj = json.loads(raw[start : end + 1])
        if "top_articles" in obj:
            return obj["top_articles"]
    raise ValueError(f"No JSON array found:\n{raw[:400]}")


# ── Claude subprocess runner ─────────────────────────────────────────

async def run_claude(user_prompt: str, stdin_data: str) -> str:
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


# ── Scoring task ─────────────────────────────────────────────────────

async def score_batch(articles: list, batch_idx: int) -> list:
    """Score a batch of articles. Returns all articles with scores attached."""
    user_prompt = (
        f"Score ALL {len(articles)} articles in this batch using the scoring dimensions "
        "from the system prompt. "
        "Output ONLY a JSON array — one scored object per article, no selection, "
        "no wrapper object, no markdown fences. "
        "Each element must have: title, link, pub_date, description, source_name, "
        "scores (relevance, quality, timeliness, bonus, total), category, keywords."
    )
    raw = await run_claude(user_prompt, json.dumps(articles, ensure_ascii=False))
    result = extract_json_array(raw)
    print(f"[score] Batch {batch_idx + 1}: {len(result)} articles scored", file=sys.stderr)
    return result


# ── Main ─────────────────────────────────────────────────────────────

async def main() -> None:
    raw_data = json.load(sys.stdin)
    # fetch.py returns either a list directly or {"articles": [...], "stats": {...}}
    if isinstance(raw_data, list):
        articles = raw_data
        stats = {}
    else:
        articles = raw_data.get("articles", raw_data)
        stats = raw_data.get("stats", {})

    batches = [articles[i : i + BATCH_SIZE] for i in range(0, len(articles), BATCH_SIZE)]
    print(
        f"[score] {len(articles)} articles → {len(batches)} parallel batches "
        f"(batch size {BATCH_SIZE})",
        file=sys.stderr,
    )

    # All batches score concurrently
    batch_results = await asyncio.gather(
        *[score_batch(batch, i) for i, batch in enumerate(batches)]
    )

    # Merge, sort globally by total score (desc), assign ranks, take top N
    all_scored = [art for batch in batch_results for art in batch]
    all_scored.sort(key=lambda a: a.get("scores", {}).get("total", 0), reverse=True)
    top = all_scored[:TOP_N]
    for i, art in enumerate(top, start=1):
        art["rank"] = i

    result = {"top_articles": top}
    json.dump(result, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())

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
from shared.claude_runner import run_claude  # noqa: E402
SYSTEM_PROMPT = (SCRIPT_DIR / "prompts" / "summarize.md").read_text()

BATCH_SIZE = 3  # articles per parallel call (5 batches for 15 articles)
MAX_CONCURRENCY = 3  # max simultaneous claude processes
STAGGER_DELAY = 2.0  # seconds between batch launches (higher than score — heavier LLM workload)
CLAUDE_BIN = shutil.which("claude") or "claude"
CLAUDE_FLAGS = [
    "--model", "haiku",
    "--max-budget-usd", "1.00",
    "--permission-mode", "bypassPermissions",
    "--no-session-persistence",
    "--bare",
]



# ── Phase tasks ──────────────────────────────────────────────────────

async def summarize_batch(
    articles: list, batch_idx: int, *, semaphore: asyncio.Semaphore, max_retries: int = 3,
) -> list:
    """Summarize one batch of articles in parallel. Returns summary dicts.

    Retries up to *max_retries* times when the LLM returns malformed output.
    """
    # Stagger launch to spread initial burst; semaphore independently caps concurrency
    await asyncio.sleep(batch_idx * STAGGER_DELAY)
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
            raw = await run_claude(
                user_prompt, stdin_data,
                system_prompt=SYSTEM_PROMPT,
                claude_bin=CLAUDE_BIN,
                claude_flags=CLAUDE_FLAGS,
                semaphore=semaphore,
            )
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
                await asyncio.sleep(2 * (attempt + 1))  # linear backoff: 2s, 4s, 6s
    raise last_err


async def generate_trend(
    summaries: list, *, semaphore: asyncio.Semaphore, max_retries: int = 3,
) -> dict:
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
            raw = await run_claude(
                user_prompt, stdin_data,
                system_prompt=SYSTEM_PROMPT,
                claude_bin=CLAUDE_BIN,
                claude_flags=CLAUDE_FLAGS,
                semaphore=semaphore,
            )
            return extract_json_object(raw)
        except (ValueError, json.JSONDecodeError, RuntimeError) as e:
            last_err = e
            if attempt < max_retries:
                print(
                    f"[summarize] Trend attempt {attempt + 1} failed ({e}), retrying...",
                    file=sys.stderr,
                )
                await asyncio.sleep(2 * (attempt + 1))  # linear backoff: 2s, 4s, 6s
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

    # All batches run concurrently — tolerate partial failures
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    batch_results = await asyncio.gather(
        *[summarize_batch(batch, i, semaphore=sem) for i, batch in enumerate(batches)],
        return_exceptions=True,
    )

    # Merge successful batches, log failures
    all_summaries = []
    failed_count = 0
    for i, result in enumerate(batch_results):
        if isinstance(result, BaseException):
            failed_count += 1
            print(f"[summarize] Batch {i + 1} failed permanently: {result}", file=sys.stderr)
        else:
            all_summaries.extend(result)

    if failed_count:
        print(
            f"[summarize] {failed_count}/{len(batches)} batches failed; "
            f"{len(all_summaries)} summaries collected.",
            file=sys.stderr,
        )

    if not all_summaries:
        print("[summarize] ERROR: All batches failed — no summaries collected.", file=sys.stderr)
        sys.exit(1)

    # Restore original rank order
    all_summaries.sort(key=lambda x: x.get("rank", 999))

    # Trend is sequential (needs full picture)
    print("[summarize] Generating trend summary...", file=sys.stderr)
    try:
        trend = await generate_trend(all_summaries, semaphore=sem)
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

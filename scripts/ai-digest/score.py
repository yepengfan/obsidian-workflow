#!/usr/bin/env python3
"""Phase 1: Parallel article scoring + global ranking.

Splits raw articles into batches, scores each batch concurrently via claude -p
subprocesses, then merges and globally ranks the results in Python.

After Claude scoring, a history-based decay is applied so that articles
featured in recent digests are penalised, maximising fresh discoveries.

Key insight: scoring is per-article (embarrassingly parallel); ranking is global
(O(n log n) sort, trivial in Python after scores are collected).

Input  (stdin): raw articles JSON from fetch.py
Output (stdout): scored JSON  { "top_articles": [...] }  — same contract as before
"""

import asyncio
import json
import shutil
import sys
from datetime import date, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR.parent))
from shared.json_helpers import extract_json_array  # noqa: E402
from shared.claude_runner import run_claude  # noqa: E402
SYSTEM_PROMPT = (SCRIPT_DIR / "prompts" / "score.md").read_text()

BATCH_SIZE = 4   # articles per parallel call (~4 batches for 14-16 articles)
TOP_N = 15       # articles to select after global ranking
MAX_CONCURRENCY = 3  # max parallel claude CLI calls to avoid rate limits
STAGGER_DELAY = 1.0  # seconds between batch launches (lower than summarize — smaller batches)
CLAUDE_BIN = shutil.which("claude") or "claude"
CLAUDE_FLAGS = [
    "--model", "sonnet",
    "--effort", "low",
    "--max-budget-usd", "1.00",
    "--permission-mode", "bypassPermissions",
    "--no-session-persistence",
    "--bare",
]

HISTORY_PATH = SCRIPT_DIR / "history.json"
DECAY_WINDOW_DAYS = 7


# ── History management ───────────────────────────────────────────────

def load_history() -> dict:
    """Load history.json or return empty structure."""
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            print("[score] Warning: history.json corrupted, starting fresh.", file=sys.stderr)
    return {"featured": {}}


def save_history(history: dict, selected: list, today: date) -> None:
    """Update and persist history after selecting articles."""
    featured = history.get("featured", {})

    # Record today's selected article links
    featured[today.isoformat()] = [a.get("link", "") for a in selected if a.get("link")]

    # Prune entries older than 14 days
    cutoff = (today - timedelta(days=14)).isoformat()
    featured = {d: links for d, links in featured.items() if d >= cutoff}

    history = {"featured": featured}
    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2))
    print(f"[score] History saved ({len(featured)} days).", file=sys.stderr)


def count_appearances(link: str, featured: dict, today: date) -> int:
    """Count how many times an article appeared in recent digests."""
    cutoff = (today - timedelta(days=DECAY_WINDOW_DAYS)).isoformat()
    count = 0
    for date_str, links in featured.items():
        if date_str >= cutoff and link in links:
            count += 1
    return count


def get_decay(appearances: int) -> float:
    """Return decay multiplier based on recent appearance count."""
    if appearances == 0:
        return 1.0
    if appearances == 1:
        return 0.3
    return 0.1  # 2+ days


# ── Scoring task ─────────────────────────────────────────────────────

async def score_batch(
    articles: list, batch_idx: int, *, semaphore: asyncio.Semaphore, max_retries: int = 3,
) -> list:
    """Score a batch of articles. Returns all articles with scores attached.

    Retries up to *max_retries* times when the LLM returns malformed output.
    """
    # Stagger launch to spread initial burst; semaphore independently caps concurrency
    await asyncio.sleep(batch_idx * STAGGER_DELAY)
    user_prompt = (
        f"Score ALL {len(articles)} articles in this batch using the scoring dimensions "
        "from the system prompt. "
        "Output ONLY a JSON array — one scored object per article, no selection, "
        "no wrapper object, no markdown fences. "
        "Each element must have: title, link, pub_date, description, source_name, "
        "scores (relevance, quality, timeliness, bonus, total), category, keywords."
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
            result = extract_json_array(raw, fallback_keys=("top_articles",))
            print(f"[score] Batch {batch_idx + 1}: {len(result)} articles scored", file=sys.stderr)
            return result
        except (ValueError, json.JSONDecodeError, RuntimeError) as e:
            last_err = e
            if attempt < max_retries:
                print(
                    f"[score] Batch {batch_idx + 1} attempt {attempt + 1} failed "
                    f"({e}), retrying...",
                    file=sys.stderr,
                )
                await asyncio.sleep(2 * (attempt + 1))  # linear backoff: 2s, 4s, 6s
    raise last_err


# ── Main ─────────────────────────────────────────────────────────────

async def main() -> None:
    today = date.today()

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

    if not batches:
        print("[score] ERROR: No articles to score.", file=sys.stderr)
        sys.exit(1)

    # All batches score concurrently — tolerate partial failures
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    batch_results = await asyncio.gather(
        *[score_batch(batch, i, semaphore=sem) for i, batch in enumerate(batches)],
        return_exceptions=True,
    )

    # Merge successful batches, log failures
    all_scored = []
    failed_count = 0
    for i, result in enumerate(batch_results):
        if isinstance(result, BaseException):
            failed_count += 1
            print(f"[score] Batch {i + 1} failed permanently: {result}", file=sys.stderr)
        else:
            all_scored.extend(result)

    if failed_count:
        print(
            f"[score] {failed_count}/{len(batches)} batches failed; "
            f"{len(all_scored)} articles scored successfully.",
            file=sys.stderr,
        )

    if len(all_scored) < TOP_N:
        print(
            f"[score] ERROR: Only {len(all_scored)} articles scored, "
            f"need at least {TOP_N}. Too many batches failed.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Apply history-based decay
    history = load_history()
    featured = history.get("featured", {})
    decayed_count = 0

    for art in all_scored:
        link = art.get("link", "")
        total = art.get("scores", {}).get("total", 0)
        appearances = count_appearances(link, featured, today) if link else 0
        decay = get_decay(appearances)
        art["appearances"] = appearances
        art["decay"] = decay
        art["effective_score"] = round(total * decay, 1)
        if decay < 1.0:
            decayed_count += 1

    if decayed_count:
        print(f"[score] Decay applied to {decayed_count} previously featured articles.", file=sys.stderr)

    # Sort by effective score (desc), assign ranks, take top N
    all_scored.sort(key=lambda a: a.get("effective_score", 0), reverse=True)
    top = all_scored[:TOP_N]
    for i, art in enumerate(top, start=1):
        art["rank"] = i

    # Save history for next run
    save_history(history, top, today)

    result = {"top_articles": top}
    json.dump(result, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())

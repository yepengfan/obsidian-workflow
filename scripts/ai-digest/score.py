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
SYSTEM_PROMPT = (SCRIPT_DIR / "prompts" / "score.md").read_text()

BATCH_SIZE = 4   # articles per parallel call (~4 batches for 14-16 articles)
TOP_N = 15       # articles to select after global ranking
CLAUDE_BIN = shutil.which("claude") or "claude"
CLAUDE_FLAGS = [
    "--model", "haiku",
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


# ── Scoring task ─────────────────────────────────────────────────────

async def score_batch(articles: list, batch_idx: int, max_retries: int = 2) -> list:
    """Score a batch of articles. Returns all articles with scores attached.

    Retries up to *max_retries* times when the LLM returns malformed output.
    """
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
            raw = await run_claude(user_prompt, stdin_data)
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

    # All batches score concurrently
    try:
        batch_results = await asyncio.gather(
            *[score_batch(batch, i) for i, batch in enumerate(batches)]
        )
    except Exception as e:
        print(f"[score] ERROR: Batch scoring failed — {e}", file=sys.stderr)
        sys.exit(1)

    # Merge all scored articles
    all_scored = [art for batch in batch_results for art in batch]

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

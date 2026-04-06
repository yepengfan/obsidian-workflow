#!/usr/bin/env python3
"""Step 2: Claude-powered scoring + summarization for podcast episodes.

Reads episode JSON from stdin (output of transcribe.py), runs two-phase
Claude enrichment per episode (score, then summarize), and writes enriched
JSON to stdout.

Phase 1 — Score: transcript → score, dimensions, category, tags, language
Phase 2 — Summarize: transcript + score → summary_zh, summary_en, takeaways, zettel_candidates

Episodes are processed concurrently via asyncio.gather.

Input  (stdin): {"episodes": [...], "stats": {...}}
Output (stdout): {"episodes": [...enriched], "stats": {...}}
"""

import asyncio
import json
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR.parent))
from shared.json_helpers import extract_json_object  # noqa: E402
SCORE_PROMPT = (SCRIPT_DIR / "prompts" / "score.md").read_text()
SUMMARIZE_PROMPT = (SCRIPT_DIR / "prompts" / "summarize.md").read_text()

CLAUDE_BIN = shutil.which("claude") or "claude"
CLAUDE_FLAGS = [
    "--model", "haiku",
    "--permission-mode", "bypassPermissions",
    "--no-session-persistence",
    "--bare",
]

# Transcript truncation limits (characters)
TRANSCRIPT_MAX_CHARS = 100_000
TRANSCRIPT_HEAD_CHARS = 80_000
TRANSCRIPT_TAIL_CHARS = 20_000
TRANSCRIPT_TRUNCATION_MARKER = "\n\n[...transcript truncated...]\n\n"


# ── Transcript helpers ────────────────────────────────────────────────

def prepare_transcript(transcript_text: str | None) -> str:
    """Truncate transcript if it exceeds the token budget."""
    if not transcript_text:
        return ""
    if len(transcript_text) <= TRANSCRIPT_MAX_CHARS:
        return transcript_text
    head = transcript_text[:TRANSCRIPT_HEAD_CHARS]
    tail = transcript_text[-TRANSCRIPT_TAIL_CHARS:]
    return head + TRANSCRIPT_TRUNCATION_MARKER + tail


# ── Claude subprocess runner ─────────────────────────────────────────

async def run_claude(user_prompt: str, stdin_data: str, system_prompt: str) -> str:
    """Spawn a claude -p subprocess, feed it stdin_data, return stdout."""
    proc = await asyncio.create_subprocess_exec(
        CLAUDE_BIN, "-p", user_prompt,
        "--system-prompt", system_prompt,
        *CLAUDE_FLAGS,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=stdin_data.encode()),
            timeout=180,
        )
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError("claude timed out after 180s")
    if proc.returncode != 0:
        err = stderr.decode().strip()
        raise RuntimeError(f"claude exited {proc.returncode}: {err}")
    return stdout.decode()


# ── Phase 1: Score ───────────────────────────────────────────────────

async def score_episode(episode: dict) -> dict:
    """Score a single episode. Returns score dict or raises on failure."""
    transcript_text = episode.get("transcript_text") or ""
    transcript = prepare_transcript(transcript_text)
    if not transcript:
        raise ValueError("no transcript available — skipping scoring")

    user_prompt = (
        "Score this podcast episode transcript using the 4 weighted dimensions. "
        "Output ONLY valid JSON — no markdown fences, no explanation. "
        "Required fields: score, dimensions, category, tags, language."
    )
    raw = await run_claude(user_prompt, transcript, SCORE_PROMPT)
    return extract_json_object(raw)


# ── Phase 2: Summarize ───────────────────────────────────────────────

async def summarize_episode(episode: dict, score_data: dict) -> dict:
    """Summarize a single episode. Returns summary dict or raises on failure."""
    transcript_text = episode.get("transcript_text") or ""
    transcript = prepare_transcript(transcript_text)
    if not transcript:
        raise ValueError("no transcript available — skipping summarization")

    # Provide both transcript and score context to the summarizer
    combined_input = json.dumps(
        {"transcript": transcript, "score": score_data},
        ensure_ascii=False,
    )

    user_prompt = (
        "Summarize this podcast episode using the transcript and score data provided. "
        "Output ONLY valid JSON — no markdown fences, no explanation. "
        "Required fields: summary_zh, summary_en, takeaways, zettel_candidates."
    )
    raw = await run_claude(user_prompt, combined_input, SUMMARIZE_PROMPT)
    return extract_json_object(raw)


# ── Per-episode enrichment ────────────────────────────────────────────

async def enrich_episode(episode: dict) -> dict:
    """Run both phases for a single episode. Returns enriched episode dict.

    On any Claude failure, logs the error and returns the episode with
    score=0 and empty summary fields rather than crashing the pipeline.
    """
    slug = episode.get("slug", episode.get("title", "unknown"))

    # ── Phase 1: Score ───
    try:
        score_data = await score_episode(episode)
    except Exception as exc:
        print(f"[enrich] ERROR scoring {slug}: {exc}", file=sys.stderr)
        score_data = {
            "score": 0,
            "dimensions": {
                "information_density": 0,
                "novelty": 0,
                "actionability": 0,
                "interest_match": 0,
            },
            "category": "other",
            "tags": [],
            "language": "unknown",
        }

    # ── Phase 2: Summarize ───
    print(f"[enrich] Summarizing: {slug}...", file=sys.stderr)
    try:
        summary_data = await summarize_episode(episode, score_data)
    except Exception as exc:
        print(f"[enrich] ERROR summarizing {slug}: {exc}", file=sys.stderr)
        summary_data = {
            "summary_zh": "",
            "summary_en": "",
            "takeaways": [],
            "zettel_candidates": [],
        }

    # Merge all enrichment fields into the episode
    enriched = dict(episode)
    enriched.update({
        "score": score_data.get("score", 0),
        "dimensions": score_data.get("dimensions", {}),
        "category": score_data.get("category", "other"),
        "tags": score_data.get("tags", []),
        "language": score_data.get("language", "unknown"),
        "summary_zh": summary_data.get("summary_zh", ""),
        "summary_en": summary_data.get("summary_en", ""),
        "takeaways": summary_data.get("takeaways", []),
        "zettel_candidates": summary_data.get("zettel_candidates", []),
    })
    return enriched


# ── Main ─────────────────────────────────────────────────────────────

async def main() -> None:
    raw_data = json.load(sys.stdin)

    if isinstance(raw_data, list):
        episodes = raw_data
        stats = {}
    else:
        episodes = raw_data.get("episodes", [])
        stats = raw_data.get("stats", {})

    if not episodes:
        print("[enrich] No episodes to process.", file=sys.stderr)
        json.dump({"episodes": [], "stats": stats}, sys.stdout, ensure_ascii=False)
        return

    print(f"[enrich] Scoring {len(episodes)} episodes...", file=sys.stderr)

    # Process all episodes concurrently
    enriched_episodes = await asyncio.gather(
        *[enrich_episode(ep) for ep in episodes]
    )

    result = {
        "episodes": list(enriched_episodes),
        "stats": stats,
    }
    json.dump(result, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())

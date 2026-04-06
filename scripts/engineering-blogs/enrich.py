#!/usr/bin/env python3
"""Enrich engineering blog articles via a single Claude -p call.

Reads articles JSON from stdin (output of fetch.py), sends all articles to
Claude for categorization, bilingual summary, and scoring, then merges
enrichment data back, applies history decay, ranks, and outputs the top 10.

Input  (stdin): articles JSON from fetch.py
Output (stdout): enriched JSON { "date": "...", "enriched": [...], "stats": {...} }
"""

import json
import re
import shutil
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SYSTEM_PROMPT = (SCRIPT_DIR / "prompts" / "enrich.md").read_text()
HISTORY_PATH = SCRIPT_DIR / "history.json"

TOP_N = 10
DECAY_WINDOW_DAYS = 7
CLAUDE_BIN = shutil.which("claude") or "claude"
CLAUDE_FLAGS = [
    "--model", "haiku",
    "--max-budget-usd", "1.00",
    "--permission-mode", "bypassPermissions",
    "--no-session-persistence",
    "--bare",
]


# ── History helpers ─────────────────────────────────────────────────

def load_history() -> dict:
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"featured": {}}


def count_appearances(link: str, featured: dict, today: date) -> int:
    cutoff = (today - timedelta(days=DECAY_WINDOW_DAYS)).isoformat()
    count = 0
    for date_str, links in featured.items():
        if date_str >= cutoff and link in links:
            count += 1
    return count


def get_decay(appearances: int) -> float:
    if appearances == 0:
        return 1.0
    if appearances == 1:
        return 0.3
    return 0.1


def save_history(history: dict, selected: list, today: date) -> None:
    featured = history.get("featured", {})
    featured[today.isoformat()] = [a.get("link", "") for a in selected if a.get("link")]
    cutoff = (today - timedelta(days=14)).isoformat()
    featured = {d: links for d, links in featured.items() if d >= cutoff}
    history = {"featured": featured}
    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2))


# ── JSON helpers ────────────────────────────────────────────────────

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
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        obj = json.loads(raw[start : end + 1])
        for key in ("enriched", "articles", "results"):
            if key in obj:
                return obj[key]
    raise ValueError(f"No JSON array found:\n{raw[:400]}")


# ── Claude subprocess runner ────────────────────────────────────────

def run_claude(user_prompt: str, stdin_data: str) -> str:
    result = subprocess.run(
        [CLAUDE_BIN, "-p", user_prompt,
         "--system-prompt", SYSTEM_PROMPT,
         *CLAUDE_FLAGS],
        input=stdin_data.encode(),
        capture_output=True,
        timeout=120,
    )
    if result.returncode != 0:
        err = result.stderr.decode().strip()
        raise RuntimeError(f"claude exited {result.returncode}: {err}")
    return result.stdout.decode()


# ── Main ────────────────────────────────────────────────────────────

def main() -> None:
    today = date.today()
    raw_data = json.load(sys.stdin)

    if isinstance(raw_data, list):
        articles = raw_data
        stats_in = {}
        input_date = today.isoformat()
    else:
        articles = raw_data.get("articles", raw_data)
        stats_in = raw_data.get("stats", {})
        input_date = raw_data.get("date", today.isoformat())

    print(f"[enrich] {len(articles)} articles loaded from stdin", file=sys.stderr)

    # Send to Claude for enrichment
    user_prompt = (
        f"Enrich ALL {len(articles)} articles. "
        "For each article, assign a category, write bilingual summaries focusing on "
        "the key engineering insight, and score it 1–10 with a high bar. "
        "Output ONLY a JSON array — one enriched object per article, in the same order "
        "as input, no markdown fences, no wrapper object."
    )
    print(f"[enrich] Sending {len(articles)} articles to Claude...", file=sys.stderr)

    try:
        raw = run_claude(user_prompt, json.dumps(articles, ensure_ascii=False))
        enrichment_records = extract_json_array(raw)
        print(f"[enrich] Received {len(enrichment_records)} enriched records", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("[enrich] ERROR: Claude CLI timed out after 120s", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"[enrich] ERROR: Claude CLI failed — {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"[enrich] ERROR: JSON parsing failed — {e}", file=sys.stderr)
        sys.exit(1)

    # Build lookup and merge
    enrichment_map: dict[str, dict] = {}
    for rec in enrichment_records:
        link = rec.get("link")
        if link:
            enrichment_map[link] = rec

    merged = []
    for art in articles:
        link = art.get("link", "")
        enc = enrichment_map.get(link, {})
        merged.append({
            **art,
            "category": enc.get("category", "other"),
            "summary_en": enc.get("summary_en", ""),
            "summary_zh": enc.get("summary_zh", ""),
            "score": enc.get("score", 0),
        })

    # Apply history decay
    history = load_history()
    featured = history.get("featured", {})
    for art in merged:
        link = art.get("link", "")
        appearances = count_appearances(link, featured, today) if link else 0
        decay = get_decay(appearances)
        art["appearances"] = appearances
        art["decay"] = decay
        art["effective_score"] = round(art.get("score", 0) * decay, 1)

    # Rank by effective_score, take top N
    merged.sort(key=lambda a: a.get("effective_score", 0), reverse=True)
    top = merged[:TOP_N]
    for i, art in enumerate(top, start=1):
        art["rank"] = i

    # Save history
    save_history(history, top, today)

    print(f"[enrich] Top {len(top)} articles selected after ranking + decay", file=sys.stderr)

    output = {
        "date": input_date,
        "enriched": top,
        "stats": {
            **stats_in,
            "enriched": len(top),
        },
    }
    json.dump(output, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Enrich GitHub trending repos via a single Claude -p call.

Reads repos JSON from stdin (output of fetch.py), sends all repos to Claude
for categorization, bilingual summary, and scoring in one call, then merges
enrichment data back, ranks by score, and outputs the top 15.

Input  (stdin): repos JSON from fetch.py
Output (stdout): enriched JSON { "date": "...", "enriched": [...], "stats": {...} }
"""

import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SYSTEM_PROMPT = (SCRIPT_DIR / "prompts" / "enrich.md").read_text()

TOP_N = 15
CLAUDE_BIN = shutil.which("claude") or "claude"
CLAUDE_FLAGS = [
    "--model", "haiku",
    "--max-budget-usd", "1.00",
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
    # Might be wrapped in an object
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        obj = json.loads(raw[start : end + 1])
        for key in ("enriched", "repos", "results"):
            if key in obj:
                return obj[key]
    raise ValueError(f"No JSON array found:\n{raw[:400]}")


# ── Claude subprocess runner ─────────────────────────────────────────

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


# ── Enrichment ───────────────────────────────────────────────────────

def enrich_repos(repos: list) -> list:
    """Send all repos to Claude in a single call and return enrichment records."""
    user_prompt = (
        f"Enrich ALL {len(repos)} repos in this list. "
        "For each repo, assign a category, write a bilingual one-sentence summary, "
        "and score it 1–10 based on innovation, community interest, and practical utility. "
        "Output ONLY a JSON array — one enriched object per repo, in the same order as input, "
        "no markdown fences, no wrapper object."
    )
    print(f"[enrich] Sending {len(repos)} repos to Claude for enrichment...", file=sys.stderr)
    raw = run_claude(user_prompt, json.dumps(repos, ensure_ascii=False))
    result = extract_json_array(raw)
    print(f"[enrich] Received {len(result)} enriched records", file=sys.stderr)
    return result


# ── Main ─────────────────────────────────────────────────────────────

def main() -> None:
    raw_data = json.load(sys.stdin)

    # Support both a plain list and a structured object from fetch.py
    if isinstance(raw_data, list):
        repos = raw_data
        stats_in = {}
        input_date = date.today().isoformat()
    else:
        repos = raw_data.get("repos", raw_data)
        stats_in = raw_data.get("stats", {})
        input_date = raw_data.get("date", date.today().isoformat())

    total_fetched = stats_in.get("total_fetched", len(repos))
    after_dedup = stats_in.get("after_dedup", len(repos))

    print(f"[enrich] {len(repos)} repos loaded from stdin", file=sys.stderr)

    try:
        enrichment_records = enrich_repos(repos)
    except subprocess.TimeoutExpired:
        print("[enrich] ERROR: Claude CLI timed out after 120s", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"[enrich] ERROR: Claude CLI failed — {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"[enrich] ERROR: JSON parsing failed — {e}", file=sys.stderr)
        sys.exit(1)

    # Build a lookup map from full_name → enrichment data
    enrichment_map: dict[str, dict] = {}
    for rec in enrichment_records:
        name = rec.get("full_name")
        if name:
            enrichment_map[name] = rec

    # Merge enrichment data back into original repo objects
    merged = []
    for repo in repos:
        name = repo.get("full_name", "")
        enc = enrichment_map.get(name, {})
        enriched_repo = {
            **repo,
            "category": enc.get("category", "other"),
            "summary_en": enc.get("summary_en", ""),
            "summary_zh": enc.get("summary_zh", ""),
            "score": enc.get("score", 0),
        }
        merged.append(enriched_repo)

    # Rank by score (desc), take top N
    merged.sort(key=lambda r: r.get("score", 0), reverse=True)
    top = merged[:TOP_N]
    for i, repo in enumerate(top, start=1):
        repo["rank"] = i

    print(f"[enrich] Top {len(top)} repos selected after ranking", file=sys.stderr)

    output = {
        "date": input_date,
        "enriched": top,
        "stats": {
            "total_fetched": total_fetched,
            "after_dedup": after_dedup,
            "enriched": len(top),
        },
    }
    json.dump(output, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()

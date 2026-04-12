#!/usr/bin/env python3
"""Enrich Claude Code plugin repos via batched Claude Haiku calls.

Reads plugin JSON from stdin (output of fetch.py), sends repos to Claude
in batches for classification, scoring, and bilingual summary, filters out
non-plugins, and outputs enriched JSON to stdout.

Input  (stdin): JSON from fetch.py
Output (stdout): enriched JSON { "week": "...", "enriched": [...], "stats": {...} }
"""

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR.parent))
from shared.json_helpers import extract_json_array  # noqa: E402
SYSTEM_PROMPT = (SCRIPT_DIR / "prompts" / "enrich.md").read_text()

CLAUDE_BIN = shutil.which("claude") or "claude"
CLAUDE_FLAGS = [
    "--model", "haiku",
    "--max-budget-usd", "1.00",
    "--permission-mode", "bypassPermissions",
    "--no-session-persistence",
    "--bare",
]

BATCH_SIZE = 50  # repos per Haiku call (50 is proven reliable)
MAX_RETRIES = 3
RETRY_DELAY = 4  # seconds between retries


# ── Claude subprocess runner ───────────────────────────────────────

def run_claude(user_prompt: str, stdin_data: str) -> str:
    result = subprocess.run(
        [CLAUDE_BIN, "-p", user_prompt,
         "--system-prompt", SYSTEM_PROMPT,
         *CLAUDE_FLAGS],
        input=stdin_data.encode(),
        capture_output=True,
        timeout=240,
    )
    if result.returncode != 0:
        err = result.stderr.decode().strip()
        raise RuntimeError(f"claude exited {result.returncode}: {err}")
    return result.stdout.decode()


# ── Enrichment ─────────────────────────────────────────────────────

def _slim_plugin(p: dict) -> dict:
    """Prepare a slimmed-down plugin payload for Haiku."""
    return {
        "repo_url": p["repo_url"],
        "name": p["name"],
        "full_name": p["full_name"],
        "description": p["description"],
        "stars": p["stars"],
        "forks": p["forks"],
        "language": p["language"],
        "topics": p["topics"],
        "pushed_at": p["pushed_at"],
        "age_days": p["age_days"],
        "readme_excerpt": p.get("readme_excerpt", "")[:500],
        "npm_info": p.get("npm_info"),
    }


def _enrich_batch(slim_batch: list, batch_num: int) -> list:
    """Enrich a single batch with retries."""
    user_prompt = (
        f"Classify and enrich ALL {len(slim_batch)} repos in this list. "
        "For each repo, first determine if it's a real Claude Code plugin (is_plugin). "
        "For real plugins, score across 4 dimensions, categorize, and write bilingual summaries. "
        "Output ONLY a JSON array — one object per repo, in the same order as input."
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            raw = run_claude(user_prompt, json.dumps(slim_batch, ensure_ascii=False))
            result = extract_json_array(raw, fallback_keys=("enriched", "plugins", "results"))
            print(f"[enrich] Batch {batch_num}: {len(result)} records", file=sys.stderr)
            return result
        except (subprocess.TimeoutExpired, RuntimeError, ValueError) as e:
            msg = str(e)[:80]
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY * attempt
                print(
                    f"[enrich] Batch {batch_num} attempt {attempt} failed ({msg}), "
                    f"retrying in {delay}s...",
                    file=sys.stderr,
                )
                time.sleep(delay)
            else:
                print(
                    f"[enrich] Batch {batch_num} failed after {MAX_RETRIES} attempts ({msg})",
                    file=sys.stderr,
                )
                return []  # graceful degradation: skip this batch


def enrich_plugins(plugins: list) -> list:
    """Send plugins to Claude in batches and return enrichment records."""
    slim = [_slim_plugin(p) for p in plugins]

    # Split into batches
    batches = [slim[i:i + BATCH_SIZE] for i in range(0, len(slim), BATCH_SIZE)]
    total_batches = len(batches)
    print(
        f"[enrich] {len(slim)} repos → {total_batches} batch(es) "
        f"(batch size {BATCH_SIZE})",
        file=sys.stderr,
    )

    all_records = []
    for i, batch in enumerate(batches, 1):
        records = _enrich_batch(batch, i)
        all_records.extend(records)
        if i < total_batches:
            time.sleep(2)  # brief pause between batches

    print(f"[enrich] Total: {len(all_records)} enrichment records.", file=sys.stderr)
    return all_records


# ── Main ───────────────────────────────────────────────────────────

def main() -> None:
    raw_data = json.load(sys.stdin)

    if isinstance(raw_data, list):
        plugins = raw_data
        stats_in = {}
        week = ""
        input_date = ""
    else:
        plugins = raw_data.get("plugins", raw_data)
        stats_in = raw_data.get("stats", {})
        week = raw_data.get("week", "")
        input_date = raw_data.get("date", "")

    print(f"[enrich] {len(plugins)} repos loaded from stdin.", file=sys.stderr)

    enrichment_records = enrich_plugins(plugins)

    if not enrichment_records:
        print("[enrich] ERROR: All batches failed, no enrichment data.", file=sys.stderr)
        sys.exit(1)

    # Build lookup by repo_url
    enrichment_map: dict[str, dict] = {}
    for rec in enrichment_records:
        url = rec.get("repo_url")
        if url:
            enrichment_map[url] = rec

    # Merge enrichment back into original plugin objects, filter non-plugins
    merged = []
    filtered_out = 0
    for plugin in plugins:
        url = plugin.get("repo_url", "")
        enc = enrichment_map.get(url, {})

        # Classification gate: skip non-plugins
        if not enc.get("is_plugin", False):
            filtered_out += 1
            continue

        enriched = {
            **plugin,
            "is_plugin": True,
            "score": enc.get("score", 0),
            "dimensions": enc.get("dimensions", {}),
            "category": enc.get("category", "other"),
            "summary_zh": enc.get("summary_zh", ""),
            "summary_en": enc.get("summary_en", ""),
            "install_cmd": enc.get("install_cmd", f"claude plugin add {plugin.get('name', '')}"),
            "tags": enc.get("tags", []),
        }
        merged.append(enriched)

    print(
        f"[enrich] Classification: {len(merged)} real plugins, "
        f"{filtered_out} filtered out.",
        file=sys.stderr,
    )

    # Sort by composite score descending
    merged.sort(key=lambda r: r.get("score", 0), reverse=True)

    # Assign ranks
    for i, plugin in enumerate(merged, start=1):
        plugin["rank"] = i

    output = {
        "week": week,
        "date": input_date,
        "enriched": merged,
        "stats": {
            **stats_in,
            "classified_plugins": len(merged),
            "filtered_out": filtered_out,
        },
    }
    json.dump(output, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()

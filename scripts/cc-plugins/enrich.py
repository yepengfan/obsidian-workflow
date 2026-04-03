#!/usr/bin/env python3
"""Enrich Claude Code plugin repos via a single Claude Haiku call.

Reads plugin JSON from stdin (output of fetch.py), sends all repos to Claude
for classification, scoring, and bilingual summary, filters out non-plugins,
and outputs enriched JSON to stdout.

Input  (stdin): JSON from fetch.py
Output (stdout): enriched JSON { "week": "...", "enriched": [...], "stats": {...} }
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SYSTEM_PROMPT = (SCRIPT_DIR / "prompts" / "enrich.md").read_text()

CLAUDE_BIN = shutil.which("claude") or "claude"
CLAUDE_FLAGS = [
    "--model", "haiku",
    "--max-budget-usd", "1.00",
    "--permission-mode", "bypassPermissions",
    "--no-session-persistence",
]


# ── JSON helpers ───────────────────────────────────────────────────

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
        for key in ("enriched", "plugins", "results"):
            if key in obj:
                return obj[key]
    raise ValueError(f"No JSON array found:\n{raw[:400]}")


# ── Claude subprocess runner ───────────────────────────────────────

def run_claude(user_prompt: str, stdin_data: str) -> str:
    result = subprocess.run(
        [CLAUDE_BIN, "-p", user_prompt,
         "--system-prompt", SYSTEM_PROMPT,
         *CLAUDE_FLAGS],
        input=stdin_data.encode(),
        capture_output=True,
        timeout=180,
    )
    if result.returncode != 0:
        err = result.stderr.decode().strip()
        raise RuntimeError(f"claude exited {result.returncode}: {err}")
    return result.stdout.decode()


# ── Enrichment ─────────────────────────────────────────────────────

def enrich_plugins(plugins: list) -> list:
    """Send all plugins to Claude in a single call and return enrichment records."""
    # Prepare a slimmed-down payload for Haiku (skip large readme excerpts)
    slim = []
    for p in plugins:
        slim.append({
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
        })

    user_prompt = (
        f"Classify and enrich ALL {len(slim)} repos in this list. "
        "For each repo, first determine if it's a real Claude Code plugin (is_plugin). "
        "For real plugins, score across 4 dimensions, categorize, and write bilingual summaries. "
        "Output ONLY a JSON array — one object per repo, in the same order as input."
    )
    print(f"[enrich] Sending {len(slim)} repos to Claude for classification + enrichment...", file=sys.stderr)
    raw = run_claude(user_prompt, json.dumps(slim, ensure_ascii=False))
    result = extract_json_array(raw)
    print(f"[enrich] Received {len(result)} enrichment records.", file=sys.stderr)
    return result


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

    try:
        enrichment_records = enrich_plugins(plugins)
    except subprocess.TimeoutExpired:
        print("[enrich] ERROR: Claude CLI timed out after 180s.", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"[enrich] ERROR: Claude CLI failed — {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"[enrich] ERROR: JSON parsing failed — {e}", file=sys.stderr)
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

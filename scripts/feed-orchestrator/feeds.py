"""Feed configuration and Anthropic SDK enrichment logic.

Each feed has:
- Config dict (paths, cadence, env vars for write_reports.py)
- Enrichment function using anthropic.AsyncAnthropic (replaces Claude CLI)
- Subprocess helpers for fetch.py and write_reports.py
"""

import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any

import anthropic

# ── Feed Configuration ──────────────────────────────────────────────

# Model auto-detection: proxy (LiteLLM) needs "anthropic." prefix
_MODEL_DIRECT = "claude-sonnet-4-6-20250514"
_MODEL_PROXY = "anthropic.claude-4-6-sonnet"
HAIKU_MODEL: str | None = os.environ.get("FEED_HAIKU_MODEL")  # explicit override
MAX_CONCURRENT = 3
STAGGER_DELAY = 0.5  # seconds between batch launches


def get_feed_config(vault_path: str | Path) -> dict[str, dict[str, Any]]:
    """Return feed configs with resolved paths."""
    v = Path(vault_path)
    s = v / "scripts"
    return {
        "ai-digest": {
            "module": "feeds-ai-digest",
            "feed_dir": v / "Feeds" / "AI-Daily",
            "script_dir": s / "ai-digest",
            "python": str(s / "ai-digest" / ".venv" / "bin" / "python"),
            "cadence": "daily",
            "report_path": lambda: v / "Feeds" / "AI-Daily" / f"{_today()}.md",
            "tmpdir_env": "TMPDIR_DIGEST",
            "extra_env": {},
            "extra_tmpfiles": ["articles.json", "scored.json", "summaries.json"],
            "archive_max_days": 14,
        },
        "github-trending": {
            "module": "feeds-github-trending",
            "feed_dir": v / "Feeds" / "GitHub-Trending",
            "script_dir": s / "github-trending",
            "python": "python3",
            "cadence": "daily",
            "report_path": lambda: v / "Feeds" / "GitHub-Trending" / f"{_today()}.md",
            "tmpdir_env": "TMPDIR_TRENDING",
            "extra_env": {},
            "extra_tmpfiles": ["fetched.json", "enriched.json"],
            "archive_max_days": 14,
        },
        "engineering-blogs": {
            "module": "feeds-engineering-blogs",
            "feed_dir": v / "Feeds" / "Engineering-Blogs",
            "script_dir": s / "engineering-blogs",
            "python": "python3",
            "cadence": "daily",
            "report_path": lambda: v / "Feeds" / "Engineering-Blogs" / f"{_today()}.md",
            "tmpdir_env": "TMPDIR_ENGBLOGS",
            "extra_env": {},
            "extra_tmpfiles": ["fetched.json", "enriched.json"],
            "archive_max_days": 14,
        },
        "cc-plugins": {
            "module": "feeds-cc-plugins",
            "feed_dir": v / "Feeds" / "CC-Plugins",
            "script_dir": s / "cc-plugins",
            "python": "python3",
            "cadence": "weekly",
            "report_path": lambda: v / "Feeds" / "CC-Plugins" / f"{_this_week()}.md",
            "tmpdir_env": "TMPDIR_CC_PLUGINS",
            "extra_env": {"WEEK": _this_week()},
            "extra_tmpfiles": ["fetched.json", "enriched.json"],
            "archive_max_weeks": 14,
        },
    }


# ── Module Guard ────────────────────────────────────────────────────

def check_module_enabled(vault_path: Path, module_name: str) -> bool:
    """Check if a module is enabled (matches bash grep pattern)."""
    module_file = vault_path / "system" / "modules" / module_name / "module.md"
    if not module_file.exists():
        return True  # If no module file, assume enabled
    content = module_file.read_text()
    return "enabled: false" not in content


def check_report_exists(config: dict[str, Any]) -> Path | None:
    """Return report path if it exists, else None."""
    report_path = config["report_path"]()
    return report_path if report_path.exists() else None


# ── Fetch (subprocess) ──────────────────────────────────────────────

async def run_fetch(
    feed_name: str, config: dict[str, Any], vault_path: Path
) -> str:
    """Run fetch.py as subprocess, return JSON string."""
    script = config["script_dir"] / "fetch.py"
    python = config["python"]
    args = [python, str(script), "--vault-path", str(vault_path)]

    # cc-plugins needs longer timeout: 7 GitHub search queries × up to 4 pages
    # can hit unauthenticated rate limits (10 req/min) causing long sleeps
    fetch_timeout = 300 if config.get("cadence") == "weekly" else 120

    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(config["script_dir"]),
        env=_build_env(config),
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=fetch_timeout
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise FetchError(
            f"{feed_name} fetch timed out after {fetch_timeout}s "
            f"(hint: set GITHUB_TOKEN to avoid rate-limit delays)"
        )

    if proc.returncode == 2:
        raise ReportExistsError(f"{feed_name} report already exists")
    if proc.returncode != 0:
        err_msg = stderr.decode()[-500:] if stderr else "unknown error"
        raise FetchError(f"{feed_name} fetch failed (exit {proc.returncode}): {err_msg}")

    return stdout.decode()


# ── Enrichment (Anthropic SDK) ──────────────────────────────────────

async def run_enrich(
    feed_name: str,
    config: dict[str, Any],
    fetched_json: str,
) -> str:
    """Enrich/score feed data using Anthropic SDK with Haiku.

    Returns JSON string of enriched data.
    Replaces all Claude CLI calls with direct API calls.
    """
    prompt_dir = config["script_dir"] / "prompts"

    if feed_name == "ai-digest":
        return await _enrich_ai_digest(fetched_json, prompt_dir)
    elif feed_name == "github-trending":
        return await _enrich_single_call(fetched_json, prompt_dir / "enrich.md", "enriched")
    elif feed_name == "engineering-blogs":
        return await _enrich_single_call(fetched_json, prompt_dir / "enrich.md", "enriched")
    elif feed_name == "cc-plugins":
        return await _enrich_single_call(fetched_json, prompt_dir / "enrich.md", "enriched")
    else:
        raise ValueError(f"Unknown feed: {feed_name}")


async def _enrich_ai_digest(fetched_json: str, prompt_dir: Path) -> str:
    """AI Digest: score articles → select top 15 → bilingual summarization.

    Two-phase enrichment:
    1. Score all articles in batches (4 per call, max 3 concurrent)
    2. Summarize top 15 in batches (5 per call, max 3 concurrent)
    """
    data = json.loads(fetched_json)
    articles = data.get("articles", [])
    if not articles:
        return json.dumps({"top_articles": [], "summaries": [], "trend_zh": "", "trend_en": ""})

    # Phase 1: Score articles in batches
    score_prompt = (prompt_dir / "score.md").read_text()
    batches = _chunk(articles, 4)
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    async def score_batch(batch: list) -> list:
        async with sem:
            await asyncio.sleep(STAGGER_DELAY)
            result = await _call_haiku(
                system=score_prompt,
                user=json.dumps(batch, ensure_ascii=False),
            )
            parsed = _parse_json_response(result)
            if isinstance(parsed, dict):
                return parsed.get("top_articles", [])
            return parsed if isinstance(parsed, list) else []

    scored_results = await asyncio.gather(
        *[score_batch(b) for b in batches], return_exceptions=True
    )

    # Merge and sort all scored articles
    all_scored = []
    for result in scored_results:
        if isinstance(result, Exception):
            print(f"[enrich] Score batch failed: {result}", file=sys.stderr)
            continue
        all_scored.extend(result)

    all_scored.sort(key=lambda a: a.get("scores", {}).get("total", 0), reverse=True)
    top_articles = all_scored[:15]

    # Re-rank
    for i, article in enumerate(top_articles, 1):
        article["rank"] = i

    # Phase 2: Summarize top articles
    summarize_prompt = (prompt_dir / "summarize.md").read_text()
    sum_batches = _chunk(top_articles, 5)

    async def summarize_batch(batch: list) -> list:
        async with sem:
            await asyncio.sleep(STAGGER_DELAY)
            result = await _call_haiku(
                system=summarize_prompt,
                user=json.dumps({"top_articles": batch}, ensure_ascii=False),
            )
            parsed = _parse_json_response(result)
            if isinstance(parsed, dict):
                return parsed.get("summaries", [])
            return parsed if isinstance(parsed, list) else []

    summary_results = await asyncio.gather(
        *[summarize_batch(b) for b in sum_batches], return_exceptions=True
    )

    all_summaries = []
    for result in summary_results:
        if isinstance(result, Exception):
            print(f"[enrich] Summarize batch failed: {result}", file=sys.stderr)
            continue
        all_summaries.extend(result)

    # Generate trend summary from all top articles at once
    trend_result = await _call_haiku(
        system=summarize_prompt,
        user=json.dumps({"top_articles": top_articles}, ensure_ascii=False),
    )
    trend_parsed = _parse_json_response(trend_result)
    trend_zh = trend_parsed.get("trend_zh", "") if isinstance(trend_parsed, dict) else ""
    trend_en = trend_parsed.get("trend_en", "") if isinstance(trend_parsed, dict) else ""

    # Build combined output matching existing pipeline format
    scored_output = json.dumps({"top_articles": top_articles}, ensure_ascii=False)
    summaries_output = json.dumps(
        {"summaries": all_summaries, "trend_zh": trend_zh, "trend_en": trend_en},
        ensure_ascii=False,
    )
    return json.dumps(
        {"scored": scored_output, "summaries": summaries_output},
        ensure_ascii=False,
    )


async def _enrich_single_call(
    fetched_json: str, prompt_path: Path, wrap_key: str
) -> str:
    """Enrich with a single Haiku call (GitHub Trending, Eng Blogs, CC Plugins)."""
    data = json.loads(fetched_json)

    # Extract the items array from the fetched data
    items = data.get("repos", data.get("articles", data.get("plugins", [])))
    print(f"[enrich] {wrap_key}: fetched data keys={list(data.keys())}, items count={len(items)}", file=sys.stderr)
    if not items:
        return json.dumps({wrap_key: []})

    system_prompt = prompt_path.read_text()

    # For large item lists, batch them
    if len(items) > 30:
        return await _enrich_batched(items, system_prompt, wrap_key)

    print(f"[enrich] {wrap_key}: sending {len(items)} items to model", file=sys.stderr)
    result = await _call_haiku(
        system=system_prompt,
        user=json.dumps(items, ensure_ascii=False),
    )
    print(f"[enrich] {wrap_key}: raw response length={len(result)}, first 200 chars: {result[:200]}", file=sys.stderr)
    parsed = _parse_json_response(result)
    print(f"[enrich] {wrap_key}: parsed type={type(parsed).__name__}, len={len(parsed) if isinstance(parsed, (list, dict)) else 'N/A'}", file=sys.stderr)
    if isinstance(parsed, list):
        enriched = parsed
    elif isinstance(parsed, dict) and wrap_key in parsed:
        enriched = parsed[wrap_key]
    elif isinstance(parsed, dict) and any(k in parsed for k in ("title", "full_name", "link")):
        # Model returned a single item instead of an array — wrap it
        print(f"[enrich] {wrap_key}: single object returned, wrapping as array", file=sys.stderr)
        enriched = [parsed]
    else:
        print(f"[enrich] {wrap_key}: FALLBACK to empty — parsed keys={list(parsed.keys()) if isinstance(parsed, dict) else 'not dict'}", file=sys.stderr)
        enriched = parsed if isinstance(parsed, list) else []

    # Assign rank by score (required by cc-plugins write_reports)
    enriched.sort(key=lambda r: r.get("score", 0), reverse=True)
    for i, item in enumerate(enriched, start=1):
        item.setdefault("rank", i)

    return json.dumps(
        {wrap_key: enriched, "date": _today(), "stats": {"enriched_count": len(enriched)}},
        ensure_ascii=False,
    )


async def _enrich_batched(
    items: list, system_prompt: str, wrap_key: str, batch_size: int = 30
) -> str:
    """Enrich large item lists in batches."""
    batches = _chunk(items, batch_size)
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    async def enrich_batch(batch: list) -> list:
        async with sem:
            await asyncio.sleep(STAGGER_DELAY)
            result = await _call_haiku(
                system=system_prompt,
                user=json.dumps(batch, ensure_ascii=False),
            )
            parsed = _parse_json_response(result)
            return parsed if isinstance(parsed, list) else []

    results = await asyncio.gather(
        *[enrich_batch(b) for b in batches], return_exceptions=True
    )

    enriched = []
    for result in results:
        if isinstance(result, Exception):
            print(f"[enrich] Batch failed: {result}", file=sys.stderr)
            continue
        enriched.extend(result)

    # Assign rank by score (required by cc-plugins write_reports)
    enriched.sort(key=lambda r: r.get("score", 0), reverse=True)
    for i, item in enumerate(enriched, start=1):
        item.setdefault("rank", i)

    return json.dumps(
        {wrap_key: enriched, "date": _today(), "stats": {"enriched_count": len(enriched)}},
        ensure_ascii=False,
    )


# ── Write Reports (subprocess) ──────────────────────────────────────

async def run_write_reports(
    feed_name: str,
    config: dict[str, Any],
    vault_path: Path,
    fetched_json: str,
    enriched_json: str,
) -> str:
    """Run write_reports.py as subprocess, return generated file path."""
    tmpdir = tempfile.mkdtemp(prefix=f"feed-{feed_name}-")
    script = config["script_dir"] / "write_reports.py"
    python = config["python"]

    try:
        # Write data files to tmpdir (matching existing conventions)
        if feed_name == "ai-digest":
            # AI digest enriched_json has {scored, summaries} wrapper
            wrapper = json.loads(enriched_json)
            Path(tmpdir, "scored.json").write_text(wrapper["scored"])
            Path(tmpdir, "summaries.json").write_text(wrapper["summaries"])
            Path(tmpdir, "articles.json").write_text(fetched_json)
        else:
            Path(tmpdir, "fetched.json").write_text(fetched_json)
            Path(tmpdir, "enriched.json").write_text(enriched_json)

        # Build environment
        env = _build_env(config)
        env[config["tmpdir_env"]] = tmpdir
        env["TODAY"] = _today()
        env["VAULT_DIR"] = str(vault_path)
        # CC Plugins also needs WEEK
        if feed_name == "cc-plugins":
            env["WEEK"] = _this_week()

        proc = await asyncio.create_subprocess_exec(
            python, str(script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(config["script_dir"]),
            env=env,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)

        if proc.returncode != 0:
            err_msg = stderr.decode()[-500:] if stderr else "unknown error"
            raise WriteError(f"write_reports.py failed: {err_msg}")

        return str(config["report_path"]())
    finally:
        # Clean up tmpdir
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Archive ─────────────────────────────────────────────────────────

def archive_old_reports(config: dict[str, Any]) -> list[str]:
    """Archive old reports, return list of archived filenames."""
    feed_dir = config["feed_dir"]
    archive_dir = feed_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archived = []

    if config["cadence"] == "weekly":
        max_weeks = config.get("archive_max_weeks", 14)
        archived = _archive_weekly(feed_dir, archive_dir, max_weeks)
    else:
        max_days = config.get("archive_max_days", 14)
        archived = _archive_daily(feed_dir, archive_dir, max_days)

    return archived


def _archive_daily(feed_dir: Path, archive_dir: Path, max_days: int) -> list[str]:
    """Archive daily reports older than max_days."""
    today = date.today()
    archived = []
    date_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2})(-en)?\.md$")

    for f in feed_dir.iterdir():
        if f.name == "Dashboard.md" or f.is_dir():
            continue
        m = date_pattern.match(f.name)
        if not m:
            continue
        try:
            fdate = date.fromisoformat(m.group(1))
            days_old = (today - fdate).days
            if days_old > max_days:
                f.rename(archive_dir / f.name)
                archived.append(f.name)
        except ValueError:
            continue
    return archived


def _archive_weekly(feed_dir: Path, archive_dir: Path, max_weeks: int) -> list[str]:
    """Archive weekly reports older than max_weeks."""
    archived = []
    week_pattern = re.compile(r"^(\d{4})-W(\d{2})(-en)?\.md$")
    current_year, current_week, _ = date.today().isocalendar()

    for f in feed_dir.iterdir():
        if f.name == "Dashboard.md" or f.is_dir():
            continue
        m = week_pattern.match(f.name)
        if not m:
            continue
        try:
            file_year = int(m.group(1))
            file_week = int(m.group(2))
            week_diff = (current_year - file_year) * 52 + (current_week - file_week)
            if week_diff > max_weeks:
                f.rename(archive_dir / f.name)
                archived.append(f.name)
        except ValueError:
            continue
    return archived


# ── Anthropic SDK Helpers ───────────────────────────────────────────

_client: anthropic.AsyncAnthropic | None = None


def get_client() -> anthropic.AsyncAnthropic:
    """Lazy-init Anthropic async client.

    Auth resolution (same pattern as cc-plugins/enrich.py):
      1. ANTHROPIC_API_KEY   → direct Anthropic API
      2. ANTHROPIC_AUTH_TOKEN → Bearer auth (LiteLLM proxy)
    Model auto-selected based on auth method unless FEED_HAIKU_MODEL is set.
    """
    global _client, HAIKU_MODEL
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
        if api_key:
            _client = anthropic.AsyncAnthropic(api_key=api_key)
            if HAIKU_MODEL is None:
                HAIKU_MODEL = _MODEL_DIRECT
        elif auth_token:
            _client = anthropic.AsyncAnthropic(auth_token=auth_token)
            if HAIKU_MODEL is None:
                HAIKU_MODEL = _MODEL_PROXY
        else:
            raise RuntimeError(
                "Neither ANTHROPIC_API_KEY nor ANTHROPIC_AUTH_TOKEN is set."
            )
        print(f"[enrich] Using model: {HAIKU_MODEL}", file=sys.stderr)
    return _client


async def _call_haiku(system: str, user: str, retries: int = 3) -> str:
    """Call Haiku with retry + exponential backoff."""
    client = get_client()
    for attempt in range(retries):
        try:
            response = await client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=16384,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            text = response.content[0].text if response.content else ""
            if not text.strip():
                raise ValueError("Empty response from Haiku")
            return text
        except (anthropic.RateLimitError, anthropic.APIConnectionError) as e:
            if attempt < retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"[haiku] Retry {attempt + 1}/{retries} after {wait}s: {e}", file=sys.stderr)
                await asyncio.sleep(wait)
            else:
                raise
    return ""  # unreachable


def _parse_json_response(raw: str) -> Any:
    """Parse LLM JSON output, handling common issues (fences, trailing commas)."""
    text = raw.strip()

    # Strip markdown code fences
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    text = text.strip()

    # Try parsing as-is first (preserves strings with commas)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[parse] Direct parse failed: {e}", file=sys.stderr)

    # Fix trailing commas before } or ] and retry
    fixed = re.sub(r",(\s*[}\]])", r"\1", text)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print(f"[parse] Trailing-comma fix also failed: {e}", file=sys.stderr)

    # Fallback: extract JSON structures from surrounding text
    # Try array first
    arr_start = text.find("[")
    if arr_start != -1:
        depth = 0
        for i in range(arr_start, len(text)):
            if text[i] == "[":
                depth += 1
            elif text[i] == "]":
                depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[arr_start : i + 1])
                except json.JSONDecodeError:
                    break

    # Array parse failed — extract individual {...} objects (recovers partial results)
    objects = []
    i = 0
    while i < len(text):
        if text[i] == "{":
            depth = 0
            in_string = False
            escape = False
            for j in range(i, len(text)):
                c = text[j]
                if escape:
                    escape = False
                    continue
                if c == "\\":
                    escape = True
                    continue
                if c == '"' and not escape:
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[i : j + 1])
                        objects.append(obj)
                    except json.JSONDecodeError:
                        pass
                    i = j + 1
                    break
            else:
                break  # unterminated object
        else:
            i += 1

    if objects:
        print(f"[parse] Recovered {len(objects)} objects from broken JSON", file=sys.stderr)
        return objects

    raise ValueError(f"Cannot parse JSON from LLM response: {text[:200]}")


# ── Utilities ───────────────────────────────────────────────────────

def _today() -> str:
    return date.today().isoformat()


def _this_week() -> str:
    d = date.today()
    year, week, _ = d.isocalendar()
    return f"{year}-W{week:02d}"


def _chunk(lst: list, n: int) -> list[list]:
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def _build_env(config: dict[str, Any]) -> dict[str, str]:
    """Build environment dict for subprocess, extending PATH."""
    env = os.environ.copy()
    env["PATH"] = (
        f"{Path.home()}/.local/bin:"
        f"{Path.home()}/.npm-global/bin:"
        f"/usr/local/bin:/opt/homebrew/bin:"
        f"{env.get('PATH', '')}"
    )
    env.update(config.get("extra_env", {}))

    # Auto-resolve GITHUB_TOKEN from gh CLI if not already set
    if not env.get("GITHUB_TOKEN"):
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                env["GITHUB_TOKEN"] = result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass  # gh not installed or hung — proceed without token

    return env


# ── Exceptions ──────────────────────────────────────────────────────

class ReportExistsError(Exception):
    pass

class FetchError(Exception):
    pass

class EnrichError(Exception):
    pass

class WriteError(Exception):
    pass

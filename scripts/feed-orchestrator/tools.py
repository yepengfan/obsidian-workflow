"""Agent SDK custom tool definitions for feed orchestration.

Each tool wraps feeds.py logic and returns results as MCP tool content blocks.
Tools communicate via a shared CONTEXT dict (set by main.py before agent starts).
Intermediate data (fetched JSON, enriched JSON) stored in CONTEXT to avoid
passing large payloads through tool arguments.
"""

import json
import sys
import traceback
from pathlib import Path
from typing import Any

from claude_agent_sdk import tool, create_sdk_mcp_server

from feeds import (
    get_feed_config,
    check_module_enabled,
    check_report_exists,
    run_fetch,
    run_enrich,
    run_write_reports,
    archive_old_reports,
    ReportExistsError,
    FetchError,
)
from status import StatusReporter

# ── Shared Context ──────────────────────────────────────────────────
# Set by main.py before agent starts. Holds vault_path, status reporter,
# feed configs, and intermediate data between tool calls.

CONTEXT: dict[str, Any] = {
    "vault_path": None,
    "reporter": None,
    "configs": {},
    "data": {},  # {feed_name: {"fetched": str, "enriched": str}}
}

VALID_FEEDS = ["ai-digest", "github-trending", "engineering-blogs"]


def init_context(vault_path: str | Path, feed_names: list[str] | None = None) -> None:
    """Initialize shared context. Called by main.py."""
    vp = Path(vault_path)
    CONTEXT["vault_path"] = vp
    CONTEXT["reporter"] = StatusReporter(vp, feed_names=feed_names)
    CONTEXT["configs"] = get_feed_config(vp)
    CONTEXT["data"] = {}


def _text(msg: str) -> dict[str, Any]:
    """Helper: build MCP tool content response."""
    return {"content": [{"type": "text", "text": msg}]}


def _error(msg: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"ERROR: {msg}"}], "isError": True}


# ── Tool Definitions ────────────────────────────────────────────────


@tool(
    "check_module_status",
    "Check if a feed module is enabled or disabled. Returns 'enabled' or 'disabled' for the given feed.",
    {"feed_name": str},
)
async def check_module_status_tool(args: dict[str, Any]) -> dict[str, Any]:
    feed_name = args["feed_name"]
    if feed_name not in VALID_FEEDS:
        return _error(f"Unknown feed: {feed_name}. Valid: {VALID_FEEDS}")

    config = CONTEXT["configs"][feed_name]
    vault_path = CONTEXT["vault_path"]
    enabled = check_module_enabled(vault_path, config["module"])

    reporter: StatusReporter = CONTEXT["reporter"]
    if not enabled:
        reporter.update_feed(feed_name, "disabled", message="Module disabled")

    status = "enabled" if enabled else "disabled"
    return _text(f"{feed_name}: {status}")


@tool(
    "check_existing_report",
    "Check if today's report already exists. Returns the file path if it exists, or 'not_found'.",
    {"feed_name": str},
)
async def check_existing_report_tool(args: dict[str, Any]) -> dict[str, Any]:
    feed_name = args["feed_name"]
    if feed_name not in VALID_FEEDS:
        return _error(f"Unknown feed: {feed_name}. Valid: {VALID_FEEDS}")

    config = CONTEXT["configs"][feed_name]
    existing = check_report_exists(config)

    if existing:
        reporter: StatusReporter = CONTEXT["reporter"]
        reporter.update_feed(
            feed_name, "skipped",
            message=f"Report already exists",
            output_path=str(existing),
        )
        return _text(f"{feed_name}: exists → {existing}")

    return _text(f"{feed_name}: not_found")


@tool(
    "fetch_feed",
    "Fetch raw data for a feed (RSS articles, GitHub repos, etc.). "
    "Runs the feed's fetch.py script and stores the result internally. "
    "Must be called before enrich_feed.",
    {"feed_name": str},
)
async def fetch_feed_tool(args: dict[str, Any]) -> dict[str, Any]:
    feed_name = args["feed_name"]
    if feed_name not in VALID_FEEDS:
        return _error(f"Unknown feed: {feed_name}. Valid: {VALID_FEEDS}")

    config = CONTEXT["configs"][feed_name]
    vault_path = CONTEXT["vault_path"]
    reporter: StatusReporter = CONTEXT["reporter"]

    reporter.update_feed(feed_name, "running", message="Fetching data...")

    try:
        fetched_json = await run_fetch(feed_name, config, vault_path)
        # Store for subsequent enrich/write calls
        CONTEXT["data"].setdefault(feed_name, {})["fetched"] = fetched_json

        # Parse to get stats
        data = json.loads(fetched_json)
        items = data.get("articles", data.get("repos", []))
        count = len(items)

        reporter.update_feed(feed_name, "running", message=f"Fetched {count} items")
        return _text(f"{feed_name}: fetched {count} items")

    except ReportExistsError:
        reporter.update_feed(feed_name, "skipped", message="Report already exists (fetcher check)")
        return _text(f"{feed_name}: skipped — report already exists")
    except FetchError as e:
        reporter.update_feed(feed_name, "failed", error=str(e))
        return _error(f"{feed_name} fetch failed: {e}")
    except Exception as e:
        reporter.update_feed(feed_name, "failed", error=str(e))
        return _error(f"{feed_name} fetch error: {e}")


@tool(
    "enrich_feed",
    "Enrich/score feed data using AI (Haiku model). "
    "For ai-digest: scores articles and generates bilingual summaries. "
    "For others: categorizes, scores, and generates one-line summaries. "
    "Must call fetch_feed first. Stores enriched data internally.",
    {"feed_name": str},
)
async def enrich_feed_tool(args: dict[str, Any]) -> dict[str, Any]:
    feed_name = args["feed_name"]
    if feed_name not in VALID_FEEDS:
        return _error(f"Unknown feed: {feed_name}. Valid: {VALID_FEEDS}")

    feed_data = CONTEXT["data"].get(feed_name, {})
    fetched_json = feed_data.get("fetched")
    if not fetched_json:
        return _error(f"No fetched data for {feed_name}. Call fetch_feed first.")

    config = CONTEXT["configs"][feed_name]
    reporter: StatusReporter = CONTEXT["reporter"]
    reporter.update_feed(feed_name, "running", message="Enriching with AI...")

    try:
        enriched_json = await run_enrich(feed_name, config, fetched_json)
        CONTEXT["data"][feed_name]["enriched"] = enriched_json

        # Parse to get stats
        enriched = json.loads(enriched_json)
        if feed_name == "ai-digest":
            scored = json.loads(enriched.get("scored", "{}"))
            count = len(scored.get("top_articles", []))
            msg = f"Scored & summarized top {count} articles"
        else:
            items = enriched.get("enriched", [])
            count = len(items)
            msg = f"Enriched {count} items"

        reporter.update_feed(feed_name, "running", message=msg)
        return _text(f"{feed_name}: {msg}")

    except Exception as e:
        tb = traceback.format_exc()
        print(f"[enrich] {feed_name} error:\n{tb}", file=sys.stderr)
        reporter.update_feed(feed_name, "failed", error=str(e))
        return _error(f"{feed_name} enrichment failed: {e}")


@tool(
    "write_report",
    "Write the Obsidian markdown report for a feed. "
    "Runs the feed's write_reports.py with fetched + enriched data. "
    "Must call fetch_feed and enrich_feed first.",
    {"feed_name": str},
)
async def write_report_tool(args: dict[str, Any]) -> dict[str, Any]:
    feed_name = args["feed_name"]
    if feed_name not in VALID_FEEDS:
        return _error(f"Unknown feed: {feed_name}. Valid: {VALID_FEEDS}")

    feed_data = CONTEXT["data"].get(feed_name, {})
    fetched_json = feed_data.get("fetched")
    enriched_json = feed_data.get("enriched")
    if not fetched_json or not enriched_json:
        return _error(f"Missing data for {feed_name}. Call fetch_feed and enrich_feed first.")

    config = CONTEXT["configs"][feed_name]
    vault_path = CONTEXT["vault_path"]
    reporter: StatusReporter = CONTEXT["reporter"]
    reporter.update_feed(feed_name, "running", message="Writing report...")

    try:
        report_path = await run_write_reports(
            feed_name, config, vault_path, fetched_json, enriched_json
        )
        reporter.update_feed(
            feed_name, "success",
            message="Report generated",
            output_path=report_path,
        )
        return _text(f"{feed_name}: report written → {report_path}")

    except Exception as e:
        reporter.update_feed(feed_name, "failed", error=str(e))
        return _error(f"{feed_name} write failed: {e}")


@tool(
    "archive_old_reports",
    "Archive old reports for a feed (>14 days for daily, >14 weeks for weekly). "
    "Moves old files to the feed's archive/ subdirectory.",
    {"feed_name": str},
)
async def archive_old_reports_tool(args: dict[str, Any]) -> dict[str, Any]:
    feed_name = args["feed_name"]
    if feed_name not in VALID_FEEDS:
        return _error(f"Unknown feed: {feed_name}. Valid: {VALID_FEEDS}")

    config = CONTEXT["configs"][feed_name]
    try:
        archived = archive_old_reports(config)
        if archived:
            return _text(f"{feed_name}: archived {len(archived)} old reports: {', '.join(archived)}")
        return _text(f"{feed_name}: no old reports to archive")
    except Exception as e:
        return _error(f"{feed_name} archive failed: {e}")


@tool(
    "update_status",
    "Update the status display for a feed. Used to set custom messages visible in Home.md.",
    {"feed_name": str, "status": str, "message": str},
)
async def update_status_tool(args: dict[str, Any]) -> dict[str, Any]:
    feed_name = args["feed_name"]
    status = args.get("status", "running")
    message = args.get("message", "")

    reporter: StatusReporter = CONTEXT["reporter"]
    reporter.update_feed(feed_name, status, message=message)
    return _text(f"{feed_name}: status → {status} ({message})")


# ── MCP Server Factory ──────────────────────────────────────────────

def create_feed_tools_server():
    """Create MCP server with all feed tools."""
    return create_sdk_mcp_server(
        name="feed_tools",
        version="1.0.0",
        tools=[
            check_module_status_tool,
            check_existing_report_tool,
            fetch_feed_tool,
            enrich_feed_tool,
            write_report_tool,
            archive_old_reports_tool,
            update_status_tool,
        ],
    )

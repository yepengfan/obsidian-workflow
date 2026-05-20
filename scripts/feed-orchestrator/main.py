"""Feed Orchestrator — Agent SDK entry point.

Runs a Claude agent that orchestrates all 4 feed pipelines using custom tools.
The agent checks module status, fetches data, enriches via Haiku, writes reports,
and archives old files — then returns a human-readable summary.

Usage:
    python main.py --vault-path /path/to/vault
    bash load-env.sh  # (from Obsidian Shell Commands)
"""

import argparse
import asyncio
import sys
from pathlib import Path

import anyio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
)

from tools import init_context, create_feed_tools_server, CONTEXT
from status import StatusReporter

ORCHESTRATOR_PROMPT = """\
You are a feed orchestrator for an Obsidian vault. Your job is to generate all 4 feed reports.

## Feeds to Generate

1. **ai-digest** (daily) — AI/ML news from 92 RSS feeds
2. **github-trending** (daily) — Trending GitHub repositories
3. **engineering-blogs** (daily) — Top company engineering blog posts
4. **cc-plugins** (weekly) — Claude Code plugin discoveries

## Workflow

For EACH feed, follow these steps IN ORDER:

1. `check_module_status(feed_name)` — Skip if disabled
2. `check_existing_report(feed_name)` — Skip if report already exists
3. `fetch_feed(feed_name)` — Fetch raw data from sources
4. `enrich_feed(feed_name)` — Score and enrich with AI
5. `write_report(feed_name)` — Generate Obsidian markdown report
6. `archive_old_reports(feed_name)` — Clean up old reports

IMPORTANT: Process all 4 feeds. Do not stop after the first one.

If a feed is disabled or already exists, note it and move to the next feed.
If a feed fails at any step, log the error and continue with the remaining feeds.

## Output

After processing all feeds, provide a brief summary:
- For each feed: ✅ success (with file path), ⏭️ skipped, ⛔ disabled, or ❌ failed (with reason)
- Total: X generated, Y skipped, Z failed
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Feed Orchestrator")
    parser.add_argument(
        "--vault-path",
        type=Path,
        required=True,
        help="Path to the Obsidian vault root",
    )
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    vault_path = args.vault_path.resolve()

    if not vault_path.exists():
        print(f"ERROR: Vault path does not exist: {vault_path}", file=sys.stderr)
        return 1

    # Initialize shared context
    init_context(vault_path)
    reporter: StatusReporter = CONTEXT["reporter"]

    # Check concurrent run lock
    if reporter.check_concurrent_lock():
        print("ERROR: Another feed run is already in progress.", file=sys.stderr)
        return 1

    reporter.write_initial()
    print("[orchestrator] Starting feed generation...", file=sys.stderr)

    # Create MCP server with feed tools
    feed_server = create_feed_tools_server()

    # Tool names follow mcp__servername__toolname pattern
    tool_names = [
        "mcp__feed_tools__check_module_status",
        "mcp__feed_tools__check_existing_report",
        "mcp__feed_tools__fetch_feed",
        "mcp__feed_tools__enrich_feed",
        "mcp__feed_tools__write_report",
        "mcp__feed_tools__archive_old_reports",
        "mcp__feed_tools__update_status",
    ]

    options = ClaudeAgentOptions(
        mcp_servers={"feed_tools": feed_server},
        allowed_tools=tool_names,
        max_turns=40,
        permission_mode="acceptEdits",
        system_prompt=(
            "You are a feed pipeline orchestrator. Use the provided tools to "
            "generate feed reports. Be systematic: process each feed completely "
            "before moving to the next. Report results concisely."
        ),
    )

    summary = ""
    try:
        async for message in query(prompt=ORCHESTRATOR_PROMPT, options=options):
            if isinstance(message, AssistantMessage):
                # Log assistant reasoning to stderr for debugging
                for block in message.content:
                    if hasattr(block, "text") and block.text:
                        print(f"[agent] {block.text[:200]}", file=sys.stderr)
            elif isinstance(message, ResultMessage):
                if message.is_error:
                    summary = f"Agent error: {message.subtype}"
                    if message.errors:
                        summary += f" — {'; '.join(message.errors)}"
                    print(f"[orchestrator] {summary}", file=sys.stderr)
                else:
                    summary = message.result or "Completed (no summary)"
                    cost = message.total_cost_usd or 0
                    turns = message.num_turns
                    print(
                        f"[orchestrator] Done in {turns} turns, ${cost:.4f}",
                        file=sys.stderr,
                    )
    except KeyboardInterrupt:
        summary = "Interrupted by user"
        print(f"\n[orchestrator] {summary}", file=sys.stderr)
    except Exception as e:
        summary = f"Orchestrator error: {e}"
        print(f"[orchestrator] {summary}", file=sys.stderr)

    # Finalize status
    reporter.write_final(summary)

    # Print summary to stderr (Shell Commands captures this as notification)
    print(f"\n{summary}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(anyio.run(main))

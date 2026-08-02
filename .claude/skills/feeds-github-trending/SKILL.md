---
name: feeds-github-trending
description: >-
  Run the GitHub trending repos digest pipeline. Use for /feeds/github-trending.
disable-model-invocation: true
---

<!-- module: feeds-github-trending -->
> [!GUARD] Read `system/modules/feeds-github-trending/module.md`. If `enabled: false` → reply "⛔ Module **feeds-github-trending** is disabled. Enable it via `/module-toggle feeds-github-trending`." and STOP. Do NOT proceed.

---

Generate today's GitHub Trending report (or for a specified date).

This runs the hybrid Python + Claude Code pipeline defined in `scripts/github-trending/run.sh`:
  Step 0: Python fetches trending repos via GitHub Search API (new + active)
  Step 1: Claude Haiku categorizes, scores, and writes bilingual one-liners
  Step 2: Python assembles Obsidian markdown reports
  Step 3: Bash archives reports older than 14 days

## Instructions

1. Run the pipeline:
   ```bash
   bash scripts/github-trending/run.sh
   ```
   - The script is idempotent — if today's report already exists, it exits cleanly (exit 0 or 2).
   - Typical runtime: ~30-60 seconds (single Haiku call for enrichment).
   - The script outputs progress to stderr (`[trending] Step N: ...`). Stream these to the user as status updates.
   - Optional: set `GITHUB_TOKEN` env var for higher API rate limits (authenticated: 30 req/min vs 10 req/min unauthenticated).

2. Check the result:
   - **Success**: Report the generated file paths and key stats:
     - `Feeds/GitHub-Trending/{DATE}.md` (中文版)
     - `Feeds/GitHub-Trending/{DATE}-en.md` (English)
     - `Feeds/GitHub-Trending/Dashboard.md` (updated index)
     - Number of repos scanned / selected (from frontmatter)
   - **Already exists**: Tell the user today's report is already generated and link to it.
   - **Failure**: Show the error output and suggest checking `claude` CLI availability, network connectivity, or GitHub API rate limits.

3. After success, read the generated Chinese report file and give a brief summary of today's top 3 repos (the 🥇🥈🥉 entries) in 2-3 sentences.

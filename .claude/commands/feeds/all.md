<!-- wrapper: feeds-ai-digest, feeds-github-trending, feeds-engineering-blogs -->
Run all daily feed pipelines in parallel.

This is a convenience wrapper that runs all feed pipelines at once:
- **AI Daily Digest** (`scripts/ai-digest/run.sh`) — ~4-6 min
- **GitHub Trending** (`scripts/github-trending/run.sh`) — ~30-60s
- **Engineering Blogs** (`scripts/engineering-blogs/run.sh`) — ~30-60s

All pipelines are independent and idempotent.

## Instructions

1. **Check modules**: Read `system/modules/feeds-ai-digest/module.md`, `system/modules/feeds-github-trending/module.md`, and `system/modules/feeds-engineering-blogs/module.md`. Note which are enabled. If ALL are disabled → reply "⛔ All feed modules are disabled. Enable them via `/module-toggle`." and STOP.

2. **Run enabled pipelines in parallel** — launch a subagent for each enabled feed:

   - **AI Digest** (if enabled): spawn a subagent that runs `bash scripts/ai-digest/run.sh` and reports success/failure/already-exists with file paths.
   - **GitHub Trending** (if enabled): spawn a subagent that runs `bash scripts/github-trending/run.sh` and reports success/failure/already-exists with file paths.
   - **Engineering Blogs** (if enabled): spawn a subagent that runs `bash scripts/engineering-blogs/run.sh` and reports success/failure/already-exists with file paths.

   Run all subagents concurrently (`run_in_background=false`, send all Agent calls in one message). If only some modules are enabled, just run those.

3. **Report results** — after all complete, give a unified summary:

   For each feed, report one of:
   - ✅ **Success**: list generated files (`Feeds/AI-Daily/{DATE}.md`, etc.) and key stats
   - ⏭️ **Already exists**: link to today's existing report
   - ❌ **Failed**: show error and suggest fixes
   - ⛔ **Disabled**: note the module is off

4. **Highlights** — after reporting results, read any newly generated Chinese digest/report files and give a brief combined summary:
   - AI Digest: 2-3 sentences on today's `📝 今日看点`
   - GitHub Trending: 2-3 sentences on the top 5 repos (1️⃣–5️⃣)
   - Engineering Blogs: 2-3 sentences on the top 3 posts

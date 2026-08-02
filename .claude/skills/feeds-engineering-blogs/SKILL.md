---
name: feeds-engineering-blogs
description: >-
  Run the engineering blogs digest pipeline. Use for /feeds/engineering-blogs.
disable-model-invocation: true
---

<!-- module: feeds-engineering-blogs -->
> [!GUARD] Read `system/modules/feeds-engineering-blogs/module.md`. If `enabled: false` → reply "⛔ Module **feeds-engineering-blogs** is disabled. Enable it via `/module-toggle feeds-engineering-blogs`." and STOP. Do NOT proceed.

---

Generate today's Engineering Blogs report (or for a specified date).

This runs the hybrid Python + Claude Code pipeline defined in `scripts/engineering-blogs/run.sh`:
  Step 0: Python fetches 10 company engineering blog RSS feeds
  Step 1: Claude Haiku categorizes, scores (with high bar), and writes bilingual summaries
  Step 2: Python assembles Obsidian markdown reports
  Step 3: Bash archives reports older than 14 days

## Instructions

1. Run the pipeline:
   ```bash
   bash scripts/engineering-blogs/run.sh
   ```
   - The script is idempotent — if today's report already exists, it exits cleanly (exit 0 or 2).
   - Typical runtime: ~30-60 seconds (single Haiku call for enrichment).
   - The script outputs progress to stderr (`[eng-blogs] Step N: ...`). Stream these to the user as status updates.
   - No external Python dependencies needed (stdlib only).

2. Check the result:
   - **Success**: Report the generated file paths and key stats:
     - `Feeds/Engineering-Blogs/{DATE}.md` (中文版)
     - `Feeds/Engineering-Blogs/{DATE}-en.md` (English)
     - `Feeds/Engineering-Blogs/Dashboard.md` (updated index)
     - Number of articles scanned / selected (from frontmatter)
   - **Already exists**: Tell the user today's report is already generated and link to it.
   - **Failure**: Show the error output and suggest checking `claude` CLI availability or network connectivity.

3. After success, read the generated Chinese report file and give a brief summary of today's top 3 posts in 2-3 sentences.

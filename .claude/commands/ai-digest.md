Generate today's AI Daily Digest (or for a specified date).

This runs the same hybrid Python + Claude Code pipeline as the Home.md "Generate" button:
  Phase 0: Python fetches 92 Karpathy-curated RSS feeds + deduplicates
  Phase 1: Claude Haiku scores & selects top 15 articles
  Phase 2: Claude Haiku generates bilingual summaries (中文 + English)
  Phase 3: Python assembles Obsidian markdown reports
  Phase 4: Bash archives digests older than 14 days

## Instructions

1. Run the pipeline:
   ```bash
   bash scripts/ai-digest/run.sh
   ```
   - The script is idempotent — if today's digest already exists, it exits cleanly (exit 0 or 2).
   - Typical runtime: ~4-6 minutes (both phases use Haiku for speed).
   - The script outputs progress to stderr (`[digest] Step N: ...`). Stream these to the user as status updates.

2. Check the result:
   - **Success**: Report the generated file paths and key stats:
     - `Feeds/AI-Daily/{DATE}.md` (中文版)
     - `Feeds/AI-Daily/{DATE}-en.md` (English)
     - `Feeds/AI-Daily/Dashboard.md` (updated index)
     - Number of articles scanned / selected (from frontmatter)
   - **Already exists**: Tell the user today's digest is already generated and link to it.
   - **Failure**: Show the error output and suggest checking `claude` CLI availability or network connectivity.

3. After success, read the generated Chinese digest file and give a brief summary of today's highlights (the `📝 今日看点` section) in 2-3 sentences.

<!-- module: feeds-cc-plugins -->
> [!GUARD] Read `system/modules/feeds-cc-plugins/module.md`. If `enabled: false` → reply "⛔ Module **feeds-cc-plugins** is disabled. Enable it via `/module-toggle feeds-cc-plugins`." and STOP. Do NOT proceed.

---

Generate this week's Claude Code Plugins report (or skip if already generated).

This runs the hybrid Python + Claude Code pipeline defined in `scripts/cc-plugins/run.sh`:
  Step 0: Python fetches plugin repos via GitHub Search + npm Registry
  Step 1: Claude Haiku classifies (is_plugin gate), scores (4 dimensions), and writes bilingual summaries
  Step 2: Python assembles Obsidian weekly reports + updates state.json
  Step 3: Bash archives reports older than 14 weeks

## Instructions

1. Run the pipeline:
   ```bash
   bash scripts/cc-plugins/run.sh
   ```
   - The script is idempotent — if this week's report already exists, it exits with code 2.
   - Typical runtime: ~60-120 seconds (GitHub search + npm lookups + single Haiku call).
   - The script outputs progress to stderr (`[cc-plugins] Step N: ...`). Stream these to the user as status updates.
   - Optional: set `GITHUB_TOKEN` env var for higher API rate limits (authenticated: 30 req/min vs 10 req/min unauthenticated).

2. Check the result:
   - **Success**: Report the generated file paths and key stats:
     - `Feeds/CC-Plugins/{WEEK}.md` (中文版)
     - `Feeds/CC-Plugins/{WEEK}-en.md` (English)
     - `Feeds/CC-Plugins/Dashboard.md` (updated index)
     - Number of plugins scanned / new / updated (from frontmatter)
   - **Already exists (exit 2)**: Tell the user this week's report is already generated and link to it.
   - **Failure**: Show the error output and suggest checking `claude` CLI availability, network connectivity, or GitHub API rate limits.

3. After success, read the generated Chinese report file and give a brief summary:
   - How many new plugins were discovered and their top 3 (name + score + one-line description)
   - Any version updates detected
   - Total plugins now tracked in state.json

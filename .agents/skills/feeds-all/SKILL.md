---
name: feeds-all
description: >-
  Run all daily feed pipelines via the sequential feed orchestrator. Use for
  /feeds-all, or when generating all feeds at once.
disable-model-invocation: true
---

<!-- wrapper: feeds-ai-digest, feeds-github-trending, feeds-engineering-blogs -->
Run all daily feed pipelines via the unified orchestrator.

This convenience wrapper runs all three daily feeds in one invocation. The orchestrator processes enabled feeds **sequentially** (ai-digest → github-trending → engineering-blogs), skipping any whose report already exists today.

Typical runtime per feed:
- **AI Daily Digest** — ~4-10 min
- **GitHub Trending** — ~1-3 min
- **Engineering Blogs** — ~1-3 min

**Recommended** — unified orchestrator (supports `FEED_LLM_BACKEND`):
```bash
bash scripts/feed-orchestrator/load-env.sh
```
When `FEED_LLM_BACKEND` is unset, the backend is inferred: Cursor CLI if `agent` is on PATH (default — subscription auth doesn't expire), otherwise Anthropic if `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN` is set. Override explicitly with `FEED_LLM_BACKEND=anthropic` or `FEED_LLM_BACKEND=cursor`.

## Instructions

1. **Check modules**: Read `system/modules/feeds-ai-digest/module.md`, `system/modules/feeds-github-trending/module.md`, and `system/modules/feeds-engineering-blogs/module.md`. Note which are enabled. If ALL are disabled → reply "⛔ All feed modules are disabled. Enable them via `/module-toggle`." and STOP.

2. **Run enabled feeds** — prefer the unified orchestrator when all feeds are needed:

   **Option A (recommended)** — sequential orchestrator with pluggable LLM backend:
   ```bash
   bash scripts/feed-orchestrator/load-env.sh
   ```
   Runs each enabled feed one after another. Respects `FEED_LLM_BACKEND` (defaults to Cursor CLI when unset, falling back to Anthropic credentials).

   **Option B** — legacy per-feed `run.sh` scripts (Claude CLI only; each feed is a separate process and may be started in parallel manually):
   - **AI Digest** (if enabled): `bash scripts/ai-digest/run.sh`
   - **GitHub Trending** (if enabled): `bash scripts/github-trending/run.sh`
   - **Engineering Blogs** (if enabled): `bash scripts/engineering-blogs/run.sh`

   Use Option A unless the user explicitly wants legacy run.sh paths.

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

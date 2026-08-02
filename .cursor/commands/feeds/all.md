Run all daily feed pipelines via the feed orchestrator.

Uses `FEED_LLM_BACKEND` (default: `cursor`). Switch to Anthropic with:
```bash
FEED_LLM_BACKEND=anthropic bash scripts/feed-orchestrator/load-env.sh
```

## Instructions

1. **Check modules**: Read `system/modules/feeds-ai-digest/module.md`, `system/modules/feeds-github-trending/module.md`, and `system/modules/feeds-engineering-blogs/module.md`. Note which are enabled. If ALL disabled → reply "⛔ All feed modules are disabled." and STOP.

2. **Run orchestrator**:
   ```bash
   bash scripts/feed-orchestrator/load-env.sh
   ```
   - Default backend is Cursor CLI (`agent -p`), billed via Cursor subscription
   - Requires `agent` on PATH and `agent login` (or `CURSOR_API_KEY`)
   - Idempotent — skips feeds whose report already exists today
   - Typical runtime: ~5-10 min (cursor) or ~4-6 min (anthropic)

3. **Report results** — for each feed: ✅ generated / ⏭️ skipped / ❌ failed / ⛔ disabled

4. **Highlights** — read newly generated Chinese reports and summarize top items briefly

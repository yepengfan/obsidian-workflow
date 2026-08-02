Run all daily feed pipelines via the feed orchestrator.

The orchestrator runs enabled feeds **sequentially** (ai-digest → github-trending → engineering-blogs). Uses `FEED_LLM_BACKEND` with credential-based default when unset (Anthropic key → anthropic; else Cursor CLI if `agent` on PATH).

```bash
bash scripts/feed-orchestrator/load-env.sh
```

Override backend explicitly:
```bash
FEED_LLM_BACKEND=anthropic bash scripts/feed-orchestrator/load-env.sh
FEED_LLM_BACKEND=cursor bash scripts/feed-orchestrator/load-env.sh
```

## Instructions

1. **Check modules**: Read `system/modules/feeds-ai-digest/module.md`, `system/modules/feeds-github-trending/module.md`, and `system/modules/feeds-engineering-blogs/module.md`. Note which are enabled. If ALL disabled → reply "⛔ All feed modules are disabled." and STOP.

2. **Run orchestrator**:
   ```bash
   bash scripts/feed-orchestrator/load-env.sh
   ```
   - Backend inferred from credentials when unset (see above)
   - Idempotent — skips feeds whose report already exists today
   - Typical runtime: ~5-10 min total (varies by backend and feed count)

3. **Report results** — for each feed: ✅ generated / ⏭️ skipped / ❌ failed / ⛔ disabled

4. **Highlights** — read newly generated Chinese reports and summarize top items briefly

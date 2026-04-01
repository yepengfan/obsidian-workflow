<!-- module: feeds-podcast -->
> [!GUARD] Read `system/modules/feeds-podcast/module.md`. If `enabled: false` → reply "⛔ Module **feeds-podcast** is disabled. Enable it via `/module-toggle feeds-podcast`." and STOP. Do NOT proceed.

---

Process new podcast episodes from subscribed RSS feeds.

This runs the 5-step Python + Claude Code pipeline defined in `scripts/podcast/run.sh`:
  Step 0: Python fetches RSS feeds + downloads new episode audio (.mp3)
  Step 1: Python transcribes audio locally with mlx-whisper (large-v3-turbo) → .srt + transcript JSON
  Step 2: Claude scores transcript (4 weighted dimensions) + generates bilingual summary + key takeaways
  Step 3: Python generates Obsidian episode notes + refreshes Podcasts.md recommendation page
  Step 4: Python runs lifecycle management (archive listened episodes, clean up old audio)

## Instructions

1. Run the pipeline:
   ```bash
   bash scripts/podcast/run.sh
   ```
   - The script is idempotent — already-processed episodes (tracked in `state.json`) are skipped.
   - Transcription uses local Apple Silicon GPU; runtime depends on episode count and length.
   - Typical runtime: ~5-10 min per 1h episode. The script outputs progress to stderr. Stream these to the user as status updates.

2. Check the result:
   - **Success**: Report the key stats:
     - Number of new episodes discovered / processed
     - Episode names and their scores (e.g., "Lex Fridman #401 — Score: 8.4 ⭐")
     - File paths generated: `Podcasts/episodes/*.md`, `Podcasts/Podcasts.md`
     - Any episodes skipped (already processed, download errors, transcription errors)
   - **No new episodes**: Tell the user all feeds are up to date — no new episodes to process.
   - **Failure**: Show the error output. Common causes:
     - `mlx-whisper` not installed → `bash scripts/podcast/setup.sh`
     - `feedparser` not installed → `pip install feedparser` in the podcast venv
     - `claude` CLI not found → check PATH
     - `ANTHROPIC_API_KEY` not set → check environment

3. After success, read `Podcasts/Podcasts.md` and give the user a brief recommendation summary:
   - List any ⭐ Strongly Recommended (score 9-10) episodes by name
   - List 👍 Worth Listening (score 7-8) episodes by name and one-line summary
   - Mention total count of new episodes processed

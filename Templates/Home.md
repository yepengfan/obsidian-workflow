---
tags: template
for: Home
updated: 2026-05-22
---

%% Reference template for Home.md. Not used to create new notes — edit the live file directly. Update this file whenever the dashboard structure changes, and bump the `updated:` frontmatter date. Append a new dated `> [!note]` entry to Design Decisions when making structural changes. %%

## Design Decisions

> [!note] 2026-03-10 — Note creation button (navToday)
> - **Why note creation lives in Home.md**: Home.md is the primary entry point to the vault. Centralising note creation here (rather than relying solely on Templater or Calendar) ensures the full toolbar experience (priority buttons, project selectors) is always applied to new daily notes.
> - **H1 format**: Daily notes use `# DayName` only (e.g., `# Tuesday`). The date is already in the filename and `date:` frontmatter — repeating it in H1 is redundant. The `navToday` button writes `"# " + dayName` (not `"# " + dateStr + " " + dayName`).
> - **Year folder auto-creation**: If `Work/<year>/` does not yet exist, the button creates it before writing the note. This makes the first daily note of a new year seamless.
> - **Project sections**: The button reads `Work/Projects.md` frontmatter (`projects:` list) to generate `### ProjectName` subheadings in the new note. This keeps the task-grouping convention consistent without manual setup.
> - **Priority toolbar**: Embedded as a dataviewjs block inside the created note — gives quick-insert buttons for 🔴/🟠/🟡/🟢 task priorities and per-project task insertion/movement. Toolbar code is inlined at creation time (not a separate template file) to keep the note self-contained.
> - **Idempotent open**: If the note already exists, the button simply opens it rather than overwriting. Safe to click multiple times.
> - **No reference template syncing**: Home.md is a single bespoke file with no structural variants. A reference template is maintained here for design decision history only — there is no "live file + mirror" sync requirement like the Work Dashboard views.

> [!note] 2026-03-12 — Four-segment progress bar (carryover system)
> - **Four segments** (left→right, dark→light): done (solid accent) | carried-away/carry-out (yellow) | carried-in/carry-in (30% opacity accent) | open (gray background). Open always at far right.
> - **Carried-away detection**: `t.status === ">"` in the Tasks section (between `## Tasks` and `## Notes`). These are tasks forwarded to the next day.
> - **Carried-in detection**: Level-2 heading where `h.heading.includes("Carryover")`. Unchecked (`t.status === " "`) tasks between that line and `carryoverEndLine` (the next `##` heading, or EOF). The end bound prevents tasks in later sections from being mis-counted as carried-in.
> - **Open uses `t.status === " "`** (not `!t.completed`) to exclude `[>]` tasks from the open count. `inTasksSection` is also capped at `min(notesLine, carryoverLine)` so Carryover tasks aren't double-counted when `## Notes` is absent.
> - **Total**: `open + done + carriedAway + carriedIn` — all four segments sum to 100%.
> - **Count badges**: `N open` | `N ⬆️` (carry-out, yellow) | `N ➡️` (carry-in) | `N done` | `N total` — all 5 always shown; zeros are dimmed (opacity 0.35) for layout consistency. Fixed `width:4.8em` per badge reserves space for 2-digit numbers. Badge order mirrors bar order (left→right).

> [!note] 2026-03-18 — Remove AI Daily Digest Generate button
> - **Why**: The Generate button relied on the Shell Commands plugin to invoke `run.sh` as a detached background process (`&`). Obsidian's stripped environment prevented the `claude` CLI from authenticating, causing the pipeline to silently fail after Step 0. Errors were invisible since the background process output is not captured.
> - **Change**: Replaced the button + polling + spinner block with a static placeholder message directing users to run `/ai-digest` in Claude Code instead.
> - **Supersedes**: The 2026-03-18 timeout note (timeout logic removed along with the button).

> [!note] 2026-03-29 — Skills tab practice tracker links
> - **What**: Added a data-driven practice links section between the radar chart legend and the footer in the Skills tab.
> - **How**: Reads `tracker` field from each skill entry in `Profile/Skill Radar.md` frontmatter. Skills with a `tracker` path get a `📐 Name → Tracker →` row. Skills without `tracker` are skipped.
> - **Scalable**: Adding a new skill with a `tracker:` field in Skill Radar frontmatter automatically surfaces its link in the Skills tab — no Home.md edit needed.

> [!note] 2026-03-31 — Fix baseball card tilt on fast mouse entry
> - **Problem**: Two independent bugs. (A) Chromium 3D hit testing triggers spurious `mouseleave` on `cardWrap` when the card tilts — the rotated card surface no longer aligns with the wrapper's 2D bounding box, so the browser thinks the cursor left. (B) `endInteraction()`'s 600ms animation-restart timer is never cancelled — re-entering within 600ms causes the old timer to re-apply `bc-float`, overriding the tilt transform.
> - **Fix A**: Guard `mouseleave` with a bounding-rect check — verify `e.clientX/Y` is actually outside `cardWrap`'s rect before calling `endInteraction()`. Spurious leaves (cursor still inside) are ignored.
> - **Fix B**: Store the timer ID in `floatTimer`, clear it in `startInteraction()` on re-entry. Timer callback also nulls `floatTimer`.
> - **Also (v1)**: Snap transform to neutral + disable transitions + force reflow before re-enabling on entry. First `mousemove` deferred via `requestAnimationFrame`.

> [!note] 2026-05-21 — Generate Feeds button with Agent SDK orchestrator
> - **Why**: Replaced the disabled AI-only Shell Commands button (2026-03-18 removal) with a unified "Generate Feeds ▶" button that triggers all 4 feed pipelines (ai-digest, github-trending, engineering-blogs, cc-plugins) via a Claude Agent SDK orchestrator.
> - **Architecture**: Button calls Shell Command `shf4gf2026` → `load-env.sh` sources `~/.zshrc` for env vars → `main.py` runs Agent SDK `query()` loop with 7 custom MCP tools (check/fetch/enrich/write/archive/status). Enrichment uses Anthropic SDK + Haiku directly (no Claude CLI dependency), solving the original PATH failure.
> - **Status polling**: Button writes `Feeds/.feed-status.json` atomically (tmp+rename). Home.md polls every 3s via `app.vault.adapter.read()`, renders per-feed emoji badges (⏳/🔄/✅/⏭️/❌/⛔). Auto-stops when all feeds reach terminal state or 12-min timeout.
> - **Concurrent lock**: `StatusReporter.check_concurrent_lock()` refuses to start if running feeds < 15 min old in `.feed-status.json`.
> - **Supersedes**: 2026-03-18 removal note — button is back with a robust solution.

> [!note] 2026-05-21 — Split feeds into Daily + CC Plugins buttons
> - **Why**: cc-plugins is a weekly feed; the other 3 (ai-digest, github-trending, engineering-blogs) are daily. One button conflated cadences — users clicking "Generate Feeds" daily would unnecessarily re-run cc-plugins (which skips via idempotency check, but wastes an Agent SDK turn).
> - **Change**: Split into two buttons: "Daily Feeds ▶" (`shf4gf2026 --feeds ai-digest,github-trending,engineering-blogs`) and "CC Plugins ▶" (`shf5cp2026 --feeds cc-plugins`). Each triggers its own Shell Command with `--feeds` arg.
> - **Implementation**: `main.py` accepts `--feeds` (comma-separated). `StatusReporter` accepts `feed_names` param — `write_initial()` only initializes the active subset. Home.md uses a shared `createFeedButton()` factory; each button tracks only its own feeds' badges.
> - **Backwards compatible**: Running without `--feeds` still processes all 4 (default behavior).

> [!note] 2026-03-13 — Automatic carryover in navToday button
> - **Problem**: The create button generated clean daily notes without checking for unfinished tasks from the previous day. The `/daily` skill had carryover logic, but clicking the Home.md button did not.
> - **Solution**: After building the note content, the button now finds the most recent previous daily note (`Work/YYYY/YYYY-MM-DD.md` where basename < today), scans its `## Tasks` and `## 🔄 Carryover` sections for incomplete tasks (`- [ ]`), marks them as `- [>]` in the previous note, and appends a `## 🔄 Carryover` section to the new note with those tasks grouped by project.
> - **Task block logic**: Tasks are grouped into blocks (top-level + indented subtasks). Only blocks where the top-level task is incomplete are carried. Within a carried block, only `- [ ]` subtasks are included (completed `- [x]` subtasks are dropped).
> - **Code fence safety**: Uses the existing `fence` variable (`String.fromCharCode(96).repeat(3)`) to detect and skip code blocks when scanning headings and tasks, preventing false matches inside dataviewjs blocks.

> [!note] 2026-05-22 — Feed status badges reset daily
> - **Problem**: Status badges (✅ AI Digest, ✅ GitHub, ✅ Eng Blogs) persisted from yesterday's run. The on-load check only tested `data.completed_at` existence, not whether it was from today. New day showed stale green checkmarks despite no digest existing yet.
> - **Solution**: Compare `completed_at` date against today (using `sv-SE` locale for ISO format). Only render badges if the status is from today's run. Otherwise badges stay hidden until the user triggers a new run.


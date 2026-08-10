---
tags: template
for: Home
updated: 2026-08-11
---

%% Reference template for Home.md. Not used to create new notes — edit the live file directly. Update this file whenever the dashboard structure changes, and bump the `updated:` frontmatter date. Append a new dated `> [!note]` entry to Design Decisions when making structural changes. %%

## Design Decisions

> [!note] 2026-08-11 — Clickable bars in Algorithm weekly activity chart
> - **Why**: The `📝 最近做题` bar chart (Algorithm tab, `🏋️ 长期练习`) only visualized weekly problem counts — there was no way to jump from a bar to the log(s) behind it.
> - **Data**: The per-week aggregation loop now keeps the matching log pages (`weekLogs`), not just the summed count — `weeks.push({ start: ws, count: cnt, logs: weekLogs })`.
> - **Click target**: Algorithm logs are per-day, not per-week, so a week can match multiple daily log files. Each non-empty bar links to that week's **most recent** daily log (`[...wk.logs].sort((a,b) => dv.date(b.date).ts - dv.date(a.date).ts)[0]`), consistent with the "latest match" convention already used by the practice-plan roadmap dots elsewhere in `Home.md`.
> - **Implementation**: Bar element switches from a plain `<div>` to `class="internal-link" data-href="<log path>"` (same convention as the weekly activity dots and roadmap dots) when `wk.logs.length > 0`, so Obsidian's built-in internal-link click handling opens it with no extra JS listener. `title` tooltip shows the week range, count, and target log date. Zero-count weeks remain plain, non-interactive `<div>`s.
> - **Fix (same day)**: The `internal-link`/`data-href` anchor didn't respond to clicks in practice. Replaced with a plain `<div>` + `bar.addEventListener("click", () => app.workspace.openLinkText(target.file.path, "", false))` — the same direct-call pattern already used by the SD tab's "Planned" session cards — instead of relying on Obsidian's automatic internal-link click delegation.
> - **Pivot (same day)**: The click destination itself was wrong, not just non-functional — jumping to one arbitrary day's raw log loses the other days' problems when a week spans multiple logs. Once `Learning/Practice/Algorithm/Weekly View.md` (dedicated week-aggregated view, see its own module notes) existed, the bar now sets `app.__algoWeeklyView.selectedWeekStart = wk.start.toFormat("yyyy-MM-dd")` and navigates to that page instead of a daily log file. `Weekly View.md` already reads this same `app.__algoWeeklyView` state on load to restore the selected week (added for its own click-persistence fix), so no changes were needed there — both pages compute Monday-anchored week boundaries identically, so the date strings always match. The now-unused per-week `logs` array and "latest log" sort were removed from the aggregation loop, reverting to a plain `count`.

> [!note] 2026-08-08 — Flattened slash-command hints after commands→skills migration
> - **Why**: Vault-wide migration retired `.claude/commands/` in favor of `.claude/skills/<name>/SKILL.md` as the single source of truth for both Claude Code and Cursor. Nested paths (`/module/command`) no longer resolve — flat hyphenated names (`/module-command`) are now the only valid invocation form.
> - **Changed**: 3 hardcoded hint strings in dataviewjs blocks — Engineering Blogs empty-state (`/feeds/engineering-blogs` → `/feeds-engineering-blogs`), System Design tab empty-state (`/sysd/solve` → `/sysd-solve`), Frontend tab empty-state (`/frnt/solve` → `/frnt-solve`).
> - **Verified**: All 9 dataviewjs blocks in Home.md still pass `node --check` after the edit.

> [!note] 2026-08-07 — 📖 读书 card reads WeRead progress live (not a static snapshot)
> - **Problem**: The 读书 card's `WeRead N%` badge read `m.weread_progress` — a static frontmatter field in each `Learning/Books/<book>/meta.md`, hand-copied at onboarding. It never tracked the live WeRead plugin data, so the badge silently went stale as the user kept reading (values happened to match only by coincidence). There was no sync mechanism — it was a one-time copy.
> - **Fix**: Added `findWeReadProgress(meta)` helper (mirror of `findBookCover`, direction reversed): resolves `meta.weread_source` → the plugin-synced WeRead note → reads its frontmatter `progress` via `app.metadataCache.getFileCache(f)`, returning that as the single source of truth. Falls back to the static `meta.weread_progress` only when the source note can't be found. Badge line changed from `if (m.weread_progress) …` to `const wr = findWeReadProgress(m); if (wr) …`.
> - **Why this works without new fields**: Every reading book's `meta.md` already carries a `weread_source:` pointer to its WeRead note, and all pointers resolved to valid files. So `weread_progress` is demoted from sole source to fallback-only; no writeback script or hook needed.
> - **Consumers**: `weread_progress` had exactly one reader (this card) — verified by grep — so a live read here fully solves staleness. Contrast the sibling `## Reading → Currently Reading` section, which was already live (`dv.pages('"WeRead"')`); only this production-layer card used the frozen field.

> [!note] 2026-08-07 — 🧬 最近更新的 Atoms card in Algorithm tab
> - **Why**: Pattern cards already surfaced recently-updated cards via "📝 最近 Pattern Cards"; Atoms/ (原子技术) had no equivalent, making it hard to see recent atom activity from Home.
> - **Placement**: Inside the Algorithm tab's `lPanels["algo"]` block, directly below "📝 最近 Pattern Cards" and above "All patterns →". Same card layout (name link + subtitle line + date), but atoms have no `category`/`problems` fields, so the subtitle shows `Atom · used by N patterns` instead — `N` computed from `atom.file.inlinks.length` (Dataview auto-tracks `[[wikilink]]` backlinks from pattern cards' `## Composed Of` sections, no manual list to maintain).
> - **Visual differentiation**: Left border uses `#8E8CD8` (already in the category donut's color palette) instead of `var(--color-accent)`, so atom cards are distinguishable from pattern cards at a glance despite identical layout.
> - **Data source**: `dv.pages('"Learning/Practice/Algorithm/Atoms"').where(x => x.file.tags.includes("#leetcode/atom"))`, sorted by `updated` desc, sliced to top 5 — mirrors the existing pattern-card query exactly.

> [!note] 2026-07-15 — 📖 读书 widget in Learning section (book production progress)
> - **Placement**: Inside the `## Learning` dataviewjs block, between 📚 学习计划 and 🏋️ 长期练习. Distinct from the existing `## Reading` section — that reads the WeRead **capture** layer (raw highlights); this reads the **production** layer (`Learning/Books/*/meta.md` with `status: reading`), i.e. books upgraded into the Feynman/write workflow.
> - **Data source**: One card per book where `meta.status === "reading"` (shows all in-progress, sorted by `started` desc). Chapter progress scans `<book>/chapters/*.md` frontmatter — `feynman` field drives done/current: done = `feynman && feynman !== "not_started"`; current chapter = lowest-numbered chapter still `not_started`. `chapter !== undefined` filter excludes non-chapter files like `_README.md`.
> - **Backward compatibility**: Older book chapter skeletons (DDIA, TFS) predate the `feynman` field — they only have `status: unread`. Undefined `feynman` is falsy, so those correctly count as 0 done rather than all done. New books (via updated book_init flow) carry `feynman`/`write` fields.
> - **Card visuals**: Mirror the 学习计划 card (3px accent bar + title-link badge → MOC, archetype pill tech-ref/cognitive, `ChN / total` stat). Chapter dots reuse the weekly-activity dot style: Feynman-done = filled accent, current = dashed border, else muted. Each dot links to its chapter file.
> - **▶ 开始阅读 button**: `app.workspace.openLinkText(mocPath)` opens the book's MOC (so Claudian ingests it as `<linked_note>`), then `app.commands.executeCommandById("realclaudian:open-view")` opens the Claudian chat. **Constraint**: Claudian (realclaudian v2.0.34) registers no URI protocol and its commands take no args — a button cannot auto-send a prompt. The button gets you to "book + chat open"; the user types the reading command (e.g. "Ch1 费曼"). Verified command id `realclaudian:open-view` (name "Open chat view", callback `activateView()` which reuses or creates the view).
> - **Empty state**: No `status: reading` books → "No books in production — 说「我要开始读 XXX」启动一本。" Footer links to `Learning/Books/Books Index.md`.
> - **gitignore note**: `Learning/` book content is gitignored (private), but Dataview indexes the working tree directly, so the widget renders fine locally. The widget code lives in the committed `Home.md`.

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

> [!note] 2026-03-31 — Fix baseball card tilt on fast mouse entry
> - **Problem**: Two independent bugs. (A) Chromium 3D hit testing triggers spurious `mouseleave` on `cardWrap` when the card tilts — the rotated card surface no longer aligns with the wrapper's 2D bounding box, so the browser thinks the cursor left. (B) `endInteraction()`'s 600ms animation-restart timer is never cancelled — re-entering within 600ms causes the old timer to re-apply `bc-float`, overriding the tilt transform.
> - **Fix A**: Guard `mouseleave` with a bounding-rect check — verify `e.clientX/Y` is actually outside `cardWrap`'s rect before calling `endInteraction()`. Spurious leaves (cursor still inside) are ignored.
> - **Fix B**: Store the timer ID in `floatTimer`, clear it in `startInteraction()` on re-entry. Timer callback also nulls `floatTimer`.
> - **Also (v1)**: Snap transform to neutral + disable transitions + force reflow before re-enabling on entry. First `mousemove` deferred via `requestAnimationFrame`.

> [!note] 2026-05-21 — Generate Feeds button with Agent SDK orchestrator
> - **Why**: Replaced the disabled AI-only Shell Commands button (2026-03-18 removal) with a unified "Generate Feeds ▶" button that triggers all 3 feed pipelines (ai-digest, github-trending, engineering-blogs) via a Claude Agent SDK orchestrator.
> - **Architecture**: Button calls Shell Command `shf4gf2026` → `load-env.sh` sources `~/.zshrc` for env vars → `main.py` runs Agent SDK `query()` loop with 7 custom MCP tools (check/fetch/enrich/write/archive/status). Enrichment uses Anthropic SDK + Haiku directly (no Claude CLI dependency), solving the original PATH failure.
> - **Status polling**: Button writes `Feeds/.feed-status.json` atomically (tmp+rename). Home.md polls every 3s via `app.vault.adapter.read()`, renders per-feed emoji badges (⏳/🔄/✅/⏭️/❌/⛔). Auto-stops when all feeds reach terminal state or 12-min timeout.
> - **Concurrent lock**: `StatusReporter.check_concurrent_lock()` refuses to start if running feeds < 15 min old in `.feed-status.json`.
> - **Supersedes**: 2026-03-18 removal note — button is back with a robust solution.

> [!note] 2026-06-01 — Removed CC Plugins feed
> - **Why**: cc-plugins pipeline was unreliable (persistent `KeyError: 'category'` failures due to data flow mismatch between enrich.py filtering and write_reports.py merge logic). Removed entirely: scripts, module, reports, Home.md section, and feed-orchestrator references.

> [!note] 2026-03-13 — Automatic carryover in navToday button
> - **Problem**: The create button generated clean daily notes without checking for unfinished tasks from the previous day. The `/daily` skill had carryover logic, but clicking the Home.md button did not.
> - **Solution**: After building the note content, the button now finds the most recent previous daily note (`Work/YYYY/YYYY-MM-DD.md` where basename < today), scans its `## Tasks` and `## 🔄 Carryover` sections for incomplete tasks (`- [ ]`), marks them as `- [>]` in the previous note, and appends a `## 🔄 Carryover` section to the new note with those tasks grouped by project.
> - **Task block logic**: Tasks are grouped into blocks (top-level + indented subtasks). Only blocks where the top-level task is incomplete are carried. Within a carried block, only `- [ ]` subtasks are included (completed `- [x]` subtasks are dropped).
> - **Code fence safety**: Uses the existing `fence` variable (`String.fromCharCode(96).repeat(3)`) to detect and skip code blocks when scanning headings and tasks, preventing false matches inside dataviewjs blocks.

> [!note] 2026-05-22 — Feed status badges reset daily + frontmatter race fix
> - **Problem 1**: Status badges persisted from yesterday's run — on-load check only tested `completed_at` existence, not date.
> - **Problem 2**: Article/repo counts showed `?/?` because `dv.page()` races with Dataview indexing on newly created files.
> - **Problem 3**: Badges could show stale intermediate state if Dataview re-rendered the block during a feed run.
> - **Solution**: (1) Compare `completed_at` date against today before rendering badges. (2) Replace `dv.page()` with `parseFM(content)` — parses YAML frontmatter directly from file content already read via `app.vault.read()`, eliminating Dataview dependency. (3) Added final re-read of status file on completion to ensure badges reflect latest state.

> [!note] 2026-06-02 — Fix "本周" stats using rolling 7-day window instead of calendar week
> - **Problem**: Algorithm tab stats line used `today.minus({ days: 7 })` (rolling 7-day window) while the bar chart used calendar week (Mon-Sun). This caused the "本周 X 题" number to disagree with the current week's bar.
> - **Solution**: Changed `weekAgo` to compute current week's Monday (`todayD.weekday === 1 ? todayD : todayD.minus({ days: todayD.weekday - 1 })`), matching the bar chart's calendar week logic. Changed "本月" (rolling 30 days) to "上月" (previous calendar month, e.g. May 1–31). Applied to both desktop and mobile code paths.


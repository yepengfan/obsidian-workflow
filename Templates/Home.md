---
tags: template
for: Home
updated: 2026-03-18
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

> [!note] 2026-03-13 — Automatic carryover in navToday button
> - **Problem**: The create button generated clean daily notes without checking for unfinished tasks from the previous day. The `/daily` skill had carryover logic, but clicking the Home.md button did not.
> - **Solution**: After building the note content, the button now finds the most recent previous daily note (`Work/YYYY/YYYY-MM-DD.md` where basename < today), scans its `## Tasks` and `## 🔄 Carryover` sections for incomplete tasks (`- [ ]`), marks them as `- [>]` in the previous note, and appends a `## 🔄 Carryover` section to the new note with those tasks grouped by project.
> - **Task block logic**: Tasks are grouped into blocks (top-level + indented subtasks). Only blocks where the top-level task is incomplete are carried. Within a carried block, only `- [ ]` subtasks are included (completed `- [x]` subtasks are dropped).
> - **Code fence safety**: Uses the existing `fence` variable (`String.fromCharCode(96).repeat(3)`) to detect and skip code blocks when scanning headings and tasks, preventing false matches inside dataviewjs blocks.


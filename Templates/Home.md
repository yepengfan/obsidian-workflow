---
tags: template
for: Home
updated: 2026-03-12
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
> - **Four segments** (left→right, dark→light): done (solid accent) | carried-in (30% opacity accent) | carried-away (yellow) | open (gray background). Open always at far right.
> - **Carried-away detection**: `t.status === ">"` in the Tasks section (between `## Tasks` and `## Notes`). These are tasks forwarded to the next day.
> - **Carried-in detection**: Level-2 heading where `h.heading.includes("Carryover")`. Unchecked (`t.status === " "`) tasks between that line and `carryoverEndLine` (the next `##` heading, or EOF). The end bound prevents tasks in later sections from being mis-counted as carried-in.
> - **Open uses `t.status === " "`** (not `!t.completed`) to exclude `[>]` tasks from the open count. `inTasksSection` is also capped at `min(notesLine, carryoverLine)` so Carryover tasks aren't double-counted when `## Notes` is absent.
> - **Total**: `open + done + carriedAway + carriedIn` — all four segments sum to 100%.
> - **Count badges**: `N open` | `N ➡️` (carry-in) | `N ⬆️` (carry-out, yellow) | `N done` | `N total` — all 5 always shown; zeros are dimmed (opacity 0.35) for layout consistency. Fixed `width:4.8em` per badge reserves space for 2-digit numbers.


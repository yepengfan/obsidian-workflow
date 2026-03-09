---
tags: template
for: Home
updated: 2026-03-10
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


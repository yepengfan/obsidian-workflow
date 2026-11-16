---
tags: template
for: Work/Work Dashboard
updated: 2026-11-17
---

%% Reference template for Work/Work Dashboard.md. Not used to create new notes — edit the live file directly. Update this file whenever the dashboard structure changes, and bump the `updated:` frontmatter date. Append a new dated `> [!note]` entry to Design Decisions when making structural changes. %%

## Design Decisions

> [!note] 2026-11-17 - Shared module dashboard
> - Work uses the shared Home visual language, searchable projects and dated notes, and explicit weekly/monthly navigation. The /work-daily copy action preserves the existing rollover workflow.

> [!note] 2026-03-10 — Initial structure
> - **Section order**: Today → Weekly View → Monthly View → Year Navigation → Projects → Brownbag Sessions. Rationale: most urgent/actionable context first (today's tasks), then broader time horizons, then reference tables.
> - **Glance-first philosophy**: Weekly and Monthly sections show summary cards on the dashboard, not full task lists. Full lists live in dedicated files ([[Work/Weekly View]] and [[Work/Monthly View]]). Keeps the dashboard fast to scan.
> - **Tag filter**: All queries use `p.file.tags.includes("#work-daily")` instead of `p.tags?.includes(...)`. The `p.tags` property is unreliable in Dataview — `p.file.tags` is the canonical array populated from YAML frontmatter.
> - **Today section**: Promoted to its own top-level section (not embedded in Weekly View) so there is a single, always-visible entry point to today's daily note. Shows open tasks inline up to 8, with "+N more" overflow.
> - **Weekly View glance**: Shows week-level aggregate only (progress bar + open/done counts). Today detail is intentionally omitted here to avoid duplication with the Today section above.
> - **Monthly View glance**: Per-day rows sorted descending (most recent first) so today appears at the top without scrolling. Stats bar (Notes / Open / Done / Done%) gives month health at a glance.
> - **Ghost card (no note yet)**: The "No note for today yet" card opens the note path via `openLinkText` — this navigates but does not create the file. Full note creation logic (with toolbar and project sections) lives in Home.md's today button. Use Home.md or the Calendar plugin to create a new daily note.

---

## Reference Content

---
tags: dashboard
cssclasses: [dashboard, module-dashboard]
---

```dataviewjs
await dv.view("scripts/dashboard/work", { app });
```

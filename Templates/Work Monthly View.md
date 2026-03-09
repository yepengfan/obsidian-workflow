---
tags: template
for: Work/Monthly View
updated: 2026-03-10
---

%% Reference template for Work/Monthly View.md. Not used to create new notes — edit the live file directly. Update this file whenever the view structure changes, and bump the `updated:` frontmatter date. Append a new dated `> [!note]` entry to Design Decisions when making structural changes. %%

## Design Decisions

> [!note] 2026-03-10 — Initial structure
> - **Why a separate file**: Month-level detail (all tasks per day, plus the all-time incomplete backlog) is high-volume. Keeping it out of the Work Dashboard avoids overwhelming the main view while still being one click away.
> - **Section order**: This Month → All Incomplete Tasks. Rationale: current month context first; the all-incomplete backlog is a secondary review tool (e.g., end-of-month cleanup).
> - **This Month — sort order**: Ascending by date (`asc`) so the month reads chronologically top to bottom, matching how daily notes are written. Contrast with the Monthly glance on Work Dashboard which sorts descending so "Today" appears first in the compact card.
> - **All Incomplete Tasks**: Sorted descending (most recent first) so the most relevant incomplete work surfaces at the top. Acts as a global backlog view — not limited to the current month.
> - **Per-day grouping in This Month**: Uses `dv.header(4, ...)` to render each day as a sub-heading with its task list underneath. This gives the full chronological breakdown for retrospectives and end-of-month review, which is the primary use case for opening this view.
> - **Back link**: `← [[Work Dashboard]]` at the top for quick return navigation.
> - **Tag filter**: `p.file.tags.includes("#work-daily")` — see Work Dashboard decisions for rationale.

---

## Reference Content

%% The sections below mirror the live file. Keep in sync when making structural changes. %%

### This Month

```dataviewjs
const today = dv.date("today");
const monthStr = today.toFormat("yyyy-MM");

const pages = dv.pages('"Work"')
    .where(p => p.file.tags.includes("#work-daily"))
    .where(p => {
        const d = dv.date(p.date);
        return d && d.toFormat("yyyy-MM") === monthStr;
    })
    .sort(p => p.date, "asc");

if (pages.length > 0) {
    for (const page of pages) {
        const tasks = page.file.tasks;
        if (tasks.length > 0) {
            dv.header(4, page.file.link + " " + (page.day || ""));
            dv.taskList(tasks, false);
        }
    }
} else {
    dv.paragraph("No work notes this month yet.");
}
```

### All Incomplete Tasks

```dataviewjs
const pages = dv.pages('"Work"')
    .where(p => p.file.tags.includes("#work-daily"))
    .sort(p => p.date, "desc");

const tasks = pages.file.tasks.where(t => !t.completed);
if (tasks.length > 0) {
    dv.taskList(tasks, true);
} else {
    dv.paragraph("No outstanding tasks!");
}
```

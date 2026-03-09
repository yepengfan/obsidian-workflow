---
tags: template
for: Work/Weekly View
updated: 2026-03-10
---

%% Reference template for Work/Weekly View.md. Not used to create new notes — edit the live file directly. Update this file whenever the view structure changes. %%

## Design Decisions

> [!note] 2026-03-10 — Initial structure
> - **Why a separate file**: Weekly detail (full task lists) is too verbose for the main dashboard. Splitting into a dedicated file keeps the Work Dashboard lean (glance-only) while still providing drill-down access via `Open Weekly View →`.
> - **Section order**: Today → This Week Incomplete → This Week Completed. Rationale: what needs action now comes first; completed tasks are a separate review section below.
> - **Today section**: Shows full `dv.taskList` (all tasks, not filtered). The intent is to open this view when you want to work, so seeing everything — including completed — gives full context. The dashboard's Today section only shows open tasks for quick scanning.
> - **Incomplete/Completed split**: Kept as separate sections (not grouped by day) so incomplete items are a single consolidated list — easier to prioritise across days without jumping between headings.
> - **Back link**: `← [[Work Dashboard]]` at the top for quick return navigation.
> - **Tag filter**: `p.file.tags.includes("#work-daily")` — see Work Dashboard decisions for rationale.

---

## Reference Content

%% The sections below mirror the live file. Keep in sync when making structural changes. %%

### Today

```dataviewjs
const today = dv.date("today").toFormat("yyyy-MM-dd");
const todayPage = dv.page("Work/" + today.slice(0, 4) + "/" + today);
if (todayPage) {
    dv.taskList(todayPage.file.tasks, false);
} else {
    dv.paragraph("No note for today yet. Click today's date in the Calendar to create one.");
}
```

### This Week — Incomplete

```dataviewjs
const today = dv.date("today");
const dow = today.weekday; // 1=Mon, 7=Sun
const weekStart = today.minus({days: dow - 1});
const weekEnd = weekStart.plus({days: 6});

const pages = dv.pages('"Work"')
    .where(p => p.file.tags.includes("#work-daily"))
    .where(p => {
        const d = dv.date(p.date);
        return d && d >= weekStart && d <= weekEnd;
    })
    .sort(p => p.date, "asc");

const tasks = pages.file.tasks.where(t => !t.completed);
if (tasks.length > 0) {
    dv.taskList(tasks, true);
} else {
    dv.paragraph("All caught up this week!");
}
```

### This Week — Completed

```dataviewjs
const today = dv.date("today");
const dow = today.weekday;
const weekStart = today.minus({days: dow - 1});
const weekEnd = weekStart.plus({days: 6});

const pages = dv.pages('"Work"')
    .where(p => p.file.tags.includes("#work-daily"))
    .where(p => {
        const d = dv.date(p.date);
        return d && d >= weekStart && d <= weekEnd;
    })
    .sort(p => p.date, "asc");

const tasks = pages.file.tasks.where(t => t.completed);
if (tasks.length > 0) {
    dv.taskList(tasks, true);
} else {
    dv.paragraph("No completed tasks this week yet.");
}
```

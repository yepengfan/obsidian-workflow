---
tags: template
for: Tasks/Board
updated: 2026-11-17
---

%% Reference template for Tasks/Board.md. Not used to create new notes — edit the live file directly. Update this file whenever the view structure changes, and bump the `updated:` frontmatter date. Append a new dated `> [!note]` entry to Design Decisions when making structural changes. %%

## Design Decisions

> [!note] 2026-11-17 - Shared dashboard shell
> - Task capture and editing share Home navigation and styling, with labeled inputs and a matrix that stacks in narrow panes. Task records and movement semantics are preserved.

> [!note] 2026-11-17 - Complete task workbench
> - Capture, quadrant movement with undo, and per-task editing now render through `scripts/dashboard/tasks/view.js`. Home shows a read-only summary.


> [!note] 2026-09-14 — Mobile-friendly matrix (app.isMobile)
> - **Single-column grid** on phone (`app.isMobile`): `grid-template-columns: 1fr`, tighter gap (8px) and cell padding (8px / min-height 56px). Desktop keeps 2×2, 10px gap, 10px / 88px cells.
> - **Short quadrant titles** on mobile (`Q1 重要·紧急` …) so headers fit a narrow column; desktop keeps the parentheticals (立刻做 / 安排做 / 压缩 / 减少).
> - **Larger tap targets** on mobile only: filter pills, ✎, drawer inputs, area pills, save/delete/cancel. Title input uses `min-width:100%` so it wraps onto its own row. Logic (bucketing, urgency, attachEdit write-back, stale-guard, matrix `editable=false` vs 任务列表 `editable=true`) is unchanged.

> [!note] 2026-09-14 — Edit moved to a dedicated 任务列表 section (matrix read-only)
> - **Matrix = read-only visualization**: `renderTasks(host, list, withDomainFilter, editable)` — the Q1–Q4 + Unclassified cards are now rendered with `editable=false`, so no `✎` on the matrix.
> - **任务列表 区**: a single section below the matrix (separated by a top border) renders **all** open tasks with `editable=true`. Each entry shows a quadrant chip (`quadOf`: Q1/Q2/Q3/Q4/U) + due + domain, and carries the `✎` edit/delete drawer. This is the one place to modify a task.
> - **Rationale**: per user — task edits belong on the individual entry, not spread across the board's quadrant cards. Matrix stays a clean panorama; checkboxes still complete tasks in place.

> [!note] 2026-09-14 — Inline edit/delete on the board; Home task → open board
> - **Home**: matrix cards are now click-through — clicking a task (not its checkbox) opens `Tasks/Board.md`. Home stays capture + overview (add composer + read-only matrix); editing lives on the board.
> - **Board**: each task li gets a `✎` (`attachEdit`) that toggles an inline drawer prefilled from the **raw** line at `t.line` (parses `⭐` / `📅 date` / `#task/<area>` / title, preserves indent + `[status]`). Fields: title, Work/Life/Other/— area pills (— drops the domain → Unclassified), ⭐ toggle, `type=date` due, 保存 / 删除 / 取消.
> - **Write**: Save rebuilds the line and replaces it at `t.line`; Delete splices it. Both re-read the file and abort with a Notice if that line changed since the drawer opened (stale-guard). `vault.modify` retriggers the board's own dataviewjs so the card re-buckets.

> [!note] 2026-09-14 — Initial structure
> - **Vault-wide matrix**: Eisenhower 2×2 lives in `Tasks/Board.md` (not Work daily notes). The board does not query `Work/` — it only reads tasks on this page.
> - **SoT is `## Tasks` in the live file**: Open tasks are authored under `## Tasks`. Checking them off / moving them to `## Done` is the source of truth; the DataviewJS matrix is a view.
> - **Urgency from 📅 / Dataview `t.due`**: Urgent = due date exists and `dv.date(t.due) <= today+7 days` (`endOf("day")`, rolling one week, including overdue). Raising urgency requires a due date.
> - **Important = ⭐ in text**: Importance is human-marked in the task text, not a Dataview field.
> - **Domain = task tags** `#task/work` `#task/life` `#task/other` via `t.tags` (strip leading `#`). File-tag filter elsewhere is `p.file.tags.includes("#tag")`; here domain is per-task.
> - **Unclassified = no domain tag**: Always rendered full-width below the grid (planning hygiene). Domain filter pills apply only to Q1–Q4; unclassified stays visible.
> - **Filter pills All / Work / Life / Other**: Default All. Toggle `style.display` on `[data-domain]` rows — no page reload.
> - **Open tasks**: `t.status === " "` (not `!t.completed`) so in-progress `[>]` is excluded from the matrix.
> - **Ignore `## Done`**: Only tasks with `t.line` between the `## Tasks` and `## Done` H2s are included.

---

## Reference Content

%% The sections below mirror the live file. Keep in sync when making structural changes. %%

---
tags: [task-board]
cssclasses: [dashboard, module-dashboard, task-board-page]
---

```dataviewjs
const { Notice, Menu } = require("obsidian");
const shared = { app, title: "Task Board", icon: "task", description: "Capture tasks and decide what deserves your attention." };
await dv.view("scripts/dashboard/ui", shared);
await dv.view("scripts/dashboard/tasks", { app, Notice, Menu, container: shared.ui.content });
```

## Tasks

## Done

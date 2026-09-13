---
name: task-add
description: >-
  Add a task to Tasks/Board.md with area, importance, and optional due date. Use for /task-add.
disable-model-invocation: true
---

<!-- module: task-board -->
> [!GUARD] Read `system/modules/task-board/module.md`. If `enabled: false` → reply "⛔ Module **task-board** is disabled. Enable it via `/module-toggle task-board`." and STOP. Do NOT proceed.

---

Add one open task to `Tasks/Board.md`. Usage: `/task-add` or `/task-add <title>`.

**Gitignored:** `Tasks/` is gitignored. Use `ls` / `test -f` / Read — not Glob/Grep.

**Do not** scan `Work/` daily notes. Do not ingest old work tasks.

## Line format

Single line, this order:

`- [ ] ⭐ 📅 YYYY-MM-DD <title> #task/<area>`

- Omit ⭐ if not important.
- Omit 📅 if no due (not urgent). Never write the word "urgent" on the line.
- Domain tag required for classified tasks: `#task/work` `#task/life` `#task/other` (or `#task/<custom>` if the user names another area).
- Date strictly `YYYY-MM-DD`.

**Urgency (reports only):** due exists AND due ≤ today+7 days (rolling one week, including overdue; use actual current date). Important = has ⭐. Unclassified = open task under `## Tasks` with no `#task/` tag.

**Quadrants:** Q1 = ⭐ + urgent · Q2 = ⭐ + not urgent · Q3 = no ⭐ + urgent · Q4 = no ⭐ + not urgent · Unclassified = no `#task/` tag.

**Open tasks:** `- [ ]` only. Ignore `- [x]` and `- [>]`.

## Steps

1. **Guard** — follow the GUARD callout above.

2. **Ensure board** — `test -d Tasks || mkdir -p Tasks`. If `Tasks/Board.md` is missing, **do not copy the whole template file** (it contains Design Decisions). Build the live file as:
   - YAML frontmatter `tags: [task-board]`
   - then the body under `## Reference Content` in `Templates/Task Board.md`, starting at `# Task Board` through `## Done` (skip the `%% The sections below… %%` comment).
   Ensure `## Tasks` and `## Done` exist.

3. **Collect** (do not invent):
   - Title: from `$ARGUMENTS` or ask.
   - Area: work / life / other / custom name.
   - Important: yes/no (⭐).
   - Due: `YYYY-MM-DD` or empty.

4. **Urgent without due** — if the user wants Q1/Q3 (urgent) but gives no due date, ASK for a due date. Never mark urgent without 📅.

5. **Write** — insert the line immediately under `## Tasks` (after the heading line, before `## Done`). Do **not** insert into a dataviewjs fence. When locating headings, skip fenced code blocks.

6. **Report** — resulting quadrant (Q1–Q4 or Unclassified) and the exact line written.

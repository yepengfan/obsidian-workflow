---
name: task-board
description: >-
  Panorama, classify, and rearrange open tasks on Tasks/Board.md. Use for /task-board.
disable-model-invocation: true
---

<!-- module: task-board -->
> [!GUARD] Read `system/modules/task-board/module.md`. If `enabled: false` → reply "⛔ Module **task-board** is disabled. Enable it via `/module-toggle task-board`." and STOP. Do NOT proceed.

---

Operate on the live Eisenhower board at `Tasks/Board.md`. Usage: `/task-board` with optional natural-language sub-intent (classify / rearrange / overview).

**Gitignored:** `Tasks/` is gitignored. Use `ls` / `test -f` / Read — not Glob/Grep.

**Do not** scan `Work/` daily notes. Do not ingest old work tasks.

**UI:** tell the user to open `Tasks/Board.md` (or Home → Task Board) for the matrix. Do **not** dump a fake ASCII art matrix as the main UI.

## Line format

`- [ ] ⭐ 📅 YYYY-MM-DD <title> #task/<area>`

- Omit ⭐ if not important. Omit 📅 if no due.
- Domain: `#task/work` `#task/life` `#task/other` or `#task/<custom>`.
- Date strictly `YYYY-MM-DD`. Never write "urgent" on the line.

**Urgency (reports only):** due exists AND due ≤ today+7 days (rolling one week, including overdue; use actual current date). Important = has ⭐. Unclassified = open task under `## Tasks` with no `#task/` tag.

**Quadrants:** Q1 = ⭐ + urgent · Q2 = ⭐ + not urgent · Q3 = no ⭐ + urgent · Q4 = no ⭐ + not urgent · Unclassified = no `#task/` tag.

**Open tasks:** `- [ ]` only. Ignore `- [x]` and `- [>]`.

## Steps

1. **Guard** — follow the GUARD callout above.

2. **Ensure board** — `test -d Tasks || mkdir -p Tasks`. If `Tasks/Board.md` is missing, **do not copy the whole template file** (it contains Design Decisions). Build the live file as:
   - YAML frontmatter `tags: [task-board]`
   - then the body under `## Reference Content` in `Templates/Task Board.md`, starting at `# Task Board` through `## Done` (skip the `%% The sections below… %%` comment).
   Ensure `## Tasks` and `## Done` exist.

3. **Parse** — Read `Tasks/Board.md`. Collect open tasks under `## Tasks` (stop at `## Done`). Skip fenced code blocks when scanning headings. Do not parse tasks inside dataviewjs fences.

4. **Panorama** — print a table: domain, ⭐, due, derived quadrant, text.

5. **Classify** — if any Unclassified: list them and ask the user to classify (area + important + optional due), then write tags/⭐/📅 back onto those lines.

6. **Rearrange** — if the user wants a task moved, ONLY edit ⭐ and/or 📅. Promoting to urgent requires a due date (ask if missing). Demoting urgency = remove 📅 or push due past today+7.

7. **Reorder** — reorder lines under `## Tasks` only if the user asks, and only within the requested quadrant. Keep all tasks; just sort those lines.

8. **Health** — summarize counts by quadrant and by domain. If Q2 count is 0 and Q1 count >= 1, mention 效能在第二象限.

9. **Point to board** — remind the user to open `Tasks/Board.md` (or Home → Task Board) to see the matrix.

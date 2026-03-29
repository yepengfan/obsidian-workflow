<!-- module: work -->
> [!GUARD] Read `system/modules/work/module.md`. If `enabled: false` → reply "⛔ Module **work** is disabled. Enable it via `/module-toggle work`." and STOP. Do NOT proceed.

---

Create today's work daily note in `Work/<YYYY>/` and carry over any unfinished tasks from the previous work daily note.

## Step 1 — Determine dates

- Today: $CURRENT_DATE (format `YYYY-MM-DD`, day name `DayName`)
- Previous work daily note: scan `Work/<YYYY>/` (where `<YYYY>` is the current year) for the most recent `.md` file with a date **before** today (skip weekends only if no file exists for them — use the most recent file that actually exists). If today is the first day of a new year, also check `Work/<YYYY-1>/`.

## Step 2 — Find unfinished tasks in the previous note

Read the previous work daily note. Scan for **all unchecked tasks** (`- [ ] …`) that appear **between `## Tasks` and `## Notes`** (the main tasks section), including nested sub-tasks. Do **not** scan tasks inside `## Notes` or any other section. Group them by their parent `### ProjectName` heading. Ignore tasks under a `## 🔄 Carryover` section (those are already carried-over items — don't double-carry).

Keep track of:
- Which `### ProjectName` each task belongs to
- The full task line (including any emoji priority prefix and indentation for sub-tasks)
- The previous note's filename (e.g. `2026-03-11`) for attribution

## Step 3 — Create (or open) today's note

**Path**: `Work/<YYYY>/<YYYY-MM-DD>.md`

**If the file does NOT exist**, create it using the template below.

**If the file already exists**, read it and skip to Step 4.

Template for new note:
```
---
date: <YYYY-MM-DD>
day: <DayName>
tags: work-daily
---

# <DayName>

## Tasks

```dataviewjs
const file = app.workspace.getActiveFile();
const config = dv.page("Work/Projects");
const projects = (config?.projects || []).map(String);
const prios = [
  { e: "🔴", l: "Urgent" }, { e: "🟠", l: "High" },
  { e: "🟡", l: "Medium" }, { e: "🟢", l: "Low" },
];
let sel = projects[0] || "";

const w = dv.container.createEl("div", {
  attr: { style: "display:flex;align-items:center;gap:6px;flex-wrap:wrap;padding:4px 0;" }
});

// Project selector
const pbs = [];
for (const p of projects) {
  const a = p === sel;
  const b = w.createEl("button", { text: p, attr: {
    style: `padding:3px 12px;border-radius:6px;font-size:0.82em;font-weight:600;cursor:pointer;border:1px solid ${a ? "var(--interactive-accent)" : "var(--background-modifier-border)"};background:${a ? "var(--interactive-accent)" : "var(--background-secondary)"};color:${a ? "var(--text-on-accent)" : "var(--text-normal)"};`
  }});
  pbs.push({ b, p });
  b.addEventListener("click", () => {
    sel = p;
    pbs.forEach(x => {
      const on = x.p === p;
      x.b.style.background = on ? "var(--interactive-accent)" : "var(--background-secondary)";
      x.b.style.color = on ? "var(--text-on-accent)" : "var(--text-normal)";
      x.b.style.borderColor = on ? "var(--interactive-accent)" : "var(--background-modifier-border)";
    });
  });
}

w.createEl("span", { text: "\u2502", attr: { style: "color:var(--text-faint);" } });

// Priority buttons — click to insert task under selected project
for (const pr of prios) {
  const b = w.createEl("button", { text: pr.e + " " + pr.l, attr: {
    title: pr.l,
    style: "padding:3px 10px;border-radius:6px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.82em;"
  }});
  b.addEventListener("click", async () => {
    if (!sel || !file) return;
    const content = await app.vault.read(file);
    const lines = content.split("\n");
    const task = "- [ ] " + pr.e + " ";
    let target;
    let headIdx = -1;
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].trim() === "### " + sel) { headIdx = i; break; }
    }
    if (headIdx >= 0) {
      let ins = headIdx + 1, repl = -1;
      for (let j = headIdx + 1; j < lines.length; j++) {
        const t = lines[j].trim();
        if (t.startsWith("### ") || t.startsWith("## ")) break;
        if (t === "- [ ]" && repl < 0) repl = j;
        ins = j;
      }
      if (repl >= 0) {
        lines[repl] = lines[repl].replace("- [ ]", task);
        target = repl;
      } else {
        lines.splice(ins + 1, 0, task);
        target = ins + 1;
      }
    } else {
      let noteIdx = lines.length;
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].trim() === "## Notes") { noteIdx = i; break; }
      }
      lines.splice(noteIdx, 0, "### " + sel, "", task, "");
      target = noteIdx + 2;
    }
    await app.vault.modify(file, lines.join("\n"));
    setTimeout(() => {
      const ed = app.workspace.activeEditor?.editor;
      if (ed) { ed.setCursor({ line: target, ch: task.length }); ed.focus(); }
    }, 150);
    new Notice("Added " + pr.e + " " + pr.l + " task to " + sel);
  });
}

w.createEl("span", { text: "\u2502", attr: { style: "color:var(--text-faint);" } });

// Sort button — reorder tasks by priority within selected project
const sortBtn = w.createEl("button", { text: "\u2195 Sort", attr: {
  title: "Sort tasks by priority",
  style: "padding:3px 10px;border-radius:6px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.82em;"
}});
sortBtn.addEventListener("click", async () => {
  if (!sel || !file) return;
  const content = await app.vault.read(file);
  const lines = content.split("\n");
  const rank = { "\u{1F534}": 0, "\u{1F7E0}": 1, "\u{1F7E1}": 2, "\u{1F7E2}": 3 };
  let headIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim() === "### " + sel) { headIdx = i; break; }
  }
  if (headIdx < 0) return;
  let endIdx = lines.length;
  for (let j = headIdx + 1; j < lines.length; j++) {
    const t = lines[j].trim();
    if (t.startsWith("### ") || t.startsWith("## ")) { endIdx = j; break; }
  }
  function getRank(line) {
    const rank = { "🔴": 0, "🟠": 1, "🟡": 2, "🟢": 3 };
    for (const [emoji, r] of Object.entries(rank)) {
      if (line.includes(emoji)) return r;
    }
    return 4;
  }
  function sortTaskLines(taskLines, baseIndent) {
    const groups = [], leading = [], trailing = [];
    let cur = null, seenTask = false;
    for (const line of taskLines) {
      const trimmed = line.trim();
      const indent = line.search(/\S/);
      if (trimmed.startsWith("- [") && indent === baseIndent) {
        seenTask = true;
        cur = { head: line, children: [], rank: getRank(trimmed) };
        groups.push(cur);
      } else if (cur && trimmed !== "") {
        cur.children.push(line);
      } else if (!seenTask) {
        leading.push(line);
      } else {
        trailing.push(line);
      }
    }
    groups.sort((a, b) => a.rank - b.rank);
    for (const g of groups) {
      if (g.children.length > 0) {
        const childIndent = g.children[0].search(/\S/);
        if (childIndent > baseIndent) g.children = sortTaskLines(g.children, childIndent);
      }
    }
    return [...leading, ...groups.flatMap(g => [g.head, ...g.children]), ...trailing];
  }
  const sectionLines = lines.slice(headIdx + 1, endIdx);
  const sorted = sortTaskLines(sectionLines, 0);
  await app.vault.modify(file, [...lines.slice(0, headIdx + 1), ...sorted, ...lines.slice(endIdx)].join("\n"));
  new Notice("Sorted " + sel + " tasks by priority");
});
` `` `

## Notes

```
**IMPORTANT when writing the file**: The template above uses ` `` ` as a placeholder to avoid nesting code fences inside this instruction block. When writing the actual note to disk, replace every ` `` ` with three backtick characters (` ``` `). The note must contain a real fenced code block — ```` ```dataviewjs ```` opening and ```` ``` ```` closing — for the toolbar to render in Obsidian.

## Step 4 — Add Carryover section (if there are unfinished tasks)

If there are **no unfinished tasks** in the previous note → skip this step entirely, output a note saying "No carryover tasks found."

If unfinished tasks exist:

**4a. Update today's note** — Append a `## 🔄 Carryover` section at the end of the file (only if it doesn't already exist). Group tasks under their original `### ProjectName` headings. Include all sub-tasks with their original indentation. Add a small attribution line before the tasks:

```
## 🔄 Carryover

> Carried over from [[Work/<YYYY>/<prev-date>]] — <N> tasks across <M> projects

### ProjectName
- [ ] task text here
	- [ ] sub-task (if any)

### AnotherProject
- [ ] another task
```

**4b. Mark tasks in the previous note** — In the previous note's file:
- Top-level carried-over tasks: replace `- [ ]` with `- [>]` **and** append ` ➡️ [[Work/<YYYY>/<today-date>]]` to the line.
- Nested sub-tasks: replace `- [ ]` with `- [>]` only — **do not** append the wikilink to sub-tasks (the parent already carries it).

Example transformation in previous note:
```
Before:
- [ ] 🟡 4 articles to read
	- [ ] 🟡 openai harness engineering: https://...
	- [ ] 🟡 martin fowler: https://...

After:
- [>] 🟡 4 articles to read ➡️ [[Work/2026/2026-03-13]]
	- [>] 🟡 openai harness engineering: https://...
	- [>] 🟡 martin fowler: https://...
```

## Step 5 — Report

After all operations, report:
- Whether the note was created or already existed
- How many tasks were carried over (or "no carryover tasks")
- Which projects had carryover tasks
- Confirm that the previous note was updated with `[>]` markers

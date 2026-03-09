---
tags: template
for: Work/Work Dashboard
updated: 2026-03-10
---

%% Reference template for Work/Work Dashboard.md. Not used to create new notes — edit the live file directly. Update this file whenever the dashboard structure changes. %%

## Design Decisions

> [!note] 2026-03-10 — Initial structure
> - **Section order**: Today → Weekly View → Monthly View → Year Navigation → Projects → Brownbag Sessions. Rationale: most urgent/actionable context first (today's tasks), then broader time horizons, then reference tables.
> - **Glance-first philosophy**: Weekly and Monthly sections show summary cards on the dashboard, not full task lists. Full lists live in dedicated files ([[Work/Weekly View]] and [[Work/Monthly View]]). Keeps the dashboard fast to scan.
> - **Tag filter**: All queries use `p.file.tags.includes("#work-daily")` instead of `p.tags?.includes(...)`. The `p.tags` property is unreliable in Dataview — `p.file.tags` is the canonical array populated from YAML frontmatter.
> - **Today section**: Promoted to its own top-level section (not embedded in Weekly View) so there is a single, always-visible entry point to today's daily note. Shows open tasks inline up to 8, with "+N more" overflow.
> - **Weekly View glance**: Shows week-level aggregate only (progress bar + open/done counts). Today detail is intentionally omitted here to avoid duplication with the Today section above.
> - **Monthly View glance**: Per-day rows sorted descending (most recent first) so today appears at the top without scrolling. Stats bar (Notes / Open / Done / Done%) gives month health at a glance.

---

## Reference Content

%% The sections below mirror the live file. Keep in sync when making structural changes. %%

### Today

```dataviewjs
const today = dv.date("today");
const todayStr = today.toFormat("yyyy-MM-dd");
const year = today.toFormat("yyyy");
const notePath = `Work/${year}/${todayStr}`;
const todayPage = dv.page(notePath);
const container = dv.el("div", "");

const header = container.createEl("div", { attr: { style: "display:flex;align-items:center;gap:8px;margin-bottom:8px;" } });
header.innerHTML = `<a class="internal-link" data-href="${notePath}" style="font-weight:700;font-size:0.88em;color:var(--interactive-accent);text-decoration:none;">${today.toFormat("yyyy-MM-dd cccc")}</a>`;

if (todayPage) {
  const open = todayPage.file.tasks.where(t => !t.completed);
  const done = todayPage.file.tasks.where(t => t.completed);
  const total = open.length + done.length;

  const barWrap = container.createEl("div", { attr: { style: "height:5px;background:var(--background-modifier-border);border-radius:3px;overflow:hidden;margin-bottom:8px;" } });
  if (total > 0) barWrap.createEl("div", { attr: { style: `height:100%;width:${Math.round(done.length/total*100)}%;background:var(--interactive-accent);border-radius:3px;` } });

  const cs = "font-size:0.72em;padding:1px 7px;border-radius:10px;background:var(--background-primary);border:1px solid var(--background-modifier-border);white-space:nowrap;";
  const badges = container.createEl("div", { attr: { style: "display:flex;gap:6px;margin-bottom:10px;" } });
  if (open.length > 0) badges.createEl("span", { text: `${open.length} open`, attr: { style: cs + "color:var(--text-muted);" } });
  if (done.length > 0) badges.createEl("span", { text: `${done.length} done`, attr: { style: cs + "color:var(--interactive-accent);" } });
  if (total === 0) badges.createEl("span", { text: "no tasks", attr: { style: cs + "color:var(--text-faint);" } });

  if (open.length === 0) {
    container.createEl("div", { text: "✓ All tasks complete", attr: { style: "font-size:0.82em;color:var(--interactive-accent);" } });
  } else {
    for (const t of open.array().slice(0, 8)) {
      const row = container.createEl("div", { attr: { style: "font-size:0.82em;color:var(--text-normal);padding:3px 0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;border-bottom:1px solid var(--background-modifier-border);" } });
      row.textContent = "· " + t.text;
    }
    if (open.length > 8) {
      container.createEl("div", { text: `+ ${open.length - 8} more`, attr: { style: "font-size:0.72em;color:var(--text-faint);padding-top:4px;" } });
    }
  }
} else {
  const ghost = container.createEl("div", {
    attr: { style: "border:1px dashed var(--interactive-accent);border-radius:8px;padding:10px 14px;background:var(--background-secondary);font-size:0.82em;color:var(--interactive-accent);opacity:0.7;cursor:pointer;" }
  });
  ghost.textContent = "No note for today yet — click to open";
  ghost.addEventListener("click", () => app.workspace.openLinkText(notePath, "", false));
}

container.createEl("div", { attr: { style: "margin-top:8px;font-size:0.85em;" } }).innerHTML =
  `<a class="internal-link" data-href="${notePath}">Open today's note →</a>`;
```

### Weekly View (glance)

```dataviewjs
const today = dv.date("today");
const dow = today.weekday;
const weekStart = today.minus({ days: dow - 1 });
const weekEnd = weekStart.plus({ days: 6 });

const pages = dv.pages('"Work"')
  .where(p => p.file.tags.includes("#work-daily"))
  .where(p => { const d = dv.date(p.date); return d && d >= weekStart && d <= weekEnd; })
  .sort(p => p.date, "asc");

const container = dv.el("div", "");
container.createEl("div", {
  text: weekStart.toFormat("MMM dd") + " – " + weekEnd.toFormat("MMM dd"),
  attr: { style: "font-size:0.78em;color:var(--text-muted);margin-bottom:8px;font-weight:600;" }
});

const weekOpen = pages.file.tasks.where(t => !t.completed).length;
const weekDone = pages.file.tasks.where(t => t.completed).length;
const weekTotal = weekOpen + weekDone;

const summary = container.createEl("div", { attr: { style: "display:flex;align-items:center;gap:10px;padding:6px 0;" } });
const barWrap = summary.createEl("div", { attr: { style: "flex:1;height:5px;background:var(--background-modifier-border);border-radius:3px;overflow:hidden;" } });
if (weekTotal > 0) barWrap.createEl("div", { attr: { style: `height:100%;width:${Math.round(weekDone/weekTotal*100)}%;background:var(--interactive-accent);border-radius:3px;` } });
const cs = "font-size:0.72em;padding:1px 7px;border-radius:10px;background:var(--background-primary);border:1px solid var(--background-modifier-border);white-space:nowrap;";
summary.createEl("span", { text: `${weekOpen} open`, attr: { style: cs + "color:var(--text-muted);" } });
summary.createEl("span", { text: `${weekDone} done`, attr: { style: cs + "color:var(--interactive-accent);" } });

container.createEl("div", { attr: { style: "margin-top:6px;font-size:0.85em;" } }).innerHTML =
  `<a class="internal-link" data-href="Work/Weekly View">Open Weekly View →</a>`;
```

### Monthly View (glance)

```dataviewjs
const today = dv.date("today");
const monthStr = today.toFormat("yyyy-MM");
const monthLabel = today.toFormat("MMMM yyyy");

const pages = dv.pages('"Work"')
  .where(p => p.file.tags.includes("#work-daily"))
  .where(p => { const d = dv.date(p.date); return d && d.toFormat("yyyy-MM") === monthStr; })
  .sort(p => p.date, "desc");

const container = dv.el("div", "");
container.createEl("div", {
  text: monthLabel,
  attr: { style: "font-size:0.78em;color:var(--text-muted);margin-bottom:8px;font-weight:600;" }
});

const totalNotes = pages.length;
const allOpen = pages.file.tasks.where(t => !t.completed).length;
const allDone = pages.file.tasks.where(t => t.completed).length;
const allTotal = allOpen + allDone;
const pct = allTotal > 0 ? Math.round(allDone / allTotal * 100) : 0;

const statsRow = container.createEl("div", { attr: { style: "display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px;" } });
for (const [num, label] of [[totalNotes, "Notes"], [allOpen, "Open"], [allDone, "Done"], [pct + "%", "Done %"]]) {
  const s = statsRow.createEl("div", { attr: { style: "padding:6px 14px;background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:8px;text-align:center;min-width:54px;" } });
  s.createEl("div", { text: String(num), attr: { style: "font-size:1.1em;font-weight:700;line-height:1.2;" } });
  s.createEl("div", { text: label, attr: { style: "font-size:0.65em;color:var(--text-muted);" } });
}

const todayStr = today.toFormat("yyyy-MM-dd");
for (const page of pages) {
  const d = dv.date(page.date);
  const isToday = d.toFormat("yyyy-MM-dd") === todayStr;
  const open = page.file.tasks.where(t => !t.completed).length;
  const done = page.file.tasks.where(t => t.completed).length;
  const total = open + done;
  const row = container.createEl("div", {
    attr: { style: `display:flex;align-items:center;gap:8px;padding:5px 10px;border-radius:6px;margin-bottom:3px;background:var(--background-secondary);border:1px solid ${isToday ? "var(--interactive-accent)" : "var(--background-modifier-border)"};` }
  });
  const dateEl = row.createEl("a", {
    cls: "internal-link",
    attr: { "data-href": page.file.path, style: `font-size:0.8em;min-width:90px;text-decoration:none;font-weight:${isToday ? "700" : "400"};color:${isToday ? "var(--interactive-accent)" : "var(--text-normal)"};white-space:nowrap;` }
  });
  dateEl.textContent = isToday ? "Today" : d.toFormat("MM-dd ccc");
  const barWrap = row.createEl("div", { attr: { style: "flex:1;height:5px;background:var(--background-modifier-border);border-radius:3px;overflow:hidden;" } });
  if (total > 0) barWrap.createEl("div", { attr: { style: `height:100%;width:${Math.round(done/total*100)}%;background:var(--interactive-accent);border-radius:3px;` } });
  const cs = "font-size:0.7em;padding:1px 6px;border-radius:4px;background:var(--background-primary);white-space:nowrap;";
  if (open > 0) row.createEl("span", { text: `${open} open`, attr: { style: cs + "color:var(--text-muted);" } });
  if (done > 0) row.createEl("span", { text: `${done} done`, attr: { style: cs + "color:var(--interactive-accent);" } });
  if (total === 0) row.createEl("span", { text: "no tasks", attr: { style: cs + "color:var(--text-faint);" } });
}

if (pages.length === 0) {
  container.createEl("p", { text: "No work notes this month yet.", attr: { style: "color:var(--text-muted);font-size:0.85em;" } });
}
container.createEl("div", { attr: { style: "margin-top:8px;font-size:0.85em;" } }).innerHTML =
  `<a class="internal-link" data-href="Work/Monthly View">Open Monthly View →</a>`;
```

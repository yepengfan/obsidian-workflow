---
cssclasses:
  - dashboard
banner: "![[home.jpg]]"
banner_x: 0.5
banner_y: 0
---

## Work

```dataviewjs
const row = dv.container.createEl("div", { attr: { style: "display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:4px;" } });

// Navigation buttons
const navDash = row.createEl("button", {
  text: "Work Dashboard",
  attr: { style: "padding:8px 18px;border:1px solid var(--background-modifier-border);border-radius:8px;background:var(--background-secondary);color:var(--text-normal);cursor:pointer;font-size:0.88em;" }
});
navDash.addEventListener("click", () => app.workspace.openLinkText("Work/Work Dashboard", "", false));

const navToday = row.createEl("button", {
  text: dv.date("today").toFormat("yyyy-MM-dd"),
  attr: { style: "padding:8px 18px;border:1px solid var(--background-modifier-border);border-radius:8px;background:var(--background-secondary);color:var(--text-normal);cursor:pointer;font-size:0.88em;" }
});
navToday.addEventListener("click", async () => {
  const today = dv.date("today");
  const dateStr = today.toFormat("yyyy-MM-dd");
  const dayName = today.toFormat("cccc");
  const year = today.toFormat("yyyy");
  const notePath = `Work/${year}/${dateStr}.md`;

  // If the note already exists, just open it
  if (app.vault.getAbstractFileByPath(notePath)) {
    await app.workspace.openLinkText(notePath, "", false);
    return;
  }

  // Ensure year folder exists
  const folder = `Work/${year}`;
  if (!app.vault.getAbstractFileByPath(folder)) {
    await app.vault.createFolder(folder);
  }

  // Read active projects from Work/Projects.md
  const configFile = app.metadataCache.getFirstLinkpathDest("Work/Projects", "");
  const projects = [];
  if (configFile) {
    const cache = app.metadataCache.getFileCache(configFile);
    if (cache?.frontmatter?.projects) {
      for (const p of cache.frontmatter.projects) {
        projects.push(String(p));
      }
    }
  }

  // Build daily note content with priority toolbar
  const fence = String.fromCharCode(96).repeat(3);
  const toolbarCode = [
    'const file = app.workspace.getActiveFile();',
    'const config = dv.page("Work/Projects");',
    'const projects = (config?.projects || []).map(String);',
    'const prios = [',
    '  { e: "\u{1F534}", l: "Urgent" }, { e: "\u{1F7E0}", l: "High" },',
    '  { e: "\u{1F7E1}", l: "Medium" }, { e: "\u{1F7E2}", l: "Low" },',
    '];',
    'let sel = projects[0] || "";',
    '',
    'const w = dv.container.createEl("div", {',
    '  attr: { style: "display:flex;align-items:center;gap:6px;flex-wrap:wrap;padding:4px 0;" }',
    '});',
    '',
    '// Project selector',
    'const pbs = [];',
    'for (const p of projects) {',
    '  const a = p === sel;',
    '  const b = w.createEl("button", { text: p, attr: {',
    '    style: `padding:3px 12px;border-radius:6px;font-size:0.82em;font-weight:600;cursor:pointer;border:1px solid ${a ? "var(--interactive-accent)" : "var(--background-modifier-border)"};background:${a ? "var(--interactive-accent)" : "var(--background-secondary)"};color:${a ? "var(--text-on-accent)" : "var(--text-normal)"};`',
    '  }});',
    '  pbs.push({ b, p });',
    '  b.addEventListener("click", () => {',
    '    sel = p;',
    '    pbs.forEach(x => {',
    '      const on = x.p === p;',
    '      x.b.style.background = on ? "var(--interactive-accent)" : "var(--background-secondary)";',
    '      x.b.style.color = on ? "var(--text-on-accent)" : "var(--text-normal)";',
    '      x.b.style.borderColor = on ? "var(--interactive-accent)" : "var(--background-modifier-border)";',
    '    });',
    '  });',
    '}',
    '',
    'w.createEl("span", { text: "\\u2502", attr: { style: "color:var(--text-faint);" } });',
    '',
    '// Priority buttons — click to insert task under selected project',
    'for (const pr of prios) {',
    '  const b = w.createEl("button", { text: pr.e + " " + pr.l, attr: {',
    '    title: pr.l,',
    '    style: "padding:3px 10px;border-radius:6px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.82em;"',
    '  }});',
    '  b.addEventListener("click", async () => {',
    '    if (!sel || !file) return;',
    '    const content = await app.vault.read(file);',
    '    const lines = content.split("\\n");',
    '    const task = "- [ ] " + pr.e + " ";',
    '    let target;',
    '    let headIdx = -1;',
    '    for (let i = 0; i < lines.length; i++) {',
    '      if (lines[i].trim() === "### " + sel) { headIdx = i; break; }',
    '    }',
    '    if (headIdx >= 0) {',
    '      let ins = headIdx + 1, repl = -1;',
    '      for (let j = headIdx + 1; j < lines.length; j++) {',
    '        const t = lines[j].trim();',
    '        if (t.startsWith("### ") || t.startsWith("## ")) break;',
    '        if (t === "- [ ]" && repl < 0) repl = j;',
    '        ins = j;',
    '      }',
    '      if (repl >= 0) {',
    '        lines[repl] = lines[repl].replace("- [ ]", task);',
    '        target = repl;',
    '      } else {',
    '        lines.splice(ins + 1, 0, task);',
    '        target = ins + 1;',
    '      }',
    '    } else {',
    '      let noteIdx = lines.length;',
    '      for (let i = 0; i < lines.length; i++) {',
    '        if (lines[i].trim() === "## Notes") { noteIdx = i; break; }',
    '      }',
    '      lines.splice(noteIdx, 0, "### " + sel, "", task, "");',
    '      target = noteIdx + 2;',
    '    }',
    '    await app.vault.modify(file, lines.join("\\n"));',
    '    setTimeout(() => {',
    '      const ed = app.workspace.activeEditor?.editor;',
    '      if (ed) { ed.setCursor({ line: target, ch: task.length }); ed.focus(); }',
    '    }, 150);',
    '    new Notice("Added " + pr.e + " " + pr.l + " task to " + sel);',
    '  });',
    '}',
    '',
    'w.createEl("span", { text: "\\u2502", attr: { style: "color:var(--text-faint);" } });',
    '',
    '// Sort button — reorder tasks by priority within selected project',
    'const sortBtn = w.createEl("button", { text: "\\u2195 Sort", attr: {',
    '  title: "Sort tasks by priority",',
    '  style: "padding:3px 10px;border-radius:6px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.82em;"',
    '}});',
    'sortBtn.addEventListener("click", async () => {',
    '  if (!sel || !file) return;',
    '  const content = await app.vault.read(file);',
    '  const lines = content.split("\\n");',
    '  const rank = { "\\u{1F534}": 0, "\\u{1F7E0}": 1, "\\u{1F7E1}": 2, "\\u{1F7E2}": 3 };',
    '  let headIdx = -1;',
    '  for (let i = 0; i < lines.length; i++) {',
    '    if (lines[i].trim() === "### " + sel) { headIdx = i; break; }',
    '  }',
    '  if (headIdx < 0) return;',
    '  let endIdx = lines.length;',
    '  for (let j = headIdx + 1; j < lines.length; j++) {',
    '    const t = lines[j].trim();',
    '    if (t.startsWith("### ") || t.startsWith("## ")) { endIdx = j; break; }',
    '  }',
    '',
    '  // Recursive sort: group tasks at each indent level, sort by priority, recurse into children',
    '  function getRank(line) {',
    '    for (const [emoji, r] of Object.entries(rank)) {',
    '      if (line.includes(emoji)) return r;',
    '    }',
    '    return 4;',
    '  }',
    '',
    '  function sortTaskLines(taskLines, baseIndent) {',
    '    const groups = [];',
    '    const leading = [];',
    '    const trailing = [];',
    '    let cur = null;',
    '    let seenTask = false;',
    '    for (const line of taskLines) {',
    '      const trimmed = line.trim();',
    '      const indent = line.search(/\\S/);',
    '      if (trimmed.startsWith("- [") && indent === baseIndent) {',
    '        seenTask = true;',
    '        cur = { head: line, children: [], rank: getRank(trimmed) };',
    '        groups.push(cur);',
    '      } else if (cur && trimmed !== "") {',
    '        cur.children.push(line);',
    '      } else if (!seenTask) {',
    '        leading.push(line);',
    '      } else {',
    '        trailing.push(line);',
    '      }',
    '    }',
    '    groups.sort((a, b) => a.rank - b.rank);',
    '    for (const g of groups) {',
    '      if (g.children.length > 0) {',
    '        const childIndent = g.children[0].search(/\\S/);',
    '        if (childIndent > baseIndent) {',
    '          g.children = sortTaskLines(g.children, childIndent);',
    '        }',
    '      }',
    '    }',
    '    const result = [...leading];',
    '    for (const g of groups) { result.push(g.head, ...g.children); }',
    '    result.push(...trailing);',
    '    return result;',
    '  }',
    '',
    '  const sectionLines = lines.slice(headIdx + 1, endIdx);',
    '  const sorted = sortTaskLines(sectionLines, 0);',
    '  const newLines = [...lines.slice(0, headIdx + 1), ...sorted, ...lines.slice(endIdx)];',
    '  await app.vault.modify(file, newLines.join("\\n"));',
    '  new Notice("Sorted " + sel + " tasks by priority");',
    '});',
  ].join("\n");

  let content = [
    "---",
    "date: " + dateStr,
    "day: " + dayName,
    "tags: work-daily",
    "---",
    "",
    "# " + dateStr + " " + dayName,
    "",
    "## Tasks",
    "",
    fence + "dataviewjs",
    toolbarCode,
    fence,
    "",
  ].join("\n");

  // Add a heading for each active project
  for (const p of projects) {
    content += `### ${p}\n\n- [ ] \n\n`;
  }

  content += "## Notes\n\n";

  await app.vault.create(notePath, content);
  await app.workspace.openLinkText(notePath, "", false);
});

// Zettel capture button — creates a new timestamped note in Inbox/
const btn = row.createEl("button", {
  text: "+ Zettel",
  attr: {
    style: "margin-left:auto;padding:8px 18px;background:var(--interactive-accent);color:var(--text-on-accent);border-radius:8px;font-weight:600;font-size:0.88em;border:none;cursor:pointer;white-space:nowrap;"
  }
});
btn.addEventListener("click", async () => {
  if (!app.vault.getAbstractFileByPath("Inbox")) {
    await app.vault.createFolder("Inbox");
  }
  const ts = dv.date("now").toFormat("yyyy-MM-dd-HHmmss");
  const path = `Inbox/${ts}.md`;
  if (app.vault.getAbstractFileByPath(path)) return;
  await app.vault.create(path, "");
  await app.workspace.openLinkText(path, "", false);
});
```

```dataviewjs
const today = dv.date("today");
const dow = today.weekday;
const weekStart = today.minus({ days: dow - 1 });
const weekEnd = weekStart.plus({ days: 6 });

const pages = dv.pages('"Work"')
  .where(p => p.file.tags.includes("#work-daily"))
  .where(p => {
    const d = dv.date(p.date);
    return d && d >= weekStart && d <= weekEnd;
  })
  .sort(p => p.date, "desc");

const container = dv.el("div", "");

// Week label
const weekLabel = weekStart.toFormat("MMM dd") + " – " + weekEnd.toFormat("MMM dd");
container.createEl("div", {
  text: weekLabel,
  attr: { style: "font-size:0.78em;color:var(--text-muted);margin-bottom:6px;font-weight:600;" }
});

const todayStr = today.toFormat("yyyy-MM-dd");
const hasTodayNote = pages.some(p => dv.date(p.date).toFormat("yyyy-MM-dd") === todayStr);

function renderRow(rowEl, labelText, isToday, open, done, total, href) {
  // Date label
  const dateEl = rowEl.createEl("a", {
    cls: "internal-link",
    attr: { "data-href": href, style: `font-size:0.82em;font-weight:${isToday ? "700" : "400"};min-width:75px;text-decoration:none;color:${isToday ? "var(--interactive-accent)" : "var(--text-normal)"};` }
  });
  dateEl.textContent = labelText;

  // Progress bar
  const barWrap = rowEl.createEl("div", { attr: { style: "flex:1;height:6px;background:var(--background-modifier-border);border-radius:3px;overflow:hidden;" } });
  if (total > 0) {
    const pct = Math.round(done / total * 100);
    barWrap.createEl("div", { attr: { style: `height:100%;width:${pct}%;background:var(--interactive-accent);border-radius:3px;` } });
  }

  // Counts
  const countStyle = "font-size:0.75em;padding:1px 6px;border-radius:4px;white-space:nowrap;";
  if (open > 0)  rowEl.createEl("span", { text: `${open} open`,  attr: { style: countStyle + "color:var(--text-muted);background:var(--background-primary);" } });
  if (done > 0)  rowEl.createEl("span", { text: `${done} done`,  attr: { style: countStyle + "color:var(--interactive-accent);background:var(--background-primary);" } });
  if (total === 0) rowEl.createEl("span", { text: "no tasks", attr: { style: countStyle + "color:var(--text-faint);" } });
}

// Always show a Today row at the top — ghost row if note doesn't exist yet
if (!hasTodayNote) {
  const ghostRow = container.createEl("div", {
    attr: { style: "display:flex;align-items:center;gap:10px;padding:6px 10px;border-radius:8px;margin-bottom:4px;background:var(--background-secondary);border:1px dashed var(--interactive-accent);opacity:0.6;" }
  });
  const year = today.toFormat("yyyy");
  const ghostPath = `Work/${year}/${todayStr}.md`;
  renderRow(ghostRow, "Today", true, 0, 0, 0, ghostPath);
  ghostRow.createEl("span", { text: "create →", attr: { style: "font-size:0.72em;color:var(--interactive-accent);white-space:nowrap;" } });
}

if (pages.length === 0 && hasTodayNote) {
  // hasTodayNote=true but pages empty is impossible, but guard anyway
} else {
  for (const page of pages) {
    const d = dv.date(page.date);
    const dateStr = d.toFormat("MM-dd ccc");
    const isToday = d.toFormat("yyyy-MM-dd") === todayStr;
    const open = page.file.tasks.where(t => !t.completed).length;
    const done = page.file.tasks.where(t => t.completed).length;
    const total = open + done;

    const row = container.createEl("div", {
      attr: { style: `display:flex;align-items:center;gap:10px;padding:6px 10px;border-radius:8px;margin-bottom:4px;background:var(--background-secondary);border:1px solid ${isToday ? "var(--interactive-accent)" : "var(--background-modifier-border)"};` }
    });
    renderRow(row, isToday ? "Today" : dateStr, isToday, open, done, total, page.file.path);
  }
}

if (!hasTodayNote && pages.length === 0) {
  container.createEl("p", { text: "No other work notes this week yet.", attr: { style: "color:var(--text-muted);font-size:0.85em;margin-top:4px;" } });
}
```

---

## Brownbag Sessions

```dataviewjs
const sessions = dv.pages('"Work/Brownbag Sessions"')
  .where(p => p.file.name !== "Brownbag Sessions")
  .sort(p => p.created, "desc")
  .limit(3);

const container = dv.el("div", "");

if (sessions.length === 0) {
  container.createEl("p", { text: "No brownbag sessions yet.", attr: { style: "color:var(--text-muted);font-size:0.85em;" } });
} else {
  const statusColor = {
    "planning": "var(--color-yellow)",
    "in-progress": "var(--color-blue)",
    "done": "var(--color-green)"
  };

  // Status inferred from acceptance criteria checklist (## 验收标准).
  // If the heading is renamed, all sessions fall back to "planning".
  function inferStatus(page) {
    const ac = page.file.tasks.where(t => t.section?.subpath === "验收标准");
    if (ac.length === 0) return "planning";
    const done = ac.where(t => t.completed).length;
    if (done === ac.length) return "done";
    if (done > 0) return "in-progress";
    return "planning";
  }

  for (const s of sessions) {
    const st = inferStatus(s);
    const accentColor = statusColor[st] || "var(--color-accent)";

    const card = container.createEl("div", {
      attr: { style: "display:flex;gap:0;margin-bottom:8px;border:1px solid var(--background-modifier-border);border-radius:8px;overflow:hidden;background:var(--background-secondary);" }
    });

    // Left accent bar
    card.createEl("div", { attr: { style: `width:3px;background:${accentColor};flex-shrink:0;` } });

    const body = card.createEl("div", { attr: { style: "flex:1;min-width:0;padding:9px 12px;display:flex;align-items:center;gap:10px;" } });

    // ID badge
    const id = s.id || "BB-?";
    body.createEl("span", {
      text: id,
      attr: { style: "font-weight:700;font-size:0.72em;background:var(--color-accent);color:#fff;border-radius:4px;padding:2px 7px;white-space:nowrap;flex-shrink:0;" }
    });

    // Title + meta
    const info = body.createEl("div", { attr: { style: "flex:1;min-width:0;" } });
    const titleEl = info.createEl("div", { attr: { style: "font-size:0.88em;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" } });
    titleEl.innerHTML = `<a class="internal-link" data-href="${s.file.path}">${s.title || s.file.name}</a>`;

    const meta = info.createEl("div", { attr: { style: "font-size:0.72em;color:var(--text-muted);margin-top:2px;" } });
    const created = s.created ? dv.date(s.created).toFormat("yyyy-MM-dd") : "";
    meta.textContent = created;

    // Status pill
    body.createEl("span", {
      text: st,
      attr: { style: `font-size:0.7em;padding:1px 8px;border-radius:20px;border:1px solid ${accentColor};color:${accentColor};white-space:nowrap;flex-shrink:0;` }
    });
  }

  container.createEl("div", { attr: { style: "margin-top:8px;font-size:0.85em;" } }).innerHTML =
    `<a class="internal-link" data-href="Work/Brownbag Sessions/Brownbag Sessions">All sessions →</a>`;
}
```

---

## Recent Updates

```dataview
TABLE file.mtime AS "Modified"
FROM ""
SORT file.mtime DESC
LIMIT 5
```

---

## Zettelkasten

```dataviewjs
const zk = dv.pages('"Zettelkasten"').where(p => p.file.name !== "Zettelkasten Index");
const inbox = dv.pages('"Inbox"').where(p => !p.file.path.includes("Inbox/archive"));
let totalLinks = 0;
try { totalLinks = zk.array().reduce((sum, p) => sum + p.file.outlinks.length + p.file.inlinks.length, 0); } catch(e) { totalLinks = 0; }

const container = dv.el("div", "");

// Stats row
const stats = container.createEl("div", {
  attr: { style: "display:flex;gap:16px;flex-wrap:wrap;margin-bottom:12px;" }
});
const statItems = [
  [zk.length, "Zettel"],
  [inbox.length, "Inbox"],
  [totalLinks, "Links"],
];
for (const [num, label] of statItems) {
  const s = stats.createEl("div", {
    attr: { style: "padding:8px 16px;background:var(--background-secondary);border-radius:8px;text-align:center;min-width:70px;" }
  });
  s.createEl("div", { text: String(num), attr: { style: "font-size:1.3em;font-weight:700;line-height:1.2;" } });
  s.createEl("div", { text: label, attr: { style: "font-size:0.72em;color:var(--text-muted);" } });
}

// Recent zettel (card grid)
container.createEl("div", { text: "Recent", attr: { style: "font-weight:600;font-size:0.85em;margin:10px 0 8px;color:var(--text-muted);" } });
const recent = zk.sort(p => p.file.ctime, "desc").limit(6);
const grid = container.createEl("div", {
  attr: { style: "display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;" }
});
const statusIcon = { seedling: "🌱", growing: "🌿", evergreen: "🌳" };
for (const p of recent) {
  const card = grid.createEl("div", {
    attr: { style: "border:1px solid var(--background-modifier-border);border-radius:10px;padding:12px;background:var(--background-secondary);box-shadow:0 1px 3px rgba(0,0,0,0.06);display:flex;flex-direction:column;" }
  });
  const titleEl = card.createEl("div", { attr: { style: "font-weight:700;font-size:0.88em;margin-bottom:6px;line-height:1.4;" } });
  titleEl.innerHTML = `<a class="internal-link" data-href="${p.file.path}">${p.file.name}</a>`;
  const topics = p.topics || [];
  if (topics.length > 0) {
    const topicRow = card.createEl("div", { attr: { style: "display:flex;gap:4px;flex-wrap:wrap;margin-bottom:8px;" } });
    for (const t of topics) {
      topicRow.createEl("span", { text: String(t), attr: { style: "font-size:0.65em;padding:1px 6px;border-radius:6px;background:var(--background-primary);color:var(--text-muted);border:1px solid var(--background-modifier-border);" } });
    }
  }
  const src = String(p.source || "").replace(/\[\[|\]\]/g, "").replace(/-\d+$/, "").replace(/-CB_.*$/, "");
  const cardBottom = card.createEl("div", { attr: { style: "margin-top:auto;padding-top:8px;font-size:0.7em;color:var(--text-faint);" } });
  if (src) {
    const srcRow = cardBottom.createEl("div", { attr: { style: "margin-bottom:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" } });
    const si = statusIcon[p.status] || "🌱";
    srcRow.createEl("span", { text: si + " ", attr: { style: "font-size:1.1em;" } });
    const srcEl = srcRow.createEl("span");
    srcEl.innerHTML = `<a class="internal-link" data-href="${String(p.source || "").replace(/\[\[|\]\]/g, "")}" style="color:var(--text-faint);">${src}</a>`;
  } else {
    cardBottom.createEl("span", { text: statusIcon[p.status] || "🌱", attr: { style: "font-size:1.1em;" } });
  }
}

// Link to full dashboard
container.createEl("div", { attr: { style: "margin-top:8px;font-size:0.85em;" } }).innerHTML =
  `<a class="internal-link" data-href="Zettelkasten/Zettelkasten Index">Open Zettelkasten Dashboard →</a>`;
```

---

## Reading

### Currently Reading

```dataviewjs
const pages = dv.pages('"WeRead"')
  .where(p => p.author && p.doc_type === "weread-highlights-reviews")
  .where(p => {
    const s = p.readingStatus || "";
    const prog = p.progress || "0%";
    const num = parseInt(String(prog));
    return (s === "在读" || (num > 0 && num < 100 && prog !== "-1")) && s !== "读完";
  })
  .sort(p => p.lastReadDate, "desc")
  .limit(8);

const readContainer = dv.el("div", "");
const grid = readContainer.createEl("div", {
  attr: { style: "display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px;margin-top:8px;" }
});

for (const p of pages) {
  const title = p.file.name.replace(/-CB_.*$/, "").replace(/-\d+$/, "");
  const cover = p.cover || "";
  const progress = p.progress || "0%";

  const card = grid.createEl("div", {
    attr: { style: "border:1px solid var(--background-modifier-border);border-radius:10px;overflow:hidden;background:var(--background-secondary);box-shadow:0 1px 3px rgba(0,0,0,0.06);" }
  });

  if (cover) {
    card.createEl("img", { attr: { src: cover, style: "width:100%;height:130px;object-fit:cover;" } });
  }

  const body = card.createEl("div", { attr: { style: "padding:8px;" } });
  const titleEl = body.createEl("div", { attr: { style: "font-weight:600;font-size:0.8em;margin-bottom:4px;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;" } });
  titleEl.innerHTML = `<a class="internal-link" data-href="${p.file.path}">${title}</a>`;
  if (p.author) {
    body.createEl("div", { text: p.author, attr: { style: "font-size:0.7em;color:var(--text-muted);margin-bottom:4px;" } });
  }
  // Progress bar
  const barBg = body.createEl("div", { attr: { style: "height:4px;background:var(--background-modifier-border);border-radius:2px;overflow:hidden;" } });
  const num = parseInt(String(progress)) || 0;
  barBg.createEl("div", { attr: { style: `height:100%;width:${num}%;background:var(--interactive-accent);border-radius:2px;` } });
  body.createEl("div", { text: progress, attr: { style: "font-size:0.68em;color:var(--text-faint);margin-top:2px;" } });
}

if (pages.length === 0) {
  readContainer.createEl("div", { text: "No books currently in progress.", attr: { style: "color:var(--text-muted);font-style:italic;" } });
}

readContainer.createEl("div", { attr: { style: "margin-top:12px;font-size:0.85em;" } }).innerHTML =
  `<a class="internal-link" data-href="Books/Books Index">Open Books Index →</a>`;
```

### Articles

```dataviewjs
function renderSection(container, title, pages, indexPath) {
  const section = container.createEl("div", { attr: { style: "flex:1;min-width:200px;" } });

  // Header with count badge
  const header = section.createEl("div", { attr: { style: "display:flex;align-items:center;gap:8px;margin-bottom:8px;" } });
  const titleEl = header.createEl("span", { attr: { style: "font-weight:600;font-size:0.85em;" } });
  titleEl.innerHTML = `<a class="internal-link" data-href="${indexPath}" style="text-decoration:none;">${title}</a>`;
  header.createEl("span", {
    text: String(pages.length),
    attr: { style: "font-size:0.65em;padding:1px 7px;border-radius:10px;background:var(--background-primary);color:var(--text-muted);border:1px solid var(--background-modifier-border);" }
  });

  // Article list
  const list = section.createEl("div", "");
  const recent = pages.sort(p => p.file.mtime, "desc").limit(8);
  for (const p of recent) {
    const row = list.createEl("div", { attr: { style: "padding:5px 0;border-bottom:1px solid var(--background-modifier-border);" } });
    const link = row.createEl("div", { attr: { style: "font-size:0.82em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" } });
    link.innerHTML = `<a class="internal-link" data-href="${p.file.path}">${p.file.name}</a>`;
  }

  // "All articles →" link
  section.createEl("div", { attr: { style: "margin-top:6px;font-size:0.8em;" } }).innerHTML =
    `<a class="internal-link" data-href="${indexPath}" style="color:var(--text-faint);">All ${title.toLowerCase()} →</a>`;
}

const container = dv.el("div", "");
const grid = container.createEl("div", {
  attr: { style: "display:flex;gap:20px;flex-wrap:wrap;" }
});

const matter = dv.pages('"Matter"').where(p => p.file.name !== "Matter Index");
const instapaper = dv.pages('"Instapaper Notes"').where(p => p.file.name !== "Instapaper Index");

renderSection(grid, "Matter", matter, "Matter/Matter Index");
renderSection(grid, "Instapaper", instapaper, "Instapaper Notes/Instapaper Index");
```

---

## Learning

```dataviewjs
function isoWeekLabel(d) {
  const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  const day = date.getUTCDay() || 7;
  date.setUTCDate(date.getUTCDate() + 4 - day);
  const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
  const week = Math.ceil((((date - yearStart) / 86400000) + 1) / 7);
  return `${date.getUTCFullYear()}-W${String(week).padStart(2, '0')}`;
}
function lastNWeeks(n) {
  const result = [];
  const now = new Date();
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i * 7);
    result.push(isoWeekLabel(d));
  }
  return result;
}

const WEEKS = lastNWeeks(4);
const currentWeek = WEEKS[WEEKS.length - 1];
const plans = dv.pages('"Learning"').where(p => p.file.name === "00_plan" && p.status === "active");
const allLogs = dv.pages('"Learning"').where(p => p.week !== undefined);

const container = dv.el("div", "");

if (plans.length === 0) {
  container.createEl("p", { text: "No active plans — run /learning-init to start one.", attr: { style: "color:var(--text-muted);font-size:0.85em;" } });
} else {
  for (const p of plans) {
    const code = p.file.folder.split("/").pop();
    const planLogs = allLogs.filter(l => l.code === code);
    const logMap = {};
    for (const l of planLogs) logMap[l.week] = l;
    const weeksElapsed = p.started
      ? Math.floor((new Date() - p.started.toJSDate()) / (7 * 24 * 60 * 60 * 1000)) + 1
      : null;
    const currentPhase = p.phase || 1;

    // Card
    const card = container.createEl("div", {
      attr: { style: "display:flex;gap:0;margin-bottom:8px;border:1px solid var(--background-modifier-border);border-radius:8px;overflow:hidden;background:var(--background-secondary);" }
    });

    // Left accent bar
    card.createEl("div", { attr: { style: "width:3px;background:var(--color-accent);flex-shrink:0;" } });

    const body = card.createEl("div", { attr: { style: "flex:1;min-width:0;padding:9px 12px;" } });

    // Row 1: code badge + phase pill + week stat
    const row1 = body.createEl("div", { attr: { style: "display:flex;align-items:center;gap:6px;margin-bottom:5px;" } });
    row1.innerHTML += `<a class="internal-link" data-href="${p.file.path}" style="font-weight:700;font-size:0.75em;background:var(--color-accent);color:#fff;border-radius:4px;padding:2px 7px;text-decoration:none;white-space:nowrap;flex-shrink:0;">${code}</a>`;
    row1.createEl("span", {
      text: `Phase ${currentPhase}`,
      attr: { style: "font-size:0.7em;padding:1px 7px;border-radius:20px;border:1px solid var(--color-accent);color:var(--color-accent);white-space:nowrap;flex-shrink:0;" }
    });
    if (weeksElapsed !== null) {
      row1.createEl("span", {
        text: `Wk ${weeksElapsed}`,
        attr: { style: "font-size:0.7em;color:var(--text-faint);white-space:nowrap;" }
      });
    }

    // Row 2: target text
    if (p.target) {
      body.createEl("div", {
        text: p.target,
        attr: { style: "font-size:0.8em;color:var(--text-muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" }
      });
    }

    // Right: 4-week activity squares
    const dotsWrap = card.createEl("div", { attr: { style: "display:flex;align-items:center;gap:3px;padding:0 12px;flex-shrink:0;" } });
    for (const w of [...WEEKS].reverse()) {
      if (logMap[w]) {
        dotsWrap.createEl("a", {
          attr: { class: "internal-link", "data-href": logMap[w].file.path, title: w, style: "width:10px;height:10px;border-radius:2px;background:var(--color-accent);display:inline-block;opacity:0.85;" }
        });
      } else {
        const isCurrent = w === currentWeek;
        dotsWrap.createEl("div", {
          attr: { title: w, style: `width:10px;height:10px;border-radius:2px;${isCurrent ? "border:1.5px dashed var(--color-accent);opacity:0.7;" : "background:var(--background-modifier-border);opacity:0.5;"}` }
        });
      }
    }
  }

  container.createEl("div", { attr: { style: "margin-top:12px;font-size:0.85em;" } }).innerHTML =
    `<a class="internal-link" data-href="Learning/Dashboard.md">Full dashboard →</a>`;
}
```

---

## Entertainment

```dataview
LIST
FROM "Entertainment"
SORT file.mtime DESC
```

---

## Vault Stats

```dataviewjs
const folders = dv.pages('').groupBy(p => p.file.folder.split('/')[0]).sort(g => g.rows.length, 'desc');
dv.table(["Folder", "Notes"], folders.map(g => [g.key || "Root", g.rows.length]));
```

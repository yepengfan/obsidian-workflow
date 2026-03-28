---
cssclasses:
  - dashboard
banner: "![[home.jpg]]"
banner_x: 0.5
banner_y: 0
---

## Work

```dataviewjs
document.getElementById('bc-grid-layout')?.remove();

// ========== TOP BAR: segment + action buttons in one row ==========
const topBar = dv.el("div", "", {
  attr: { style: "display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px;" }
});

// Panels (created AFTER topBar so they appear below)
const panels = {};
panels["work"] = dv.el("div", "", { attr: { style: "display:none;" } });
panels["card"] = dv.el("div", "", { attr: { style: "display:none;" } });
const tabBtns = {};
function setTab(id) {
  for (const k of Object.keys(panels)) {
    panels[k].style.display = k === id ? "block" : "none";
    tabBtns[k].style.cssText = "padding:4px 14px;border-radius:7px;border:none;cursor:pointer;font-size:0.82em;font-weight:600;transition:all 0.15s;" + (k === id
      ? "background:var(--background-primary);color:var(--text-normal);box-shadow:0 1px 3px rgba(0,0,0,0.08);"
      : "background:transparent;color:var(--text-muted);box-shadow:none;");
  }
}

// Segment control (left side of topBar)
const seg = topBar.createEl("div", {
  attr: { style: "display:inline-flex;gap:2px;padding:2px;border-radius:9px;background:var(--background-secondary);margin-left:-6px;" }
});
for (const t of [{id:"work",label:"Work"},{id:"card",label:"Card"}]) {
  tabBtns[t.id] = seg.createEl("button", { text: t.label });
  tabBtns[t.id].addEventListener("click", () => setTab(t.id));
}
setTab("work");

// ========== WORK TAB ==========
// Action buttons always inside Work panel, separate row from segment
const row = panels["work"].createEl("div", { attr: { style: "display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:4px;" } });

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
    "# " + dayName,
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

  // --- Carryover: bring incomplete tasks from previous daily note ---
  const prevDailies = app.vault.getMarkdownFiles()
    .filter(f => /^Work\/\d{4}\/\d{4}-\d{2}-\d{2}\.md$/.test(f.path) && f.basename < dateStr)
    .sort((a, b) => b.basename.localeCompare(a.basename));
  if (prevDailies.length > 0) {
    const pf = prevDailies[0];
    const pc = (await app.vault.read(pf)).split("\n");
    // Locate ## headings (skip code blocks)
    let tS = -1, cS = -1; const h2L = []; let inCB = false;
    for (let i = 0; i < pc.length; i++) {
      if (pc[i].trim().startsWith(fence)) { inCB = !inCB; continue; }
      if (inCB) continue;
      if (/^## /.test(pc[i])) {
        h2L.push(i);
        if (/^## Tasks/.test(pc[i]) && tS < 0) tS = i;
        if (/Carryover/.test(pc[i]) && cS < 0) cS = i;
      }
    }
    const nxtH2 = (pos) => { for (const h of h2L) if (h > pos) return h; return pc.length; };
    // Collect task line indices from ## Tasks and ## Carryover sections
    const ranges = [];
    if (tS >= 0) ranges.push([tS, nxtH2(tS)]);
    if (cS >= 0) ranges.push([cS, nxtH2(cS)]);
    const byProj = {};
    for (const [s, e] of ranges) {
      let proj = null, ic = false;
      for (let i = s + 1; i < e; i++) {
        const t = pc[i].trim();
        if (t.startsWith(fence)) { ic = !ic; continue; }
        if (ic) continue;
        if (t.startsWith("### ")) { proj = t.slice(4); continue; }
        if (proj && /^- \[.\]/.test(t)) {
          if (!byProj[proj]) byProj[proj] = [];
          byProj[proj].push(i);
        }
      }
    }
    // Build task blocks (top-level + subtasks), keep only incomplete
    const toMark = []; const carry = {}; let tot = 0, pCt = 0;
    for (const [pr, idxs] of Object.entries(byProj)) {
      const blocks = []; let blk = null;
      for (const idx of idxs) {
        if (pc[idx].search(/\S/) === 0) { blk = [idx]; blocks.push(blk); }
        else if (blk) blk.push(idx);
      }
      const kept = [];
      for (const b of blocks) {
        if (/^- \[ \]/.test(pc[b[0]].trim())) {
          const out = [];
          for (const idx of b) {
            if (/- \[ \]/.test(pc[idx]) && pc[idx].replace(/^\t*- \[ \] ?/, "").trim() !== "") { toMark.push(idx); tot++; out.push(pc[idx]); }
          }
          if (out.length > 0) kept.push(...out);
        }
      }
      if (kept.length > 0) { carry[pr] = kept; pCt++; }
    }
    // Mark previous note tasks as [>] and append carryover section
    if (toMark.length > 0) {
      for (const idx of toMark) pc[idx] = pc[idx].replace(/- \[ \]/, "- [>]");
      await app.vault.modify(pf, pc.join("\n"));
      const ref = pf.path.replace(".md", "");
      content += "## \u{1F504} Carryover\n\n";
      content += "> Carried over from [[" + ref + "]] \u2014 " + tot + " tasks across " + pCt + " project" + (pCt !== 1 ? "s" : "") + "\n\n";
      for (const [pr, lines] of Object.entries(carry)) {
        content += "### " + pr + "\n";
        content += lines.join("\n") + "\n\n";
      }
    }
  }

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

// ========== WEEKLY VIEW (Work tab) ==========
const today = dv.date("today");
const rangeStart = today.minus({ days: 6 });

const pages = dv.pages('"Work"')
  .where(p => p.file.tags.includes("#work-daily"))
  .where(p => {
    const d = dv.date(p.date);
    return d && d >= rangeStart && d <= today;
  })
  .sort(p => p.date, "desc");

const wkView = panels["work"].createEl("div", "");

// Date range label (rolling 7 days)
const weekLabel = rangeStart.toFormat("MMM dd") + " – " + today.toFormat("MMM dd");
wkView.createEl("div", {
  text: weekLabel,
  attr: { style: "font-size:0.78em;color:var(--text-muted);margin-bottom:6px;font-weight:600;" }
});

const todayStr = today.toFormat("yyyy-MM-dd");
const hasTodayNote = pages.some(p => dv.date(p.date).toFormat("yyyy-MM-dd") === todayStr);

function renderRow(rowEl, labelText, isToday, open, done, carriedIn, carriedAway, total, href) {
  // Date label
  const dateEl = rowEl.createEl("a", {
    cls: "internal-link",
    attr: { "data-href": href, style: `font-size:0.82em;font-weight:${isToday ? "700" : "400"};min-width:75px;text-decoration:none;color:${isToday ? "var(--interactive-accent)" : "var(--text-normal)"};` }
  });
  dateEl.textContent = labelText;

  // Progress bar: [done][carried-away ⬆️][carried-in ➡️][  open  ]
  // done (solid accent) | carry-out (yellow) | carry-in (30% accent) | open (gray bg)
  const barWrap = rowEl.createEl("div", { attr: { style: "flex:1;height:6px;background:var(--background-modifier-border);border-radius:3px;overflow:hidden;position:relative;" } });
  if (total > 0) {
    const filledPct      = Math.round((done + carriedAway + carriedIn) / total * 100);
    const donePct        = Math.round(done        / total * 100);
    const carriedAwayPct = Math.round(carriedAway / total * 100);
    const carriedInPct   = Math.max(0, filledPct - donePct - carriedAwayPct);
    if (done > 0)
      barWrap.createEl("div", { attr: { style: `position:absolute;left:0;top:0;height:100%;width:${donePct}%;background:var(--interactive-accent);` } });
    if (carriedAway > 0)
      barWrap.createEl("div", { attr: { style: `position:absolute;left:${donePct}%;top:0;height:100%;width:${carriedAwayPct}%;background:var(--color-yellow);opacity:0.75;` } });
    if (carriedIn > 0)
      barWrap.createEl("div", { attr: { style: `position:absolute;left:${donePct + carriedAwayPct}%;top:0;height:100%;width:${carriedInPct}%;background:var(--interactive-accent);opacity:0.3;` } });
  }

  // Counts — always show all metrics for consistent layout; dim zeros
  // display:inline-block + width:4.8em reserves space for 2-digit numbers and keeps columns aligned
  const countStyle = "display:inline-block;width:4.8em;font-size:0.75em;padding:1px 4px;border-radius:4px;white-space:nowrap;text-align:center;box-sizing:border-box;";
  const dim = "color:var(--text-faint);background:var(--background-primary);opacity:0.35;";
  if (total === 0) {
    rowEl.createEl("span", { text: "no tasks", attr: { style: countStyle + "color:var(--text-faint);" } });
  } else {
    rowEl.createEl("span", { text: `${open} open`,      attr: { style: countStyle + (open       > 0 ? "color:var(--text-muted);background:var(--background-primary);"        : dim) } });
    rowEl.createEl("span", { text: `${carriedAway} ⬆️`, attr: { style: countStyle + (carriedAway > 0 ? "color:var(--color-yellow);background:var(--background-primary);"    : dim) } });
    rowEl.createEl("span", { text: `${carriedIn} ➡️`,   attr: { style: countStyle + (carriedIn  > 0 ? "color:var(--text-faint);background:var(--background-primary);"        : dim) } });
    rowEl.createEl("span", { text: `${done} done`,      attr: { style: countStyle + (done        > 0 ? "color:var(--interactive-accent);background:var(--background-primary);" : dim) } });
    rowEl.createEl("span", { text: `${total} total`,    attr: { style: countStyle + "color:var(--text-faint);background:var(--background-primary);" } });
  }
}

// Always show a Today row at the top — ghost row if note doesn't exist yet
if (!hasTodayNote) {
  const ghostRow = wkView.createEl("div", {
    attr: { style: "display:flex;align-items:center;gap:10px;padding:6px 10px;border-radius:8px;margin-bottom:4px;background:var(--background-secondary);border:1px dashed var(--interactive-accent);opacity:0.6;cursor:pointer;" }
  });
  ghostRow.createEl("span", {
    text: "Today",
    attr: { style: "font-size:0.82em;font-weight:700;min-width:75px;color:var(--interactive-accent);" }
  });
  ghostRow.createEl("div", { attr: { style: "flex:1;height:6px;background:var(--background-modifier-border);border-radius:3px;" } });
  ghostRow.createEl("span", { text: "create →", attr: { style: "font-size:0.72em;color:var(--interactive-accent);white-space:nowrap;" } });
  // Click → trigger the navToday button (date button in the Work toolbar above) which has the full creation logic
  ghostRow.addEventListener("click", () => {
    const btn = Array.from(document.querySelectorAll("button"))
      .find(b => b.textContent.trim() === todayStr);
    if (btn) btn.click();
  });
}

for (const page of pages) {
  const d = dv.date(page.date);
  const dateStr = d.toFormat("MM-dd ccc");
  const isToday = d.toFormat("yyyy-MM-dd") === todayStr;
  // Count only tasks between ## Tasks and ## Notes (or EOF if ## Notes absent).
  // Tasks live under ### <ProjectName> sub-headings, so section.subpath won't work — line range is used instead.
  const tfile = app.vault.getAbstractFileByPath(page.file.path);
  const fCache = tfile ? app.metadataCache.getFileCache(tfile) : null;
  const fHeadings = fCache?.headings || [];
  let tasksLine = -1, notesLine = Infinity, carryoverLine = -1, carryoverEndLine = Infinity;
  for (const h of fHeadings) {
    if (h.level === 2 && h.heading === "Tasks" && tasksLine === -1) tasksLine = h.position.start.line;
    if (h.level === 2 && h.heading === "Notes" && notesLine === Infinity) notesLine = h.position.start.line;
    if (h.level === 2 && h.heading.includes("Carryover") && carryoverLine === -1) carryoverLine = h.position.start.line;
    else if (carryoverLine !== -1 && h.level === 2 && carryoverEndLine === Infinity) carryoverEndLine = h.position.start.line;
  }
  // Cap tasksSection at carryoverLine when ## Notes is absent — prevents Carryover tasks
  // from being double-counted as both inTasksSection and inCarryoverSection.
  const tasksSectionEnd = Math.min(notesLine, carryoverLine === -1 ? Infinity : carryoverLine);
  const inTasksSection = tasksLine !== -1
    ? t => t.line > tasksLine && t.line < tasksSectionEnd
    : () => false;
  const inCarryoverSection = carryoverLine !== -1
    ? t => t.line > carryoverLine && t.line < carryoverEndLine
    : () => false;
  const open        = page.file.tasks.where(t => t.status === " "  && inTasksSection(t)).length;
  const done        = page.file.tasks.where(t => t.completed        && inTasksSection(t)).length;
  const carriedAway = page.file.tasks.where(t => t.status === ">"  && inTasksSection(t)).length;
  const carriedIn   = page.file.tasks.where(t => t.status === " "  && inCarryoverSection(t)).length;
  const total = open + done + carriedAway + carriedIn;

  const row = wkView.createEl("div", {
    attr: { style: `display:flex;align-items:center;gap:10px;padding:6px 10px;border-radius:8px;margin-bottom:4px;background:var(--background-secondary);border:1px solid ${isToday ? "var(--interactive-accent)" : "var(--background-modifier-border)"};` }
  });
  renderRow(row, isToday ? "Today" : dateStr, isToday, open, done, carriedIn, carriedAway, total, page.file.path);
}

if (pages.length === 0) {
  wkView.createEl("p", { text: "No other work notes in the last 7 days.", attr: { style: "color:var(--text-muted);font-size:0.85em;margin-top:4px;" } });
}

// ========== CARD TAB ==========
const bcPage = dv.page("Profile/Personal Baseball Card");
if (bcPage) {
  const card = panels["card"].createEl("div", {
    attr: { style: "width:260px;max-width:100%;margin:0 auto;border:1px solid var(--background-modifier-border);border-radius:12px;overflow:hidden;background:var(--background-primary);box-shadow:0 2px 6px rgba(0,0,0,0.08);" }
  });

  // Header
  const hdr = card.createEl("div", { attr: { style: "padding:14px 14px 6px;text-align:center;" } });
  const imgFile = app.vault.getAbstractFileByPath("Profile/ted-profile.png");
  if (imgFile) {
    hdr.createEl("img", {
      attr: { src: app.vault.getResourcePath(imgFile), style: "width:48px;height:48px;border-radius:50%;object-fit:cover;object-position:top;border:2px solid var(--background-modifier-border);" }
    });
  }
  hdr.createEl("div", { text: "Ted Fan", attr: { style: "font-size:0.92em;font-weight:800;margin-top:4px;" } });
  const bcBadges = hdr.createEl("div", { attr: { style: "display:flex;justify-content:center;gap:3px;margin-top:3px;" } });
  bcBadges.createEl("span", { text: String(bcPage.mbti || ""), attr: { style: "font-size:0.52em;font-weight:700;padding:1px 4px;border-radius:3px;background:var(--interactive-accent);color:var(--text-on-accent);" } });
  bcBadges.createEl("span", { text: String(bcPage.role || ""), attr: { style: "font-size:0.52em;padding:1px 4px;border-radius:3px;border:1px solid var(--background-modifier-border);color:var(--text-muted);" } });
  bcBadges.createEl("span", { text: "🏆 " + String(bcPage.py_archetype || ""), attr: { style: "font-size:0.52em;padding:1px 4px;border-radius:3px;border:1px solid var(--background-modifier-border);color:var(--text-muted);" } });

  // Radar chart
  const traits = [
    { n: "Deliberative", s: "Del", v: Number(bcPage.py_deliberative) || 0, g: "t" },
    { n: "Detailed", s: "Det", v: Number(bcPage.py_detailed) || 0, g: "t" },
    { n: "Creative", s: "Cre", v: Number(bcPage.py_creative) || 0, g: "t" },
    { n: "Conceptual", s: "Con", v: Number(bcPage.py_conceptual) || 0, g: "t" },
    { n: "Leadership", s: "Ldr", v: Number(bcPage.py_leadership) || 0, g: "e" },
    { n: "Tough", s: "Tgh", v: Number(bcPage.py_tough) || 0, g: "e" },
    { n: "Nurturing", s: "Nur", v: Number(bcPage.py_nurturing) || 0, g: "e" },
    { n: "Extraverted", s: "Ext", v: Number(bcPage.py_extraverted) || 0, g: "e" },
    { n: "Composed", s: "Cmp", v: Number(bcPage.py_composed) || 0, g: "a" },
    { n: "Determined", s: "Dtr", v: Number(bcPage.py_determined) || 0, g: "a" },
    { n: "Humble", s: "Hum", v: Number(bcPage.py_humble) || 0, g: "a" },
    { n: "Autonomous", s: "Aut", v: Number(bcPage.py_autonomous) || 0, g: "a" },
  ];
  const gCol = { t: "#2ba5a5", e: "#8b6bae", a: "#c4953a" };
  const sz = 240, rcx = sz/2, rcy = sz/2, RR = 72;
  const NN = traits.length, rstep = (2 * Math.PI) / NN;
  const rpt = (i, pct) => {
    const a = -Math.PI/2 + i * rstep;
    return [rcx + (pct/100)*RR*Math.cos(a), rcy + (pct/100)*RR*Math.sin(a)];
  };
  let svg = `<svg viewBox="0 0 ${sz} ${sz}" style="width:100%;max-width:220px;display:block;margin:0 auto;">`;
  for (const p of [25,50,75,100])
    svg += `<circle cx="${rcx}" cy="${rcy}" r="${(p/100)*RR}" fill="none" stroke="var(--background-modifier-border)" stroke-width="0.5"/>`;
  for (let i = 0; i < NN; i++) {
    const [x,y] = rpt(i, 100);
    svg += `<line x1="${rcx}" y1="${rcy}" x2="${x}" y2="${y}" stroke="var(--background-modifier-border)" stroke-width="0.3"/>`;
  }
  const polyPts = traits.map((t,i) => rpt(i, t.v).join(",")).join(" ");
  svg += `<polygon points="${polyPts}" fill="rgba(58,154,92,0.12)" stroke="#3a9a5c" stroke-width="1.8" stroke-linejoin="round"/>`;
  traits.forEach((t,i) => {
    const [x,y] = rpt(i, t.v);
    const c = t.v >= 70 ? '#3a9a5c' : t.v >= 40 ? '#999' : '#c75c5c';
    svg += `<circle cx="${x}" cy="${y}" r="2.5" fill="${c}"><title>${t.n}: ${t.v}%</title></circle>`;
  });
  // Trait labels around the outside
  traits.forEach((t, i) => {
    const [x, y] = rpt(i, 130);
    const col = gCol[t.g];
    svg += `<text x="${x}" y="${y}" text-anchor="middle" dominant-baseline="central" font-size="6.5" font-weight="600" fill="${col}" opacity="0.8"><title>${t.n}: ${t.v}%</title>${t.s}</text>`;
  });
  svg += '</svg>';
  const chartEl = card.createEl("div", { attr: { style: "padding:6px 8px 2px;border-top:1px solid var(--background-modifier-border);" } });
  chartEl.innerHTML = svg;

  card.createEl("div", { attr: { style: "padding:4px 14px 10px;text-align:center;font-size:0.7em;" } }).innerHTML =
    '<a class="internal-link" data-href="Profile/Personal Baseball Card">Open Baseball Card →</a>';
}
```

---

## Feeds

```dataviewjs
// Tab bar (pill / segment)
const fTopBar = dv.el("div", "", {
  attr: { style: "display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px;" }
});
const fSeg = fTopBar.createEl("div", {
  attr: { style: "display:inline-flex;gap:2px;padding:2px;border-radius:9px;background:var(--background-secondary);margin-left:-6px;" }
});
const fPanels = {};
fPanels["ai"] = dv.el("div", "", { attr: { style: "display:none;" } });
fPanels["gh"] = dv.el("div", "", { attr: { style: "display:none;" } });
const fBtns = {};
function setFeedTab(id) {
  for (const k of Object.keys(fPanels)) {
    fPanels[k].style.display = k === id ? "block" : "none";
    fBtns[k].style.cssText = "padding:4px 14px;border-radius:7px;border:none;cursor:pointer;font-size:0.82em;font-weight:600;transition:all 0.15s;" + (k === id
      ? "background:var(--background-primary);color:var(--text-normal);box-shadow:0 1px 3px rgba(0,0,0,0.08);"
      : "background:transparent;color:var(--text-muted);box-shadow:none;");
  }
}
for (const t of [{id:"ai",label:"AI Digest"},{id:"gh",label:"GitHub Trending"}]) {
  fBtns[t.id] = fSeg.createEl("button", { text: t.label });
  fBtns[t.id].addEventListener("click", () => setFeedTab(t.id));
}
setFeedTab("ai");

// ========== AI DIGEST TAB ==========
{
  const p = fPanels["ai"];
  const today = dv.date("today").toFormat("yyyy-MM-dd");
  const zhPath = `Feeds/AI-Daily/${today}.md`;
  const enPath = `Feeds/AI-Daily/${today}-en.md`;
  const zhFile = app.vault.getAbstractFileByPath(zhPath);
  const enFile = app.vault.getAbstractFileByPath(enPath);
  const digestFile = enFile || zhFile;

  if (digestFile) {
    const isEn = !!enFile;
    const digestPath = isEn ? enPath : zhPath;
    const page = dv.page(digestPath);
    const content = await app.vault.read(digestFile);
    const lines = content.split("\n");

    const highlightMarker = isEn ? "Today's Highlights" : "今日看点";
    let start = -1, end = lines.length;
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].startsWith("##") && lines[i].includes(highlightMarker)) { start = i + 1; continue; }
      if (start > 0 && lines[i].startsWith("---")) { end = i; break; }
    }
    const summary = start > 0
      ? lines.slice(start, end).filter(l => l.trim()).join(" ")
      : "";

    const row = p.createEl("div", {
      attr: { style: "display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:8px;" }
    });
    const scanned = page.articles_scanned || "?";
    const selected = page.articles_selected || "?";
    row.createEl("span", {
      text: `📰 ${selected}/${scanned} articles`,
      attr: { style: "font-size:0.78em;color:var(--text-muted);" }
    });
    const links = row.createEl("div", { attr: { style: "margin-left:auto;display:flex;gap:8px;" } });
    links.createEl("a", { text: "中文", cls: "internal-link", attr: { "data-href": zhPath, style: "font-size:0.82em;" } });
    if (enFile) {
      links.createEl("a", { text: "EN", cls: "internal-link", attr: { "data-href": enPath, style: "font-size:0.82em;" } });
    }

    if (summary) {
      p.createEl("div", {
        text: summary,
        attr: { style: "font-size:0.85em;line-height:1.6;padding:10px 12px;background:var(--background-secondary);border-radius:8px;border-left:3px solid var(--interactive-accent);" }
      });
    }
  } else {
    p.createEl("div", {
      text: "No digest for today yet. Run /ai-digest in Claude Code to generate.",
      attr: { style: "font-size:0.85em;color:var(--text-muted);padding:12px;border-radius:8px;background:var(--background-secondary);border:1px dashed var(--background-modifier-border);" }
    });
  }
  p.createEl("div", { attr: { style: "margin-top:8px;font-size:0.82em;" } }).innerHTML =
    '<a class="internal-link" data-href="Feeds/AI-Daily/Dashboard">All digests →</a>';
}

// ========== GITHUB TRENDING TAB ==========
{
  const p = fPanels["gh"];
  const today = dv.date("today").toFormat("yyyy-MM-dd");
  const zhPath = `Feeds/GitHub-Trending/${today}.md`;
  const enPath = `Feeds/GitHub-Trending/${today}-en.md`;
  const zhFile = app.vault.getAbstractFileByPath(zhPath);
  const enFile = app.vault.getAbstractFileByPath(enPath);
  const reportFile = enFile || zhFile;

  if (reportFile) {
    const isEn = !!enFile;
    const reportPath = isEn ? enPath : zhPath;
    const page = dv.page(reportPath);
    const content = await app.vault.read(reportFile);
    const lines = content.split("\n");

    const repoLines = lines
      .filter(l => l.startsWith("> [!tip]") && (l.includes("🥇") || l.includes("🥈") || l.includes("🥉")))
      .slice(0, 3);

    const row = p.createEl("div", {
      attr: { style: "display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:8px;" }
    });
    const scanned = page.repos_scanned || "?";
    const selected = page.repos_selected || "?";
    row.createEl("span", {
      text: `📦 ${selected}/${scanned} repos`,
      attr: { style: "font-size:0.78em;color:var(--text-muted);" }
    });
    const links = row.createEl("div", { attr: { style: "margin-left:auto;display:flex;gap:8px;" } });
    links.createEl("a", { text: "中文", cls: "internal-link", attr: { "data-href": zhPath, style: "font-size:0.82em;" } });
    if (enFile) {
      links.createEl("a", { text: "EN", cls: "internal-link", attr: { "data-href": enPath, style: "font-size:0.82em;" } });
    }

    if (repoLines.length > 0) {
      const preview = p.createEl("div", {
        attr: { style: "font-size:0.85em;line-height:1.8;padding:10px 12px;background:var(--background-secondary);border-radius:8px;border-left:3px solid var(--interactive-accent);" }
      });
      for (const line of repoLines) {
        const cleaned = line.replace(/^>\s*\[!tip\]\s*/, "");
        preview.createEl("div", { text: cleaned });
      }
    }
  } else {
    p.createEl("div", {
      text: "No trending report for today yet. Run /github-trending in Claude Code to generate.",
      attr: { style: "font-size:0.85em;color:var(--text-muted);padding:12px;border-radius:8px;background:var(--background-secondary);border:1px dashed var(--background-modifier-border);" }
    });
  }
  p.createEl("div", { attr: { style: "margin-top:8px;font-size:0.82em;" } }).innerHTML =
    '<a class="internal-link" data-href="Feeds/GitHub-Trending/Dashboard">All reports →</a>';
}
```

---

## Brownbag Sessions

```dataviewjs
const sessions = dv.pages('"Work/Brownbag Sessions"')
  .where(p => p.id && String(p.id).startsWith("BB-"))
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

const WEEKS = lastNWeeks(10);
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

    // Right: 10-week activity squares
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

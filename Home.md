---
cssclasses:
  - dashboard
banner: "![[home.jpg]]"
banner_x: 0.5
banner_y: 0
---

```dataviewjs
const isMobile = app.isMobile;

// Tab factory: creates pill/segment tab group, returns { panels, topBar }
function createTabGroup(dvRef, tabs, defaultId) {
  const topBar = dvRef.el("div", "", {
    attr: { style: "display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px;" }
  });
  const panels = {};
  const btns = {};
  const tabPad = isMobile ? "3px 8px" : "4px 14px";
  const tabFont = isMobile ? "0.72em" : "0.82em";
  const segGap = isMobile ? "1px" : "2px";
  for (const t of tabs) {
    panels[t.id] = dvRef.el("div", "", { attr: { style: "display:none;" } });
  }
  function activate(id) {
    for (const k of Object.keys(panels)) {
      panels[k].style.display = k === id ? "block" : "none";
      btns[k].style.cssText = `padding:${tabPad};border-radius:7px;border:none;cursor:pointer;font-size:${tabFont};font-weight:600;transition:all 0.15s;` + (k === id
        ? "background:var(--background-primary);color:var(--text-normal);box-shadow:0 1px 3px rgba(0,0,0,0.08);"
        : "background:transparent;color:var(--text-muted);box-shadow:none;");
    }
  }
  const seg = topBar.createEl("div", {
    attr: { style: `display:inline-flex;gap:${segGap};padding:2px;border-radius:9px;background:var(--background-secondary);` }
  });
  for (const t of tabs) {
    btns[t.id] = seg.createEl("button", { text: t.label });
    btns[t.id].addEventListener("click", () => activate(t.id));
  }
  activate(defaultId);
  return { panels, topBar };
}

// ========== WORK + CARD TABS ==========
const { panels, topBar } = createTabGroup(dv, [
  { id: "work", label: "Work" },
  { id: "card", label: "Profile" },
  { id: "skills", label: "Skills" },
], "work");

// ========== WORK TAB ==========
// Action buttons always inside Work panel, separate row from segment
const btnPad = isMobile ? "6px 10px" : "8px 18px";
const btnFont = isMobile ? "0.8em" : "0.88em";
const row = panels["work"].createEl("div", { attr: { style: "display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:4px;" } });

// Navigation buttons
const navDash = row.createEl("button", {
  text: "Work Dashboard",
  attr: { style: `padding:${btnPad};border:1px solid var(--background-modifier-border);border-radius:8px;background:var(--background-secondary);color:var(--text-normal);cursor:pointer;font-size:${btnFont};` }
});
navDash.addEventListener("click", () => app.workspace.openLinkText("Work/Work Dashboard", "", false));

const navToday = row.createEl("button", {
  text: dv.date("today").toFormat("yyyy-MM-dd"),
  attr: { style: `padding:${btnPad};border:1px solid var(--background-modifier-border);border-radius:8px;background:var(--background-secondary);color:var(--text-normal);cursor:pointer;font-size:${btnFont};` }
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
    content += `### ${p}\n\n`;
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
    style: `margin-left:auto;padding:${btnPad};background:var(--interactive-accent);color:var(--text-on-accent);border-radius:8px;font-weight:600;font-size:${btnFont};border:none;cursor:pointer;white-space:nowrap;`
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
  // On mobile: drop total column, use auto width + tighter padding
  const countStyle = isMobile
    ? "display:inline-block;width:auto;font-size:0.65em;padding:1px 3px;border-radius:4px;white-space:nowrap;text-align:center;box-sizing:border-box;"
    : "display:inline-block;width:4.8em;font-size:0.75em;padding:1px 4px;border-radius:4px;white-space:nowrap;text-align:center;box-sizing:border-box;";
  const dim = "color:var(--text-faint);background:var(--background-primary);opacity:0.35;";
  if (total === 0) {
    rowEl.createEl("span", { text: "no tasks", attr: { style: countStyle + "color:var(--text-faint);" } });
  } else {
    rowEl.createEl("span", { text: `${open} open`,      attr: { style: countStyle + (open       > 0 ? "color:var(--text-muted);background:var(--background-primary);"        : dim) } });
    rowEl.createEl("span", { text: `${carriedAway} ⬆️`, attr: { style: countStyle + (carriedAway > 0 ? "color:var(--color-yellow);background:var(--background-primary);"    : dim) } });
    rowEl.createEl("span", { text: `${carriedIn} ➡️`,   attr: { style: countStyle + (carriedIn  > 0 ? "color:var(--text-faint);background:var(--background-primary);"        : dim) } });
    rowEl.createEl("span", { text: `${done} done`,      attr: { style: countStyle + (done        > 0 ? "color:var(--interactive-accent);background:var(--background-primary);" : dim) } });
    if (!isMobile) {
      rowEl.createEl("span", { text: `${total} total`,    attr: { style: countStyle + "color:var(--text-faint);background:var(--background-primary);" } });
    }
  }
}

// Always show a Today row at the top — ghost row if note doesn't exist yet
const rowGap = isMobile ? "6px" : "10px";
if (!hasTodayNote) {
  const ghostRow = wkView.createEl("div", {
    attr: { style: `display:flex;align-items:center;gap:${rowGap};padding:6px 10px;border-radius:8px;margin-bottom:4px;background:var(--background-secondary);border:1px dashed var(--interactive-accent);opacity:0.6;cursor:pointer;` }
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
    attr: { style: `display:flex;align-items:center;gap:${rowGap};padding:6px 10px;border-radius:8px;margin-bottom:4px;background:var(--background-secondary);border:1px solid ${isToday ? "var(--interactive-accent)" : "var(--background-modifier-border)"};` }
  });
  renderRow(row, isToday ? "Today" : dateStr, isToday, open, done, carriedIn, carriedAway, total, page.file.path);
}

if (pages.length === 0) {
  wkView.createEl("p", { text: "No other work notes in the last 7 days.", attr: { style: "color:var(--text-muted);font-size:0.85em;margin-top:4px;" } });
}

// ========== CARD TAB ==========
const bcPage = dv.page("Profile/Personal Baseball Card");
if (bcPage) {
  // 3D wrapper for perspective
  const cardWrap = panels["card"].createEl("div", {
    attr: { style: "width:260px;max-width:100%;margin:0 auto;perspective:600px;" }
  });
  const card = cardWrap.createEl("div", {
    attr: { style: "position:relative;border:1px solid var(--background-modifier-border);border-radius:12px;overflow:hidden;background:#faf6f0;box-shadow:0 2px 6px rgba(0,0,0,0.08);transition:transform 0.15s ease,box-shadow 0.15s ease;transform-style:preserve-3d;will-change:transform;" }
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
  // Archetype tagline
  hdr.createEl("div", {
    text: "Planful, methodical and results-oriented",
    attr: { style: "font-size:0.55em;color:var(--text-faint);font-style:italic;margin-top:3px;" }
  });

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
  // Glow filter for radar polygon
  svg += `<defs><filter id="radarGlow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>`;
  svg += `<polygon points="${polyPts}" fill="rgba(58,154,92,0.12)" stroke="#3a9a5c" stroke-width="1.8" stroke-linejoin="round" filter="url(#radarGlow)"/>`;
  traits.forEach((t,i) => {
    const [x,y] = rpt(i, t.v);
    const c = t.v >= 70 ? '#3a9a5c' : t.v >= 40 ? '#999' : '#c75c5c';
    svg += `<circle cx="${x}" cy="${y}" r="3.5" fill="${c}" stroke="var(--background-primary)" stroke-width="1"><title>${t.n}: ${t.v}%</title></circle>`;
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

  // Summary
  card.createEl("div", {
    text: "Strong thinker & executor · Low social engagement",
    attr: { style: "padding:2px 14px 0;text-align:center;font-size:0.58em;color:var(--text-faint);line-height:1.4;" }
  });

  // Footer: date + link
  const footer = card.createEl("div", {
    attr: { style: "padding:6px 14px 10px;display:flex;justify-content:space-between;align-items:center;" }
  });
  footer.createEl("span", {
    text: bcPage.py_date ? dv.date(bcPage.py_date).toFormat("MMM yyyy") : "",
    attr: { style: "font-size:0.55em;color:var(--text-faint);" }
  });
  footer.createEl("span", { attr: { style: "font-size:0.7em;" } }).innerHTML =
    '<a class="internal-link" data-href="Profile/Personal Baseball Card">Open Card →</a>';

  // === HOLOGRAPHIC EFFECT (mouse + touch) ===
  function applyHoloEffect(clientX, clientY) {
    const rect = card.getBoundingClientRect();
    const px = (clientX - rect.left) / rect.width;
    const py = (clientY - rect.top) / rect.height;
    const rotY = (px - 0.5) * 20;
    const rotX = (0.5 - py) * 20;
    const hue = Math.round(px * 360);
    const cx = px * 100, cy = py * 100;

    card.style.transform = `rotateY(${rotY}deg) rotateX(${rotX}deg)`;
    card.style.boxShadow = [
      `${-rotY*0.5}px ${rotX*0.5}px 15px rgba(0,0,0,0.1)`,
      `${-rotY*0.8}px ${rotX*0.8}px 30px hsla(${hue}, 60%, 65%, 0.15)`,
      `${-rotY*0.3}px ${rotX*0.3}px 8px hsla(${(hue+120)%360}, 50%, 70%, 0.1)`
    ].join(",");

    const edgeHue = (hue + 60) % 360;
    card.style.borderColor = `hsla(${edgeHue}, 70%, 75%, 0.5)`;
    card.style.borderWidth = "1px";
    const side = px > 0.5 ? "Right" : "Left";
    card.style[`border${side}Color`] = `hsla(${edgeHue}, 80%, 80%, 0.8)`;

    card.style.backgroundImage = [
      `radial-gradient(circle at ${cx}% ${cy}%, rgba(255,255,255,0.35) 0%, transparent 45%)`,
      `conic-gradient(from ${(px-0.5)*180}deg at ${cx}% ${cy}%, rgba(255,50,50,0.12), rgba(255,180,50,0.12), rgba(50,255,100,0.12), rgba(50,180,255,0.12), rgba(180,50,255,0.12), rgba(255,50,150,0.12), rgba(255,50,50,0.12))`,
      `repeating-linear-gradient(${135 + (px-0.5)*20}deg, transparent 0px, transparent 2px, rgba(255,255,255,0.06) 2px, rgba(255,255,255,0.06) 3px)`
    ].join(",");
    card.style.backgroundColor = "#faf6f0";
  }

  let isFirstMove = false;
  let floatTimer = null;
  function startInteraction() {
    if (floatTimer) { clearTimeout(floatTimer); floatTimer = null; }
    card.style.animation = "none";
    card.style.transform = "rotateY(0deg) rotateX(0deg)";
    card.style.transition = "none";
    void card.offsetHeight;
    card.style.transition = "transform 0.1s ease, box-shadow 0.1s ease";
    isFirstMove = true;
  }

  function endInteraction() {
    isFirstMove = false;
    card.style.transition = "transform 0.5s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.4s ease, border-color 0.4s ease, background-image 0.4s ease";
    card.style.transform = "rotateY(0deg) rotateX(0deg)";
    card.style.boxShadow = "0 2px 6px rgba(0,0,0,0.08)";
    card.style.borderColor = "var(--background-modifier-border)";
    card.style.borderLeftColor = "var(--background-modifier-border)";
    card.style.borderRightColor = "var(--background-modifier-border)";
    card.style.backgroundImage = "none";
    floatTimer = setTimeout(() => {
      card.style.animation = "bc-float 4s ease-in-out infinite";
      floatTimer = null;
    }, 600);
  }

  // Mouse events
  cardWrap.addEventListener("mousemove", (e) => {
    if (isFirstMove) {
      isFirstMove = false;
      requestAnimationFrame(() => applyHoloEffect(e.clientX, e.clientY));
    } else {
      applyHoloEffect(e.clientX, e.clientY);
    }
  });
  cardWrap.addEventListener("mouseenter", startInteraction);
  cardWrap.addEventListener("mouseleave", (e) => {
    const rect = cardWrap.getBoundingClientRect();
    if (e.clientX >= rect.left && e.clientX <= rect.right &&
        e.clientY >= rect.top && e.clientY <= rect.bottom) {
      return;
    }
    endInteraction();
  });

  // Touch events — only on card body, not footer links
  let touching = false;
  cardWrap.addEventListener("touchstart", (e) => {
    if (e.target.closest("a")) return; // let links work normally
    touching = true;
    startInteraction();
    const t = e.touches[0];
    applyHoloEffect(t.clientX, t.clientY);
  }, { passive: true });
  cardWrap.addEventListener("touchmove", (e) => {
    if (!touching) return;
    e.preventDefault();
    const t = e.touches[0];
    applyHoloEffect(t.clientX, t.clientY);
  }, { passive: false });
  cardWrap.addEventListener("touchend", () => {
    if (!touching) return;
    touching = false;
    endInteraction();
  });

  // Idle breathing animation
  const breatheId = 'bc-breathe';
  if (!document.getElementById(breatheId)) {
    const s = document.createElement('style');
    s.id = breatheId;
    s.textContent = `@keyframes bc-float{0%,100%{transform:translateY(0px)}50%{transform:translateY(-3px)}}`;
    document.head.appendChild(s);
  }
  card.style.animation = "bc-float 4s ease-in-out infinite";
}

// ========== SKILLS TAB ==========
const srPage = dv.page("Profile/Skill Radar");
if (srPage && srPage.skills) {
  const skills = Array.isArray(srPage.skills) ? srPage.skills : [srPage.skills];
  const stageRings = [
    { label: "探索", r: 0.25 },
    { label: "入门", r: 0.50 },
    { label: "熟练", r: 0.75 },
    { label: "精通", r: 1.00 },
  ];
  const cogColors = { "\u26A1": "#e57373", "\uD83C\uDFAF": "#4db6ac", "\uD83C\uDF0A": "#81c784" };

  const sz = 240, rcx = sz/2, rcy = sz/2, RR = 85;
  let rsvg = `<svg viewBox="0 0 ${sz} ${sz}" style="width:100%;max-width:220px;display:block;margin:0 auto;">`;

  // Concentric rings
  for (const s of stageRings) {
    rsvg += `<circle cx="${rcx}" cy="${rcy}" r="${s.r * RR}" fill="none" stroke="var(--text-faint)" stroke-width="0.6" opacity="0.45"/>`;
  }
  // Stage labels along right axis
  for (const s of stageRings) {
    rsvg += `<text x="${rcx + s.r * RR + 3}" y="${rcy - 3}" font-size="6" fill="var(--text-muted)" font-weight="500">${s.label}</text>`;
  }
  // Crosshairs
  rsvg += `<line x1="${rcx}" y1="${rcy - RR}" x2="${rcx}" y2="${rcy + RR}" stroke="var(--text-faint)" stroke-width="0.4" opacity="0.4"/>`;
  rsvg += `<line x1="${rcx - RR}" y1="${rcy}" x2="${rcx + RR}" y2="${rcy}" stroke="var(--text-faint)" stroke-width="0.4" opacity="0.4"/>`;
  // Center dot
  rsvg += `<circle cx="${rcx}" cy="${rcy}" r="1.5" fill="var(--text-faint)" opacity="0.5"/>`;

  // Plot skills as blips
  const sN = skills.length;
  skills.forEach((sk, si) => {
    const ss = String(sk.stage || "");
    const sc = String(sk.cognitive || "");
    // Stage → radial position
    let rPct = 0.25;
    if (ss.includes("\uD83C\uDFD4") || ss.includes("精通")) rPct = 1.0;
    else if (ss.includes("\uD83C\uDF33") || ss.includes("熟练")) rPct = 0.75;
    else if (ss.includes("\uD83C\uDF3F") || ss.includes("入门")) rPct = 0.5;
    // Cognitive → color
    let sCol = "#4db6ac";
    for (const [em, cl] of Object.entries(cogColors)) { if (sc.includes(em)) { sCol = cl; break; } }
    // Position (distribute evenly from top)
    const sAngle = -Math.PI/2 + (si * 2 * Math.PI / Math.max(sN, 1));
    const sx = rcx + rPct * RR * Math.cos(sAngle);
    const sy = rcy + rPct * RR * Math.sin(sAngle);
    // Glow
    rsvg += `<circle cx="${sx}" cy="${sy}" r="12" fill="${sCol}" opacity="0.1"/>`;
    rsvg += `<circle cx="${sx}" cy="${sy}" r="7" fill="${sCol}" opacity="0.15"/>`;
    // Dot
    rsvg += `<circle cx="${sx}" cy="${sy}" r="4" fill="${sCol}" stroke="var(--background-primary)" stroke-width="1.5"><title>${String(sk.name||"")}: ${ss}</title></circle>`;
    // Label
    const lbR = rPct * RR + 16;
    const lx = rcx + lbR * Math.cos(sAngle);
    const ly = rcy + lbR * Math.sin(sAngle);
    rsvg += `<text x="${lx}" y="${ly}" text-anchor="middle" dominant-baseline="central" font-size="7.5" font-weight="600" fill="var(--text-normal)">${String(sk.name||"")}</text>`;
  });
  rsvg += '</svg>';

  // Render
  const srWrap = panels["skills"].createEl("div", {
    attr: { style: "width:280px;max-width:100%;margin:0 auto;text-align:center;" }
  });
  const srChart = srWrap.createEl("div", { attr: { style: "padding:8px 0;" } });
  srChart.innerHTML = rsvg;

  // Legend
  const srLeg = srWrap.createEl("div", {
    attr: { style: "display:flex;justify-content:center;gap:12px;margin-top:2px;" }
  });
  for (const [em, label, col] of [["\u26A1","高认知","#e57373"],["\uD83C\uDFAF","高专注","#4db6ac"],["\uD83C\uDF0A","低认知","#81c784"]]) {
    const li = srLeg.createEl("span", { attr: { style: "display:flex;align-items:center;gap:3px;font-size:0.6em;color:var(--text-faint);" } });
    li.createEl("span", { attr: { style: `width:6px;height:6px;border-radius:50%;background:${col};display:inline-block;` } });
    li.createEl("span", { text: label });
  }

  // Practice links (skills with tracker field)
  const tracked = skills.filter(sk => sk.tracker);
  if (tracked.length > 0) {
    const prWrap = srWrap.createEl("div", {
      attr: { style: "margin-top:10px;padding:0 4px;" }
    });
    for (const sk of tracked) {
      const row = prWrap.createEl("div", {
        attr: { style: "display:flex;justify-content:space-between;align-items:center;padding:3px 0;" }
      });
      row.createEl("span", {
        text: `${String(sk.icon || "🎯")} ${String(sk.name || "")}`,
        attr: { style: "font-size:0.72em;color:var(--text-normal);" }
      });
      row.createEl("span", { attr: { style: "font-size:0.7em;" } }).innerHTML =
        `<a class="internal-link" data-href="${String(sk.tracker)}">Tracker →</a>`;
    }
  }

  // Footer
  const srFoot = srWrap.createEl("div", {
    attr: { style: "margin-top:8px;display:flex;justify-content:space-between;align-items:center;padding:0 4px;" }
  });
  srFoot.createEl("span", { text: `${skills.length} active`, attr: { style: "font-size:0.6em;color:var(--text-faint);" } });
  srFoot.createEl("span", { attr: { style: "font-size:0.7em;" } }).innerHTML =
    '<a class="internal-link" data-href="Profile/Skill Radar">Open Radar →</a>';
}
```

---

## Feeds

```dataviewjs
const isMobile = app.isMobile;

// Tab factory (same as Work section — each dataviewjs block has its own scope)
function createTabGroup(dvRef, tabs, defaultId) {
  const topBar = dvRef.el("div", "", {
    attr: { style: "display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px;" }
  });
  const panels = {};
  const btns = {};
  const tabPad = isMobile ? "3px 8px" : "4px 14px";
  const tabFont = isMobile ? "0.72em" : "0.82em";
  const segGap = isMobile ? "1px" : "2px";
  for (const t of tabs) panels[t.id] = dvRef.el("div", "", { attr: { style: "display:none;" } });
  function activate(id) {
    for (const k of Object.keys(panels)) {
      panels[k].style.display = k === id ? "block" : "none";
      btns[k].style.cssText = `padding:${tabPad};border-radius:7px;border:none;cursor:pointer;font-size:${tabFont};font-weight:600;transition:all 0.15s;` + (k === id
        ? "background:var(--background-primary);color:var(--text-normal);box-shadow:0 1px 3px rgba(0,0,0,0.08);"
        : "background:transparent;color:var(--text-muted);box-shadow:none;");
    }
  }
  const seg = topBar.createEl("div", {
    attr: { style: `display:inline-flex;gap:${segGap};padding:2px;border-radius:9px;background:var(--background-secondary);` }
  });
  for (const t of tabs) {
    btns[t.id] = seg.createEl("button", { text: t.label });
    btns[t.id].addEventListener("click", () => activate(t.id));
  }
  activate(defaultId);
  return { panels, topBar };
}

const { panels: fPanels } = createTabGroup(dv, [
  { id: "ai", label: "AI Digest" },
  { id: "gh", label: "GitHub Trending" },
  { id: "eng", label: "Eng Blogs" },
  { id: "pod", label: "Podcasts" },
], "ai");

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
    const scanned = page?.articles_scanned || "?";
    const selected = page?.articles_selected || "?";
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
      .filter(l => l.startsWith("> [!tip]"))
      .slice(0, 5);

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

// ========== ENGINEERING BLOGS TAB ==========
{
  const p = fPanels["eng"];
  const today = dv.date("today").toFormat("yyyy-MM-dd");
  const zhPath = `Feeds/Engineering-Blogs/${today}.md`;
  const enPath = `Feeds/Engineering-Blogs/${today}-en.md`;
  const zhFile = app.vault.getAbstractFileByPath(zhPath);
  const enFile = app.vault.getAbstractFileByPath(enPath);
  const reportFile = enFile || zhFile;

  if (reportFile) {
    const isEn = !!enFile;
    const reportPath = isEn ? enPath : zhPath;
    const page = dv.page(reportPath);
    const content = await app.vault.read(reportFile);
    const lines = content.split("\n");

    const postLines = lines
      .filter(l => l.startsWith("> [!tip]"))
      .slice(0, 5);

    const row = p.createEl("div", {
      attr: { style: "display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:8px;" }
    });
    const scanned = page?.articles_scanned || "?";
    const selected = page?.articles_selected || "?";
    row.createEl("span", {
      text: `🏗️ ${selected}/${scanned} posts`,
      attr: { style: "font-size:0.78em;color:var(--text-muted);" }
    });
    const links = row.createEl("div", { attr: { style: "margin-left:auto;display:flex;gap:8px;" } });
    links.createEl("a", { text: "中文", cls: "internal-link", attr: { "data-href": zhPath, style: "font-size:0.82em;" } });
    if (enFile) {
      links.createEl("a", { text: "EN", cls: "internal-link", attr: { "data-href": enPath, style: "font-size:0.82em;" } });
    }

    if (postLines.length > 0) {
      const preview = p.createEl("div", {
        attr: { style: "font-size:0.85em;line-height:1.8;padding:10px 12px;background:var(--background-secondary);border-radius:8px;border-left:3px solid var(--interactive-accent);" }
      });
      for (const line of postLines) {
        const cleaned = line.replace(/^>\s*\[!tip\]\s*/, "");
        preview.createEl("div", { text: cleaned });
      }
    }
  } else {
    p.createEl("div", {
      text: "No engineering blogs report for today yet. Run /feeds/engineering-blogs in Claude Code to generate.",
      attr: { style: "font-size:0.85em;color:var(--text-muted);padding:12px;border-radius:8px;background:var(--background-secondary);border:1px dashed var(--background-modifier-border);" }
    });
  }
  p.createEl("div", { attr: { style: "margin-top:8px;font-size:0.82em;" } }).innerHTML =
    '<a class="internal-link" data-href="Feeds/Engineering-Blogs/Dashboard">All reports →</a>';
}

// ========== PODCASTS TAB ==========
{
  const p = fPanels["pod"];
  const eps = dv.pages('"Podcasts/episodes"')
    .where(ep => ep.type === "podcast-episode")
    .sort(ep => ep.date, "desc")
    .limit(5);

  if (eps.length > 0) {
    const stats = dv.pages('"Podcasts/episodes"').where(ep => ep.type === "podcast-episode");
    const unlistened = stats.where(ep => ep.status === "unlistened").length;
    const total = stats.length;
    const row = p.createEl("div", {
      attr: { style: "display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:8px;" }
    });
    row.createEl("span", {
      text: `🎧 ${unlistened} unlistened / ${total} total`,
      attr: { style: "font-size:0.78em;color:var(--text-muted);" }
    });

    const list = p.createEl("div", {
      attr: { style: "display:flex;flex-direction:column;gap:6px;" }
    });
    for (const ep of eps) {
      const card = list.createEl("div", {
        attr: { style: "display:flex;align-items:center;gap:10px;padding:8px 12px;background:var(--background-secondary);border-radius:8px;border-left:3px solid " + (ep.score >= 7 ? "var(--interactive-accent)" : "var(--background-modifier-border)") + ";" }
      });
      // Score badge
      card.createEl("span", {
        text: ep.score != null ? String(ep.score) : "–",
        attr: { style: "flex-shrink:0;width:2.2em;text-align:center;font-size:0.82em;font-weight:700;color:" + (ep.score >= 7 ? "var(--interactive-accent)" : "var(--text-muted)") + ";" }
      });
      // Info column
      const info = card.createEl("div", { attr: { style: "flex:1;min-width:0;overflow:hidden;" } });
      const titleEl = info.createEl("div", { attr: { style: "font-size:0.85em;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" } });
      titleEl.innerHTML = `<a class="internal-link" data-href="${ep.file.path}">${ep.title || ep.file.name}</a>`;
      info.createEl("div", {
        text: `${ep.podcast || ""} · ${ep.date || ""} · ${ep.duration || ""}`,
        attr: { style: "font-size:0.75em;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" }
      });
      // Status icon
      const statusIcon = ep.status === "listened" ? "✅" : ep.status === "archived" ? "🗄️" : "📥";
      card.createEl("span", {
        text: statusIcon,
        attr: { style: "flex-shrink:0;font-size:0.85em;" }
      });
    }
  } else {
    p.createEl("div", {
      text: "No podcast episodes yet. Run /feeds/podcast to fetch.",
      attr: { style: "font-size:0.85em;color:var(--text-muted);padding:12px;border-radius:8px;background:var(--background-secondary);border:1px dashed var(--background-modifier-border);" }
    });
  }
  p.createEl("div", { attr: { style: "margin-top:8px;font-size:0.82em;" } }).innerHTML =
    '<a class="internal-link" data-href="Podcasts/Podcasts">All episodes →</a>';
}
```

## CC Plugins <span style="float:right;font-size:0.75em;color:var(--text-muted);">Weekly 📦</span>

```dataviewjs
const isMobile = app.isMobile;

// Find latest weekly report by sorting YYYY-WXX filenames descending
const reports = dv.pages('"Feeds/CC-Plugins"')
  .where(p => p.file.name !== "Dashboard" && !p.file.name.endsWith("-en") && !p.file.path.includes("archive"))
  .sort(p => p.file.name, "desc");

if (reports.length === 0) {
  dv.el("div", "No CC Plugins reports yet. Run /feeds/cc-plugins to generate.", {
    attr: { style: "font-size:0.85em;color:var(--text-muted);padding:12px;border-radius:8px;background:var(--background-secondary);border:1px dashed var(--background-modifier-border);" }
  });
} else {
  const latest = reports[0];
  const week = latest.week || latest.file.name;
  const newCount = latest.plugins_new || 0;
  const updatedCount = latest.plugins_updated || 0;
  const discovered = latest.plugins_discovered || 0;

  // Header line with 中文/EN links
  const enPath = `Feeds/CC-Plugins/${latest.file.name}-en.md`;
  const enFile = app.vault.getAbstractFileByPath(enPath);

  const hdr = dv.el("div", "", {
    attr: { style: "display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:8px;" }
  });
  hdr.createEl("span", {
    text: `📦 ${week} · ${newCount} new · ${updatedCount} updated`,
    attr: { style: "font-size:0.78em;color:var(--text-muted);" }
  });
  const links = hdr.createEl("div", { attr: { style: "margin-left:auto;display:flex;gap:8px;" } });
  links.createEl("a", { text: "中文", cls: "internal-link", attr: { "data-href": latest.file.path, style: "font-size:0.82em;" } });
  if (enFile) {
    links.createEl("a", { text: "EN", cls: "internal-link", attr: { "data-href": enPath, style: "font-size:0.82em;" } });
  }

  // Read the raw file content to extract plugin entries
  const content = await dv.io.load(latest.file.path);
  const lines = content.split("\n");

  // Parse callout blocks: > [!tip] or > [!info]
  const newPlugins = [];
  const updatedPlugins = [];
  let currentSection = null;
  let currentEntry = [];

  for (const line of lines) {
    if (line.startsWith("## 🆕")) { currentSection = "new"; continue; }
    if (line.startsWith("## 📦")) { currentSection = "updated"; continue; }
    if (line.startsWith("## 📊") || line.startsWith("---")) {
      if (currentEntry.length > 0 && currentSection) {
        (currentSection === "new" ? newPlugins : updatedPlugins).push(currentEntry.join("\n"));
        currentEntry = [];
      }
      currentSection = line.startsWith("## 📊") ? null : currentSection;
      continue;
    }
    if (currentSection && line.startsWith("> [!tip]")) {
      if (currentEntry.length > 0) {
        newPlugins.push(currentEntry.join("\n"));
      }
      currentEntry = [line];
    } else if (currentSection && line.startsWith("> [!info]")) {
      if (currentEntry.length > 0) {
        updatedPlugins.push(currentEntry.join("\n"));
      }
      currentEntry = [line];
    } else if (currentSection && (line.startsWith(">") || line === "")) {
      if (line === "" && currentEntry.length > 0) {
        (currentSection === "new" ? newPlugins : updatedPlugins).push(currentEntry.join("\n"));
        currentEntry = [];
      } else if (line.startsWith(">")) {
        currentEntry.push(line);
      }
    }
  }
  if (currentEntry.length > 0 && currentSection) {
    (currentSection === "new" ? newPlugins : updatedPlugins).push(currentEntry.join("\n"));
  }

  // Render new discoveries (top 5)
  const maxShow = 5;
  const fontSize = isMobile ? "0.78em" : "0.85em";
  const gap = isMobile ? "4px" : "6px";

  if (newPlugins.length > 0) {
    dv.el("div", "🆕 New Discoveries", {
      attr: { style: `font-size:${fontSize};font-weight:600;margin:8px 0 4px 0;` }
    });
    const list = dv.el("div", "", { attr: { style: `display:flex;flex-direction:column;gap:${gap};` } });
    for (const entry of newPlugins.slice(0, maxShow)) {
      // Extract name, score, summary from callout
      const tipMatch = entry.match(/>\s*\[!tip\]\s*(?:\S+)\s+(\S+)\s+⭐\s*([\d.]+)\s*·\s*(\S+)\s+(.*)/);
      const summaryMatch = entry.match(/>\s*>\s*(.+)/);
      const summary = summaryMatch ? summaryMatch[1] : "";
      if (tipMatch) {
        const [, name, score, catEmoji, catLabel] = tipMatch;
        const scoreNum = parseFloat(score);
        const scoreColor = scoreNum >= 8 ? "var(--text-accent)" : scoreNum >= 6 ? "var(--text-normal)" : "var(--text-muted)";
        const row = list.createEl("div", {
          attr: { style: `font-size:${fontSize};padding:4px 0;border-bottom:1px solid var(--background-modifier-border);` }
        });
        row.innerHTML = `<span style="color:${scoreColor};font-weight:600;">⭐ ${score}</span> <strong>${name}</strong> <span style="color:var(--text-muted);">${catEmoji}</span> <span style="font-size:0.9em;color:var(--text-muted);">— ${summary.substring(0, 60)}${summary.length > 60 ? "…" : ""}</span>`;
      }
    }
  }

  // Render version updates (top 5)
  if (updatedPlugins.length > 0) {
    dv.el("div", "📦 Version Updates", {
      attr: { style: `font-size:${fontSize};font-weight:600;margin:10px 0 4px 0;` }
    });
    const uList = dv.el("div", "", { attr: { style: `display:flex;flex-direction:column;gap:${gap};` } });
    for (const entry of updatedPlugins.slice(0, maxShow)) {
      const infoMatch = entry.match(/>\s*\[!info\]\s*(\S+)\s+`([^`]+)`\s*→\s*`([^`]+)`/);
      const summaryMatch = entry.match(/>\s*>\s*(.+)/);
      const summary = summaryMatch ? summaryMatch[1] : "";
      if (infoMatch) {
        const [, name, oldVer, newVer] = infoMatch;
        const row = uList.createEl("div", {
          attr: { style: `font-size:${fontSize};padding:4px 0;border-bottom:1px solid var(--background-modifier-border);` }
        });
        row.innerHTML = `<strong>${name}</strong> <code style="font-size:0.85em;">${oldVer}</code> → <code style="font-size:0.85em;">${newVer}</code> <span style="font-size:0.9em;color:var(--text-muted);">— ${summary.substring(0, 50)}${summary.length > 50 ? "…" : ""}</span>`;
      }
    }
  }

  // Footer link
  dv.el("div", "", { attr: { style: "margin-top:8px;font-size:0.82em;" } }).innerHTML =
    '<a class="internal-link" data-href="Feeds/CC-Plugins/Dashboard">All reports →</a>';
}
```

---

## Learning

```dataviewjs
const isMobile = app.isMobile;

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

const WEEKS = lastNWeeks(isMobile ? 6 : 10);
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

    // Activity squares (6 weeks on mobile, 10 on desktop)
    const dotSize = isMobile ? "8px" : "10px";
    const dotGap = isMobile ? "2px" : "3px";
    const dotsWrap = card.createEl("div", { attr: { style: `display:flex;align-items:center;gap:${dotGap};padding:0 12px;flex-shrink:0;` } });
    for (const w of [...WEEKS].reverse()) {
      if (logMap[w]) {
        dotsWrap.createEl("a", {
          attr: { class: "internal-link", "data-href": logMap[w].file.path, title: w, style: `width:${dotSize};height:${dotSize};border-radius:2px;background:var(--color-accent);display:inline-block;opacity:0.85;` }
        });
      } else {
        const isCurrent = w === currentWeek;
        dotsWrap.createEl("div", {
          attr: { title: w, style: `width:${dotSize};height:${dotSize};border-radius:2px;${isCurrent ? "border:1.5px dashed var(--color-accent);opacity:0.7;" : "background:var(--background-modifier-border);opacity:0.5;"}` }
        });
      }
    }
  }

  container.createEl("div", { attr: { style: "margin-top:12px;font-size:0.85em;" } }).innerHTML =
    `<a class="internal-link" data-href="Learning/Dashboard.md">Full dashboard →</a>`;
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
  `<a class="internal-link" data-href="Learning/Books/Books Index">Open Books Index →</a>`;
```

### Articles

```dataviewjs
const container = dv.el("div", "");

const matter = dv.pages('"Matter"').where(p => p.file.name !== "Matter Index");
const instapaper = dv.pages('"Instapaper Notes"').where(p => p.file.name !== "Instapaper Index");
const all = [...matter, ...instapaper].sort((a, b) => b.file.mtime - a.file.mtime);

// Header with count badge
const header = container.createEl("div", { attr: { style: "display:flex;align-items:center;gap:8px;margin-bottom:8px;" } });
header.createEl("span", { text: "Recent", attr: { style: "font-weight:600;font-size:0.85em;" } });
header.createEl("span", {
  text: String(all.length),
  attr: { style: "font-size:0.65em;padding:1px 7px;border-radius:10px;background:var(--background-primary);color:var(--text-muted);border:1px solid var(--background-modifier-border);" }
});

// Unified article list
const list = container.createEl("div", "");
const recent = all.slice(0, 10);
for (const p of recent) {
  const source = p.file.path.startsWith("Matter/") ? "Matter" : "Instapaper";
  const row = list.createEl("div", { attr: { style: "display:flex;align-items:center;justify-content:space-between;gap:8px;padding:5px 0;border-bottom:1px solid var(--background-modifier-border);" } });
  const link = row.createEl("div", { attr: { style: "font-size:0.82em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;min-width:0;" } });
  link.innerHTML = `<a class="internal-link" data-href="${p.file.path}">${p.file.name}</a>`;
  row.createEl("span", {
    text: source,
    attr: { style: "font-size:0.65em;padding:1px 6px;border-radius:8px;background:var(--background-primary);color:var(--text-muted);border:1px solid var(--background-modifier-border);white-space:nowrap;flex-shrink:0;" }
  });
}

// Footer links
container.createEl("div", { attr: { style: "margin-top:8px;font-size:0.8em;display:flex;gap:12px;" } }).innerHTML =
  `<a class="internal-link" data-href="Matter/Matter Index" style="color:var(--text-faint);">All Matter →</a>` +
  `<a class="internal-link" data-href="Instapaper Notes/Instapaper Index" style="color:var(--text-faint);">All Instapaper →</a>`;
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

## Recent Updates

```dataview
TABLE file.mtime AS "Modified"
FROM ""
SORT file.mtime DESC
LIMIT 5
```

---

## Vault Stats

```dataviewjs
const folders = dv.pages('').groupBy(p => p.file.folder.split('/')[0]).sort(g => g.rows.length, 'desc');
dv.table(["Folder", "Notes"], folders.map(g => [g.key || "Root", g.rows.length]));
```

---

<small>🚀 [[GETTING_STARTED|Getting Started]] · 📊 [[system/registry|Registry]] · 📖 [[system/README|Module Docs]]</small>

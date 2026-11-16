---
tags: [learning/dashboard]
---

> 🏠 [[Home]]

```dataviewjs
// ─── Helpers ──────────────────────────────────────────────────────────────────

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

function renderPhaseContent(container, content) {
  const lines = content.split("\n");
  let inTable = false;
  for (const raw of lines) {
    const line = raw.trimEnd();
    if (!line.trim()) { inTable = false; continue; }
    if (/^\|[-\s|]+\|/.test(line)) continue;
    if (line.startsWith("|")) {
      const cells = line.split("|").map(c => c.trim()).filter(Boolean);
      if (cells.length === 0) continue;
      if (!inTable) {
        inTable = true;
        const hdr = container.createEl("div", { attr: { style: "display:flex;gap:8px;margin-bottom:2px;" } });
        for (const c of cells) {
          hdr.createEl("span", { attr: { style: "font-size:0.65em;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:var(--text-faint);flex:1;" } }).innerHTML = mdInline(c);
        }
      } else {
        const row = container.createEl("div", { attr: { style: "display:flex;gap:8px;margin-bottom:3px;padding:3px 0;border-top:1px solid var(--background-modifier-border);" } });
        for (const c of cells) {
          row.createEl("span", { attr: { style: "font-size:0.78em;color:var(--text-normal);flex:1;line-height:1.4;" } }).innerHTML = mdInline(c);
        }
      }
      continue;
    }
    inTable = false;
    if (/^[-*]\s+/.test(line)) {
      const item = container.createEl("div", { attr: { style: "font-size:0.8em;color:var(--text-normal);margin-bottom:3px;padding-left:12px;text-indent:-12px;" } });
      item.innerHTML = "• " + mdInline(line.replace(/^[-*]\s+/, ""));
      continue;
    }
    if (/^\*\*/.test(line)) {
      const el = container.createEl("div", { attr: { style: "font-size:0.8em;color:var(--text-muted);margin-top:6px;margin-bottom:3px;" } });
      el.innerHTML = mdInline(line);
      continue;
    }
    const el = container.createEl("div", { attr: { style: "font-size:0.8em;color:var(--text-muted);margin-bottom:2px;" } });
    el.innerHTML = mdInline(line);
  }
}

function mdInline(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`(.+?)`/g, "<code style='font-size:0.9em;background:var(--background-primary);padding:1px 4px;border-radius:3px;'>$1</code>")
    .replace(/✅/g, "<span style='color:#2b8a3e;'>✅</span>")
    .replace(/🔄/g, "<span style='color:#1971c2;'>🔄</span>")
    .replace(/⏳/g, "<span style='color:#868e96;'>⏳</span>");
}

const WEEKS = lastNWeeks(12);
const currentWeek = WEEKS[WEEKS.length - 1];
const DISPLAY_WEEKS = [...WEEKS].reverse();

const STATUS_STYLE = {
  active:    { bg: "#d3f9d8", color: "#2b8a3e" },
  paused:    { bg: "#fff3bf", color: "#e67700" },
  completed: { bg: "#f1f3f5", color: "#868e96" },
};

// ─── Data ─────────────────────────────────────────────────────────────────────

const plans = dv.pages('"Learning"')
  .where(p => p.file.name === "00_plan")
  .sort(p => p.started, 'asc')
  .sort(p => p.status === "active" ? 0 : 1, "asc");

const allLogs = dv.pages('"Learning"')
  .where(p => p.week !== undefined);

// ─── Layout root ──────────────────────────────────────────────────────────────

const root = dv.el("div", "", { attr: { style: "font-family:var(--font-interface);max-width:860px;" } });

function sectionHeader(label) {
  root.createEl("div", {
    text: label,
    attr: { style: "font-size:0.7em;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-muted);margin:28px 0 10px;" }
  });
}

// ─── 1. Plans (tabbed) ────────────────────────────────────────────────────────

sectionHeader("Plans");

const tabBar = root.createEl("div", {
  attr: { style: "display:flex;border-bottom:2px solid var(--background-modifier-border);margin-bottom:16px;gap:0;" }
});
const plansContent = root.createEl("div");

const planTabs = [];
const planPanels = [];

const showPlan = (idx) => {
  planTabs.forEach((tab, i) => {
    const active = i === idx;
    tab.style.borderBottomColor = active ? "var(--color-accent)" : "transparent";
    tab.style.color = active ? "var(--color-accent)" : "var(--text-muted)";
    tab.style.fontWeight = active ? "700" : "500";
  });
  planPanels.forEach((panel, i) => {
    panel.style.display = i === idx ? "" : "none";
  });
};

let planIdx = 0;
for (const p of plans) {
  const idx = planIdx++;
  const code = p.file.folder.split("/").pop();
  const planLogs = allLogs.filter(l => l.code === code);
  const sortedLogs = planLogs.sort(l => l.week, 'desc');
  const lastLog = sortedLogs.length > 0 ? sortedLogs[0].week : null;
  const weeksElapsed = p.started
    ? Math.floor((new Date() - p.started.toJSDate()) / (7 * 24 * 60 * 60 * 1000)) + 1
    : null;
  const startedStr = p.started ? p.started.toFormat("yyyy-MM-dd") : "—";
  const status = p.status || "active";
  const ss = STATUS_STYLE[status] || STATUS_STYLE.active;

  // Parse phases with full content
  const planContent = await dv.io.load(p.file.path);
  const phases = [];
  const sectionMatch = planContent.match(/## 阶段划分([\s\S]*?)(?=\n## |\n```|$)/);
  if (sectionMatch) {
    const parts = sectionMatch[1].split(/(?=^### )/m).filter(pt => pt.trim());
    for (const part of parts) {
      const headingMatch = part.match(/^### (Phase \d+)(?:\s*[—–-]+\s*(.+))?/);
      if (headingMatch) {
        const afterHeading = part.slice(part.indexOf("\n") + 1).trim();
        phases.push({ label: headingMatch[1], desc: headingMatch[2] ? headingMatch[2].trim() : "", content: afterHeading });
      }
    }
  }
  const currentPhase = p.phase || 1;

  // ── Tab button
  const tab = tabBar.createEl("button", {
    text: code,
    attr: {
      "data-tab": String(idx),
      style: `padding:8px 18px;border:none;border-bottom:2px solid ${idx === 0 ? "var(--color-accent)" : "transparent"};margin-bottom:-2px;background:transparent;color:${idx === 0 ? "var(--color-accent)" : "var(--text-muted)"};cursor:pointer;font-weight:${idx === 0 ? "700" : "500"};font-size:0.88em;letter-spacing:0.04em;`
    }
  });
  tab.addEventListener("click", () => showPlan(idx));
  planTabs.push(tab);

  // ── Panel
  const panel = plansContent.createEl("div", {
    attr: { style: `display:${idx === 0 ? "" : "none"};` }
  });
  planPanels.push(panel);

  // Row 1: target + status chip
  const row1 = panel.createEl("div", { attr: { style: "display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:10px;" } });
  const targetEl = row1.createEl("div", { attr: { style: "font-size:0.95em;font-weight:600;color:var(--text-normal);line-height:1.4;flex:1;" } });
  targetEl.textContent = p.target || code;
  row1.createEl("span", {
    text: status,
    attr: { style: `font-size:0.72em;font-weight:600;background:${ss.bg};color:${ss.color};border-radius:20px;padding:2px 9px;white-space:nowrap;flex-shrink:0;margin-top:3px;` }
  });

  // Row 2: stats row
  const row2 = panel.createEl("div", { attr: { style: "display:flex;flex-wrap:wrap;gap:20px;margin-bottom:12px;" } });
  const stat = (label, value) => {
    const s = row2.createEl("span", { attr: { style: "display:flex;flex-direction:column;gap:1px;" } });
    s.createEl("span", { text: label, attr: { style: "font-size:0.65em;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;color:var(--text-faint);" } });
    s.createEl("span", { text: value, attr: { style: "font-size:0.82em;color:var(--text-muted);" } });
  };
  stat("Started", startedStr);
  stat("Plan week", weeksElapsed !== null ? `Wk ${weeksElapsed}` : "—");
  stat("Logged", `${planLogs.length} wk${planLogs.length !== 1 ? "s" : ""}`);
  stat("Coverage", weeksElapsed ? `${Math.round((planLogs.length / weeksElapsed) * 100)}%` : "—");
  stat("Last log", lastLog || "—");

  // Row 3: phase pills + detail panel
  if (phases.length > 0) {
    const phaseRow = panel.createEl("div", { attr: { style: "display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:8px;" } });
    const phaseDetail = panel.createEl("div", {
      attr: { style: "padding:10px 12px;background:var(--background-primary);border-radius:6px;border:1px solid var(--background-modifier-border);" }
    });

    const showPhase = (phaseIdx) => {
      phaseDetail.empty();
      const ph = phases[phaseIdx];
      if (!ph) return;
      phaseDetail.createEl("div", { attr: { style: "font-size:0.8em;font-weight:700;color:var(--text-normal);margin-bottom:8px;" } })
        .textContent = ph.label + (ph.desc ? " — " + ph.desc : "");
      if (ph.content) renderPhaseContent(phaseDetail, ph.content);
      phaseRow.querySelectorAll("[data-phase-pill]").forEach((pill, i) => {
        const active = i === phaseIdx;
        pill.style.background = active ? "var(--color-accent)" : "transparent";
        pill.style.color = active ? "#fff" : "var(--text-faint)";
        pill.style.borderColor = active ? "var(--color-accent)" : "var(--background-modifier-border)";
        pill.style.fontWeight = active ? "700" : "400";
      });
    };

    for (let i = 0; i < phases.length; i++) {
      const isCurrent = (i + 1) === currentPhase;
      const pill = phaseRow.createEl("span", {
        text: phases[i].label,
        attr: {
          "data-phase-pill": String(i),
          style: `font-size:0.7em;font-weight:${isCurrent ? "700" : "400"};padding:2px 9px;border-radius:20px;border:1px solid ${isCurrent ? "var(--color-accent)" : "var(--background-modifier-border)"};background:${isCurrent ? "var(--color-accent)" : "transparent"};color:${isCurrent ? "#fff" : "var(--text-faint)"};white-space:nowrap;cursor:pointer;`
        }
      });
      pill.addEventListener("click", () => showPhase(i));
    }
    showPhase(currentPhase - 1);
  }
}

// ─── 2. Activity Grid ─────────────────────────────────────────────────────────

sectionHeader("Activity — last 12 weeks");

const gridWrap = root.createEl("div", { attr: { style: "overflow-x:auto;padding-bottom:4px;" } });
const gridInner = gridWrap.createEl("div", { attr: { style: "display:inline-block;min-width:100%;" } });

// Year header row — spans consecutive weeks belonging to the same year
const yearGroups = [];
for (const w of DISPLAY_WEEKS) {
  const year = w.split("-W")[0];
  if (yearGroups.length === 0 || yearGroups[yearGroups.length - 1].year !== year) {
    yearGroups.push({ year, count: 1 });
  } else {
    yearGroups[yearGroups.length - 1].count++;
  }
}
const yearRow = gridInner.createEl("div", { attr: { style: "display:flex;align-items:center;gap:4px;margin-bottom:1px;padding-left:56px;" } });
for (const group of yearGroups) {
  const w = group.count * 28 + (group.count - 1) * 4;
  yearRow.createEl("div", {
    text: group.year,
    attr: { style: `width:${w}px;font-size:0.6em;font-weight:600;color:var(--text-faint);flex-shrink:0;` }
  });
}

const weekRow = gridInner.createEl("div", { attr: { style: "display:flex;align-items:center;gap:4px;margin-bottom:6px;padding-left:56px;" } });
for (const w of DISPLAY_WEEKS) {
  const label = "W" + w.split("-W")[1];
  const isCurrent = w === currentWeek;
  weekRow.createEl("div", {
    text: label,
    attr: { style: `width:28px;text-align:center;font-size:0.65em;font-weight:${isCurrent ? "700" : "400"};color:${isCurrent ? "var(--color-accent)" : "var(--text-faint)"};flex-shrink:0;` }
  });
}

for (const p of plans) {
  const code = p.file.folder.split("/").pop();
  const planLogs = allLogs.filter(l => l.code === code);
  const logMap = {};
  for (const l of planLogs) logMap[l.week] = l;

  const planRow = gridInner.createEl("div", { attr: { style: "display:flex;align-items:center;gap:4px;margin-bottom:5px;" } });
  const label = planRow.createEl("div", { attr: { style: "width:52px;flex-shrink:0;text-align:right;padding-right:8px;" } });
  label.innerHTML = `<a class="internal-link" data-href="${p.file.path}" style="font-size:0.75em;font-weight:700;color:var(--text-muted);text-decoration:none;">${code}</a>`;

  for (const w of DISPLAY_WEEKS) {
    const isCurrent = w === currentWeek;
    if (logMap[w]) {
      planRow.createEl("a", { attr: { class: "internal-link", "data-href": logMap[w].file.path, title: w, style: "width:28px;height:20px;background:var(--color-accent);border-radius:4px;display:inline-block;flex-shrink:0;opacity:0.85;" } });
    } else if (isCurrent) {
      planRow.createEl("div", { attr: { title: w, style: "width:28px;height:20px;border:2px dashed var(--color-accent);border-radius:4px;flex-shrink:0;opacity:0.6;" } });
    } else {
      planRow.createEl("div", { attr: { title: w, style: "width:28px;height:20px;background:var(--background-modifier-border);border-radius:4px;flex-shrink:0;opacity:0.4;" } });
    }
  }
}

const legend = root.createEl("div", { attr: { style: "display:flex;align-items:center;gap:12px;margin-top:8px;margin-bottom:4px;" } });
const mkLegend = (style, text) => {
  const item = legend.createEl("div", { attr: { style: "display:flex;align-items:center;gap:5px;" } });
  item.createEl("div", { attr: { style } });
  item.createEl("span", { text, attr: { style: "font-size:0.68em;color:var(--text-muted);" } });
};
mkLegend("width:14px;height:14px;background:var(--color-accent);border-radius:3px;opacity:0.85;", "logged");
mkLegend("width:14px;height:14px;border:2px dashed var(--color-accent);border-radius:3px;opacity:0.6;", "current (no log)");
mkLegend("width:14px;height:14px;background:var(--background-modifier-border);border-radius:3px;opacity:0.4;", "no log");

// ─── 3. Recent Activity ───────────────────────────────────────────────────────

sectionHeader("Recent Activity");

const recentLogs = allLogs.sort(l => l.week, 'desc').limit(8).array();
const logCodes = [...new Set(recentLogs.map(l => l.code || l.file.folder.split("/").pop()))].filter(Boolean);

const filterRow = root.createEl("div", { attr: { style: "display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;" } });
const activityContainer = root.createEl("div");

const makeFilterBtn = (code, label) => {
  const isAll = code === "all";
  const btn = filterRow.createEl("button", {
    text: label,
    attr: {
      "data-filter": code,
      style: `font-size:0.72em;padding:3px 10px;border-radius:20px;cursor:pointer;border:1px solid ${isAll ? "var(--color-accent)" : "var(--background-modifier-border)"};background:${isAll ? "var(--color-accent)" : "var(--background-secondary)"};color:${isAll ? "#fff" : "var(--text-muted)"};`
    }
  });
  btn.addEventListener("click", () => {
    filterRow.querySelectorAll("button").forEach(b => {
      const active = b.dataset.filter === code;
      b.style.borderColor = active ? "var(--color-accent)" : "var(--background-modifier-border)";
      b.style.background = active ? "var(--color-accent)" : "var(--background-secondary)";
      b.style.color = active ? "#fff" : "var(--text-muted)";
    });
    activityContainer.querySelectorAll("[data-log-code]").forEach(card => {
      card.style.display = (code === "all" || card.dataset.logCode === code) ? "" : "none";
    });
  });
};

makeFilterBtn("all", "All");
for (const code of logCodes) makeFilterBtn(code, code);

for (const log of recentLogs) {
  const code = log.code || log.file.folder.split("/").pop();
  const content = await dv.io.load(log.file.path);
  const match = content.match(/## 实际完成\n([\s\S]*?)(?=\n## |\n```|$)/);
  const rawCompleted = match ? match[1].trim() : null;
  const lines = rawCompleted
    ? rawCompleted.split("\n").filter(l => l.trim() && !l.startsWith("<!--")).map(l => l.replace(/^[-*]\s+/, "• "))
    : null;

  const card = activityContainer.createEl("div", {
    attr: { "data-log-code": code, style: "display:flex;gap:12px;margin-bottom:10px;padding:12px 14px;background:var(--background-secondary);border-radius:8px;border:1px solid var(--background-modifier-border);" }
  });
  card.createEl("div", { attr: { style: "width:3px;background:var(--color-accent);border-radius:2px;flex-shrink:0;" } });
  const body = card.createEl("div", { attr: { style: "flex:1;min-width:0;" } });
  const hdr = body.createEl("div", { attr: { style: "display:flex;align-items:center;gap:8px;margin-bottom:7px;" } });
  hdr.createEl("span", { text: code, attr: { style: "font-size:0.72em;font-weight:700;background:var(--color-accent);color:#fff;border-radius:4px;padding:2px 7px;letter-spacing:0.05em;flex-shrink:0;" } });
  hdr.createEl("span", { text: log.week, attr: { style: "font-size:0.85em;font-weight:600;color:var(--text-normal);" } });
  hdr.innerHTML += `<a class="internal-link" data-href="${log.file.path}" style="margin-left:auto;font-size:0.72em;color:var(--text-muted);border:1px solid var(--background-modifier-border);border-radius:4px;padding:1px 7px;text-decoration:none;flex-shrink:0;">open →</a>`;

  if (lines && lines.length > 0) {
    body.createEl("div", { text: lines.join("\n"), attr: { style: "font-size:0.8em;color:var(--text-normal);line-height:1.7;white-space:pre-line;" } });
  } else {
    body.createEl("div", { text: "No activity logged yet.", attr: { style: "font-size:0.8em;color:var(--text-faint);font-style:italic;" } });
  }
}
```

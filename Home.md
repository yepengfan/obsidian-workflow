---
cssclasses:
  - dashboard
banner: "![[home.jpg]]"
banner_x: 0.5
banner_y: 0
---

## Work

```dataviewjs
const row = dv.el("div", "", { attr: { style: "display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:4px;" } });

// Navigation buttons
const navDash = row.createEl("button", {
  text: "Work Dashboard",
  attr: { style: "padding:6px 14px;border:1px solid var(--background-modifier-border);border-radius:7px;background:var(--background-secondary);color:var(--text-normal);cursor:pointer;font-size:0.85em;" }
});
navDash.addEventListener("click", () => app.workspace.openLinkText("Work/Work Dashboard", "", false));

const navToday = row.createEl("button", {
  text: dv.date("today").toFormat("yyyy-MM-dd"),
  attr: { style: "padding:6px 14px;border:1px solid var(--background-modifier-border);border-radius:7px;background:var(--background-secondary);color:var(--text-normal);cursor:pointer;font-size:0.85em;" }
});
navToday.addEventListener("click", () => app.workspace.openLinkText("Work/" + dv.date("today").toFormat("yyyy/yyyy-MM-dd"), "", false));

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

**Today's open tasks:**

```dataviewjs
const today = dv.date("today").toFormat("yyyy-MM-dd");
const todayPage = dv.page("Work/" + today.slice(0, 4) + "/" + today);
if (todayPage) {
    const tasks = todayPage.file.tasks.where(t => !t.completed);
    if (tasks.length > 0) {
        dv.taskList(tasks, false);
    } else {
        dv.paragraph("All done for today!");
    }
} else {
    dv.paragraph("No daily note yet — click today in Calendar to start.");
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

```dataview
TABLE length(rows) AS "Notes"
FROM "Matter" OR "Instapaper Notes"
FLATTEN file.folder AS source
GROUP BY source
SORT length(rows) DESC
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
        const sq = dotsWrap.createEl("a", {
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

  container.innerHTML += `<div style="margin-top:8px;font-size:0.78em;"><a class="internal-link" data-href="Learning/Dashboard.md" style="color:var(--text-muted);">→ Full dashboard</a></div>`;
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

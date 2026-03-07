---
tags: [MOC]
cssclasses: [wide-page]
---

# Books Index

## Currently Reading

```dataviewjs
const fmt = (d) => d ? dv.date(d).toFormat("yyyy-MM-dd") : "";
const pages = dv.pages('"Books"').where(p => p.file.name === "00_meta" && p.status === "reading").sort(p => p.started, "desc");
const rows = pages.map(p => {
  const mapFile = dv.page(p.file.folder + "/00_map");
  const link = mapFile ? dv.fileLink(mapFile.file.path, false, p.title) : p.file.link;
  return [link, p.author, fmt(p.started)];
});
dv.table(["Book", "Author", "Started"], rows);
```

## Finished

```dataviewjs
const fmt = (d) => d ? dv.date(d).toFormat("yyyy-MM-dd") : "";
const pages = dv.pages('"Books"').where(p => p.file.name === "00_meta" && p.status === "finished").sort(p => p.finished, "desc");
const rows = pages.map(p => {
  const mapFile = dv.page(p.file.folder + "/00_map");
  const link = mapFile ? dv.fileLink(mapFile.file.path, false, p.title) : p.file.link;
  return [link, p.author, fmt(p.started), fmt(p.finished)];
});
if (rows.length > 0) dv.table(["Book", "Author", "Started", "Finished"], rows);
else dv.paragraph("*No finished books yet.*");
```

---

## WeRead Library

```dataviewjs
const pages = dv.pages('"WeRead"')
  .where(p => p.author && p.doc_type === "weread-highlights-reviews")
  .sort(p => p.lastReadDate, "desc");

// Status badge
const badge = (status, progress) => {
  if (status === "读完" || progress === "100%") return `<span style="background:#d3f9d8;color:#2b8a3e;padding:2px 8px;border-radius:10px;font-size:0.75em">✅ 已读</span>`;
  if (status === "在读" || (progress && progress !== "0%")) return `<span style="background:#d0ebff;color:#1864ab;padding:2px 8px;border-radius:10px;font-size:0.75em">📖 在读</span>`;
  return `<span style="background:#f3f0ff;color:#7048e8;padding:2px 8px;border-radius:10px;font-size:0.75em">💜 想读</span>`;
};

// Classify each page
const getStatus = (p) => {
  const s = p.readingStatus || "";
  const prog = p.progress || "0%";
  if (s === "读完" || prog === "100%") return "已读";
  if (s === "在读" || (prog && prog !== "0%" && prog !== "-1")) return "在读";
  return "想读";
};

const container = dv.el("div", "");
const btnBase = "padding:5px 14px;border:none;border-radius:6px;cursor:pointer;font-size:0.82em;transition:all 0.15s;";
const btnOff = btnBase + "background:transparent;color:var(--text-muted);";
const btnOn = btnBase + "background:var(--interactive-accent);color:var(--text-on-accent);font-weight:500;";

// Toolbar: filters left, sort right
const toolbar = container.createEl("div", {
  attr: { style: "display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:12px;" }
});

// Filter tabs (left)
let activeTab = "all";
const tabGroup = toolbar.createEl("div", {
  attr: { style: "display:flex;gap:2px;background:var(--background-secondary);border-radius:8px;padding:3px;" }
});
const tabs = [
  { label: "📋 全部", value: "all" },
  { label: "✅ 已读", value: "已读" },
  { label: "📖 在读", value: "在读" },
  { label: "💜 想读", value: "想读" },
];
const tabEls = tabs.map(t => {
  const btn = tabGroup.createEl("button", { text: t.label, attr: { style: btnOff } });
  btn.addEventListener("click", () => { activeTab = t.value; updateStyles(); render(); });
  return { el: btn, value: t.value };
});

// Sort toggle (right)
let activeSort = "time";
const sortGroup = toolbar.createEl("div", {
  attr: { style: "display:flex;gap:2px;background:var(--background-secondary);border-radius:8px;padding:3px;align-items:center;" }
});
sortGroup.createEl("span", { text: "排序", attr: { style: "font-size:0.8em;color:var(--text-faint);padding:0 6px;" } });
const sortOpts = [
  { label: "最近阅读", value: "time" },
  { label: "笔记数", value: "notes" },
];
const sortEls = sortOpts.map(s => {
  const btn = sortGroup.createEl("button", { text: s.label, attr: { style: btnOff } });
  btn.addEventListener("click", () => { activeSort = s.value; updateStyles(); render(); });
  return { el: btn, value: s.value };
});

function updateStyles() {
  tabEls.forEach(t => { t.el.setAttribute("style", t.value === activeTab ? btnOn : btnOff); });
  sortEls.forEach(s => { s.el.setAttribute("style", s.value === activeSort ? btnOn : btnOff); });
}
updateStyles();

// Search box
const searchBox = container.createEl("input", {
  attr: { type: "text", placeholder: "搜索书名或作者...", style: "width:100%;padding:8px 14px;margin-bottom:14px;border:1px solid var(--background-modifier-border);border-radius:8px;font-size:0.9em;background:var(--background-primary);color:var(--text-normal);outline:none;" }
});

const grid = container.createEl("div", "");

function render() {
  grid.empty();
  grid.setAttribute("style", "display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:16px;");

  const q = searchBox.value.toLowerCase();
  let filtered = pages;

  if (activeTab !== "all") {
    filtered = filtered.where(p => getStatus(p) === activeTab);
  }
  if (q) {
    filtered = filtered.where(p => {
      const title = p.file.name.replace(/-CB_.*$/, "").replace(/-\d+$/, "");
      return title.toLowerCase().includes(q) || (p.author && p.author.toLowerCase().includes(q));
    });
  }
  if (activeSort === "notes") {
    filtered = filtered.sort(p => (p.noteCount || 0) + (p.reviewCount || 0), "desc");
  }

  for (const p of filtered) {
    const title = p.file.name.replace(/-CB_.*$/, "").replace(/-\d+$/, "");
    const cover = p.cover || "";
    const status = getStatus(p);
    const progress = p.progress || "0%";
    const time = p.readingTime || "";

    const card = grid.createEl("div", {
      attr: { style: "border:1px solid var(--background-modifier-border);border-radius:12px;overflow:hidden;background:var(--background-secondary);cursor:pointer;transition:box-shadow 0.2s;box-shadow:0 1px 3px rgba(0,0,0,0.06);" }
    });

    if (cover) {
      card.createEl("img", {
        attr: { src: cover, style: "width:100%;height:160px;object-fit:cover;" }
      });
    }

    const body = card.createEl("div", { attr: { style: "padding:10px;" } });
    const titleEl = body.createEl("div", { attr: { style: "font-weight:600;font-size:0.9em;margin-bottom:4px;line-height:1.3;" } });
    titleEl.innerHTML = `<a class="internal-link" data-href="${p.file.path}">${title}</a>`;
    if (p.author) {
      body.createEl("div", { attr: { style: "font-size:0.75em;color:var(--text-muted);margin-bottom:6px;" }, text: p.author });
    }
    body.createEl("div", { attr: { style: "margin-bottom:6px;" }, text: "" }).innerHTML = badge(status, progress);
    const notes = (p.noteCount || 0) + (p.reviewCount || 0);
    const meta = [`${progress}`];
    if (notes > 0) meta.push(`📝 ${notes}`);
    body.createEl("div", { attr: { style: "font-size:0.8em;color:var(--text-muted);" }, text: meta.join(" · ") });
    if (time && time !== "0小时0分钟") {
      body.createEl("div", { attr: { style: "font-size:0.8em;color:var(--text-accent);margin-top:2px;" }, text: time });
    }
  }
}

searchBox.addEventListener("input", () => render());
render();
```

---
tags: [MOC]
cssclasses: [wide-page]
---

# Zettelkasten Index

```dataviewjs
const allZk = dv.pages('"Zettelkasten"').where(p => p.file.name !== "Zettelkasten Index");
const inbox = dv.pages('"Inbox"').where(p => !p.file.path.includes("Inbox/archive"));
const btnBase = "padding:5px 14px;border:none;border-radius:6px;cursor:pointer;font-size:0.82em;transition:all 0.15s;";
const btnOff = btnBase + "background:transparent;color:var(--text-muted);";
const btnOn = btnBase + "background:var(--interactive-accent);color:var(--text-on-accent);font-weight:500;";
const topicPillOff = "padding:3px 10px;border-radius:14px;font-size:0.78em;cursor:pointer;background:var(--background-primary);color:var(--text-muted);border:1px solid var(--background-modifier-border);transition:all 0.15s;white-space:nowrap;";
const topicPillOn = "padding:3px 10px;border-radius:14px;font-size:0.78em;cursor:pointer;background:var(--interactive-accent);color:var(--text-on-accent);border:1px solid transparent;font-weight:500;white-space:nowrap;";

const container = dv.el("div", "");

// Stats bar
let totalLinks = 0;
try { totalLinks = allZk.array().reduce((sum, p) => sum + p.file.outlinks.length + p.file.inlinks.length, 0); } catch(e) {}
const statsBar = container.createEl("div", {
  attr: { style: "display:flex;gap:20px;flex-wrap:wrap;margin-bottom:16px;padding:12px 16px;background:var(--background-secondary);border-radius:10px;" }
});
const statItems = [
  [`${allZk.length}`, "Zettel"],
  [`${inbox.length}`, "Inbox"],
  [`${totalLinks}`, "Links"],
  [`${new Set(allZk.where(p => p.source).map(p => String(p.source).replace(/\[\[|\]\]/g, ""))).size}`, "Sources"],
];
for (const [num, label] of statItems) {
  const s = statsBar.createEl("div", { attr: { style: "text-align:center;" } });
  s.createEl("div", { text: num, attr: { style: "font-size:1.4em;font-weight:700;line-height:1.2;" } });
  s.createEl("div", { text: label, attr: { style: "font-size:0.75em;color:var(--text-muted);" } });
}

// Compute top topics by frequency
const topicCounts = {};
for (const p of allZk) {
  for (const t of (p.topics || [])) {
    const ts = String(t);
    topicCounts[ts] = (topicCounts[ts] || 0) + 1;
  }
}
const topTopics = Object.entries(topicCounts).sort((a, b) => b[1] - a[1]).slice(0, 12).map(e => e[0]);

// Row 1: Search + Sort
const searchRow = container.createEl("div", {
  attr: { style: "display:flex;gap:10px;align-items:center;margin-bottom:12px;" }
});
const searchBox = searchRow.createEl("input", {
  attr: { type: "text", placeholder: "Search zettel...", style: "flex:1;min-width:0;padding:8px 14px;border:1px solid var(--background-modifier-border);border-radius:8px;font-size:0.88em;background:var(--background-primary);color:var(--text-normal);outline:none;" }
});
let activeSort = "recent";
const sortGroup = searchRow.createEl("div", {
  attr: { style: "display:flex;gap:2px;background:var(--background-secondary);border-radius:8px;padding:3px;align-items:center;flex-shrink:0;" }
});
const sortOpts = [
  { label: "Recent", value: "recent" },
  { label: "Links", value: "links" },
  { label: "Source", value: "source" },
];
const sortEls = sortOpts.map(s => {
  const btn = sortGroup.createEl("button", { text: s.label, attr: { style: btnOff } });
  btn.addEventListener("click", () => { activeSort = s.value; updateSortStyles(); render(); });
  return { el: btn, value: s.value };
});
function updateSortStyles() {
  sortEls.forEach(s => { s.el.setAttribute("style", s.value === activeSort ? btnOn : btnOff); });
}
updateSortStyles();

// Row 1b: Status filter
let activeStatus = null;
const statusRow = container.createEl("div", {
  attr: { style: "display:flex;gap:6px;align-items:center;margin-bottom:10px;" }
});
statusRow.createEl("span", { text: "Status:", attr: { style: "font-size:0.78em;color:var(--text-faint);flex-shrink:0;" } });
const statusOpts = [
  { label: "All", value: null },
  { label: "\ud83c\udf31 Seedling", value: "seedling" },
  { label: "\ud83c\udf3f Growing", value: "growing" },
  { label: "\ud83c\udf33 Evergreen", value: "evergreen" },
];
const statusEls = statusOpts.map(s => {
  const btn = statusRow.createEl("button", { text: s.label, attr: { style: s.value === activeStatus ? btnOn : btnOff } });
  btn.addEventListener("click", () => { activeStatus = s.value; updateStatusStyles(); render(); });
  return { el: btn, value: s.value };
});
function updateStatusStyles() {
  statusEls.forEach(s => { s.el.setAttribute("style", s.value === activeStatus ? btnOn : btnOff); });
}

// Row 2: Popular topics — clean horizontal bar
const topicBar = container.createEl("div", {
  attr: { style: "display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;" }
});
const topicBarEls = [];
for (const t of topTopics) {
  const pill = topicBar.createEl("span", { text: `${t} ${topicCounts[t]}`, attr: { style: topicPillOff } });
  pill.addEventListener("click", () => { addTopicFilter(t); updateTopicBar(); });
  topicBarEls.push({ el: pill, topic: t });
}
function updateTopicBar() {
  topicBarEls.forEach(te => {
    te.el.setAttribute("style", activeTopics.has(te.topic) ? topicPillOn : topicPillOff);
  });
}

// Row 3: Active filter chips (only visible when filtering)
const activeTopics = new Set();
const activeChipsRow = container.createEl("div", { attr: { style: "display:flex;gap:6px;flex-wrap:wrap;min-height:0;" } });

function renderActiveChips() {
  activeChipsRow.empty();
  if (activeTopics.size === 0) {
    activeChipsRow.style.marginBottom = "0";
    return;
  }
  activeChipsRow.style.marginBottom = "12px";
  activeChipsRow.createEl("span", { text: "Filter:", attr: { style: "font-size:0.78em;color:var(--text-faint);line-height:1.8;" } });
  for (const t of activeTopics) {
    const chip = activeChipsRow.createEl("span", {
      attr: { style: "display:inline-flex;align-items:center;gap:4px;font-size:0.78em;padding:3px 10px;border-radius:14px;background:var(--interactive-accent);color:var(--text-on-accent);cursor:pointer;font-weight:500;" }
    });
    chip.createEl("span", { text: t });
    chip.createEl("span", { text: "\u00d7", attr: { style: "font-size:1.1em;line-height:1;" } });
    chip.addEventListener("click", () => { activeTopics.delete(t); renderActiveChips(); updateTopicBar(); render(); });
  }
}

function addTopicFilter(t) {
  const topic = String(t);
  if (activeTopics.has(topic)) {
    activeTopics.delete(topic);
  } else {
    activeTopics.add(topic);
  }
  renderActiveChips();
  render();
}

const list = container.createEl("div", "");

function render() {
  list.empty();

  const q = searchBox.value.toLowerCase();
  let filtered = allZk;

  // Status filter
  if (activeStatus) {
    filtered = filtered.where(p => p.status === activeStatus);
  }

  // Topic filter: must match ALL active topics
  if (activeTopics.size > 0) {
    filtered = filtered.where(p => {
      const pt = (p.topics || []).map(x => String(x));
      return [...activeTopics].every(t => pt.includes(t));
    });
  }
  if (q) {
    filtered = filtered.where(p => {
      const title = p.file.name.toLowerCase();
      const src = String(p.source || "").toLowerCase();
      const tp = (p.topics || []).join(" ").toLowerCase();
      return title.includes(q) || src.includes(q) || tp.includes(q);
    });
  }

  // Sort
  if (activeSort === "recent") {
    filtered = filtered.sort(p => p.file.ctime, "desc");
  } else if (activeSort === "links") {
    filtered = filtered.sort(p => p.file.outlinks.length + p.file.inlinks.length, "desc");
  } else if (activeSort === "source") {
    filtered = filtered.sort(p => String(p.source || "zzz"), "asc");
  }

  const statusIcon = { seedling: "\ud83c\udf31", growing: "\ud83c\udf3f", evergreen: "\ud83c\udf33" };

  // Render cards
  const grid = list.createEl("div", {
    attr: { style: "display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;" }
  });

  for (const p of filtered) {
    const linkCount = p.file.outlinks.length + p.file.inlinks.length;
    const src = String(p.source || "").replace(/\[\[|\]\]/g, "").replace(/-\d+$/, "").replace(/-CB_.*$/, "");

    const card = grid.createEl("div", {
      attr: { style: "border:1px solid var(--background-modifier-border);border-radius:12px;padding:14px 16px;background:var(--background-secondary);transition:box-shadow 0.2s;box-shadow:0 1px 3px rgba(0,0,0,0.06);display:flex;flex-direction:column;" }
    });

    // Title — hero element
    const titleEl = card.createEl("div", { attr: { style: "font-weight:700;font-size:0.95em;margin-bottom:8px;line-height:1.4;" } });
    titleEl.innerHTML = `<a class="internal-link" data-href="${p.file.path}">${p.file.name}</a>`;

    // Topics — inline, compact
    const topics = p.topics || [];
    if (topics.length > 0) {
      const topicRow = card.createEl("div", { attr: { style: "margin-bottom:10px;display:flex;gap:4px;flex-wrap:wrap;" } });
      for (const t of topics) {
        const isActive = activeTopics.has(String(t));
        const chip = topicRow.createEl("span", { text: String(t), attr: { style: isActive ? "font-size:0.7em;padding:1px 7px;border-radius:8px;background:var(--interactive-accent);color:var(--text-on-accent);border:1px solid transparent;cursor:pointer;transition:all 0.15s;" : "font-size:0.7em;padding:1px 7px;border-radius:8px;background:var(--background-primary);color:var(--text-muted);border:1px solid var(--background-modifier-border);cursor:pointer;transition:all 0.15s;" } });
        chip.addEventListener("click", (e) => { e.stopPropagation(); addTopicFilter(t); updateTopicBar(); });
      }
    }

    // Bottom: two rows — source on top, meta on bottom (pushed to card bottom)
    const cardBottom = card.createEl("div", { attr: { style: "margin-top:auto;padding-top:10px;font-size:0.73em;color:var(--text-faint);" } });

    // Row 1: source
    if (src) {
      const srcRow = cardBottom.createEl("div", { attr: { style: "margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" } });
      const si = statusIcon[p.status] || "";
      if (si) srcRow.createEl("span", { text: si + " ", attr: { style: "font-size:1.1em;" } });
      const srcEl = srcRow.createEl("span");
      srcEl.innerHTML = `<a class="internal-link" data-href="${String(p.source || "").replace(/\[\[|\]\]/g, "")}" style="color:var(--text-faint);">${src}</a>`;
    }

    // Row 2: link count + date + evergreen button
    const metaRow = cardBottom.createEl("div", { attr: { style: "display:flex;align-items:center;gap:6px;" } });
    if (!src) {
      const si = statusIcon[p.status] || "";
      if (si) metaRow.createEl("span", { text: si, attr: { style: "font-size:1.1em;" } });
    }
    if (linkCount > 0) {
      metaRow.createEl("span", { text: `\u00b7 ${linkCount} links` });
    }

    // Right-aligned group: date + evergreen button
    const metaRight = metaRow.createEl("div", { attr: { style: "display:flex;align-items:center;gap:8px;margin-left:auto;" } });
    const created = p.created ? String(p.created).slice(0, 10) : "";
    if (created) {
      metaRight.createEl("span", { text: created });
    }

    // Evergreen promote button — only shown on growing notes
    if (p.status === "growing") {
      const evBtn = metaRight.createEl("button", {
        text: "\ud83c\udf33 Evergreen",
        attr: {
          title: "Mark as evergreen",
          style: "border:1px solid var(--color-green);border-radius:6px;background:none;color:var(--color-green);cursor:pointer;font-size:0.8em;padding:3px 10px;opacity:0.5;transition:opacity 0.15s;flex-shrink:0;"
        }
      });
      evBtn.addEventListener("mouseenter", () => { evBtn.style.opacity = "1"; });
      evBtn.addEventListener("mouseleave", () => { evBtn.style.opacity = "0.5"; });
      evBtn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const tFile = app.vault.getAbstractFileByPath(p.file.path);
        if (!tFile) return;
        await app.fileManager.processFrontMatter(tFile, fm => { fm.status = "evergreen"; });
        evBtn.style.opacity = "1";
        evBtn.style.cursor = "default";
        evBtn.title = "Marked as evergreen \u2713";
        card.style.borderColor = "var(--color-green)";
      });
    }
  }

  // Empty state
  if (filtered.length === 0) {
    list.createEl("div", { text: "No zettel found.", attr: { style: "color:var(--text-muted);padding:20px;text-align:center;" } });
  }
}

searchBox.addEventListener("input", () => render());
render();
```

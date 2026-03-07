---
tags: [MOC]
cssclasses: [wide-page]
---

# Zettelkasten Index

```dataviewjs
const allZk = dv.pages('"Zettelkasten"').where(p => p.file.name !== "Zettelkasten Index");
const inbox = dv.pages('"Inbox"');
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
      attr: { style: "border:1px solid var(--background-modifier-border);border-radius:12px;padding:14px 16px;background:var(--background-secondary);transition:box-shadow 0.2s;box-shadow:0 1px 3px rgba(0,0,0,0.06);" }
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

    // Bottom row: status + source (truncated) + links + date
    const bottom = card.createEl("div", {
      attr: { style: "display:flex;align-items:center;gap:6px;font-size:0.73em;color:var(--text-faint);" }
    });
    const si = statusIcon[p.status] || "";
    if (si) bottom.createEl("span", { text: si, attr: { style: "font-size:1.1em;flex-shrink:0;" } });
    if (src) {
      const srcEl = bottom.createEl("span", { attr: { style: "overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0;" } });
      srcEl.innerHTML = `<a class="internal-link" data-href="${String(p.source || "").replace(/\[\[|\]\]/g, "")}" style="color:var(--text-faint);">${src}</a>`;
    }
    if (linkCount > 0) {
      bottom.createEl("span", { text: `\u00b7 ${linkCount}`, attr: { style: "flex-shrink:0;" } });
    }
    const created = p.created ? String(p.created).slice(0, 10) : "";
    if (created) {
      bottom.createEl("span", { text: created, attr: { style: "margin-left:auto;flex-shrink:0;" } });
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

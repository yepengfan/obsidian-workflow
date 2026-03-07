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

const container = dv.el("div", "");

// Stats bar
const totalLinks = allZk.array().reduce((sum, p) => sum + p.file.outlinks.length + p.file.inlinks.length, 0);
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

// Toolbar: domain filter left, sort right
const toolbar = container.createEl("div", {
  attr: { style: "display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:12px;" }
});

// Domain filter (left)
let activeDomain = "all";
const domainGroup = toolbar.createEl("div", {
  attr: { style: "display:flex;gap:2px;background:var(--background-secondary);border-radius:8px;padding:3px;" }
});
const domains = [
  { label: "All", value: "all" },
  { label: "Reading", value: "reading" },
  { label: "Work", value: "work" },
  { label: "Skill", value: "skill" },
  { label: "Meta", value: "meta" },
];
const domainEls = domains.map(d => {
  const btn = domainGroup.createEl("button", { text: d.label, attr: { style: btnOff } });
  btn.addEventListener("click", () => { activeDomain = d.value; updateStyles(); render(); });
  return { el: btn, value: d.value };
});

// Sort toggle (right)
let activeSort = "recent";
const sortGroup = toolbar.createEl("div", {
  attr: { style: "display:flex;gap:2px;background:var(--background-secondary);border-radius:8px;padding:3px;align-items:center;" }
});
sortGroup.createEl("span", { text: "Sort", attr: { style: "font-size:0.8em;color:var(--text-faint);padding:0 6px;" } });
const sortOpts = [
  { label: "Recent", value: "recent" },
  { label: "Links", value: "links" },
  { label: "Source", value: "source" },
];
const sortEls = sortOpts.map(s => {
  const btn = sortGroup.createEl("button", { text: s.label, attr: { style: btnOff } });
  btn.addEventListener("click", () => { activeSort = s.value; updateStyles(); render(); });
  return { el: btn, value: s.value };
});

function updateStyles() {
  domainEls.forEach(d => { d.el.setAttribute("style", d.value === activeDomain ? btnOn : btnOff); });
  sortEls.forEach(s => { s.el.setAttribute("style", s.value === activeSort ? btnOn : btnOff); });
}
updateStyles();

// Search + topic filter
const activeTopics = new Set();
const filterArea = container.createEl("div", { attr: { style: "margin-bottom:14px;" } });
const topicChipsRow = filterArea.createEl("div", { attr: { style: "display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;min-height:0;" } });
const searchBox = filterArea.createEl("input", {
  attr: { type: "text", placeholder: "Search zettel by title or source...", style: "width:100%;padding:8px 14px;border:1px solid var(--background-modifier-border);border-radius:8px;font-size:0.9em;background:var(--background-primary);color:var(--text-normal);outline:none;" }
});

function renderTopicChips() {
  topicChipsRow.empty();
  if (activeTopics.size === 0) {
    topicChipsRow.style.marginBottom = "0";
    return;
  }
  topicChipsRow.style.marginBottom = "8px";
  for (const t of activeTopics) {
    const chip = topicChipsRow.createEl("span", {
      attr: { style: "display:inline-flex;align-items:center;gap:4px;font-size:0.8em;padding:3px 10px;border-radius:14px;background:var(--interactive-accent);color:var(--text-on-accent);cursor:pointer;font-weight:500;" }
    });
    chip.createEl("span", { text: t });
    chip.createEl("span", { text: "×", attr: { style: "font-size:1.1em;line-height:1;" } });
    chip.addEventListener("click", () => { activeTopics.delete(t); renderTopicChips(); render(); });
  }
}

function addTopicFilter(t) {
  const topic = String(t);
  if (activeTopics.has(topic)) {
    activeTopics.delete(topic);
  } else {
    activeTopics.add(topic);
  }
  renderTopicChips();
  render();
}

const list = container.createEl("div", "");

function render() {
  list.empty();

  const q = searchBox.value.toLowerCase();
  let filtered = allZk;

  if (activeDomain !== "all") {
    filtered = filtered.where(p => (p.domain || "") === activeDomain);
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

  // Badges
  const badge = (text, style) => `<span style="${style};padding:2px 8px;border-radius:10px;font-size:0.72em;font-weight:500;">${text}</span>`;
  const domainBadge = (d) => {
    const colors = {
      reading: "background:#d0ebff;color:#1864ab",
      work: "background:#fff3bf;color:#e67700",
      skill: "background:#d3f9d8;color:#2b8a3e",
      meta: "background:#f3f0ff;color:#7048e8",
    };
    return badge(d || "—", colors[d] || "background:var(--background-secondary);color:var(--text-muted)");
  };
  const statusBadge = (s) => {
    const icons = { seedling: "🌱", growing: "🌿", evergreen: "🌳" };
    return icons[s] || "";
  };

  // Render cards
  const grid = list.createEl("div", {
    attr: { style: "display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;" }
  });

  for (const p of filtered) {
    const linkCount = p.file.outlinks.length + p.file.inlinks.length;
    const src = String(p.source || "").replace(/\[\[|\]\]/g, "");

    const card = grid.createEl("div", {
      attr: { style: "border:1px solid var(--background-modifier-border);border-radius:12px;padding:14px;background:var(--background-secondary);cursor:pointer;transition:box-shadow 0.2s;box-shadow:0 1px 3px rgba(0,0,0,0.06);" }
    });

    // Title
    const titleEl = card.createEl("div", { attr: { style: "font-weight:600;font-size:0.92em;margin-bottom:6px;line-height:1.3;" } });
    titleEl.innerHTML = `<a class="internal-link" data-href="${p.file.path}">${p.file.name}</a>`;

    // Source
    if (src) {
      const srcEl = card.createEl("div", { attr: { style: "font-size:0.78em;color:var(--text-muted);margin-bottom:6px;" } });
      srcEl.innerHTML = `<a class="internal-link" data-href="${src}">${src}</a>`;
    }

    // Topics
    const topics = p.topics || [];
    if (topics.length > 0) {
      const topicRow = card.createEl("div", { attr: { style: "margin-bottom:8px;display:flex;gap:4px;flex-wrap:wrap;" } });
      for (const t of topics) {
        const chip = topicRow.createEl("span", { text: String(t), attr: { style: "font-size:0.7em;padding:1px 7px;border-radius:8px;background:var(--background-primary);color:var(--text-muted);border:1px solid var(--background-modifier-border);cursor:pointer;transition:all 0.15s;" } });
        chip.addEventListener("click", (e) => { e.stopPropagation(); addTopicFilter(t); });
      }
    }

    // Bottom row: status + domain badge + link count + date
    const bottom = card.createEl("div", {
      attr: { style: "display:flex;align-items:center;gap:8px;flex-wrap:wrap;" }
    });
    const si = statusBadge(p.status);
    if (si) bottom.createEl("span", { text: si, attr: { style: "font-size:0.85em;" } });
    bottom.createEl("span", { attr: { style: "" } }).innerHTML = domainBadge(p.domain);
    if (linkCount > 0) {
      bottom.createEl("span", { text: `${linkCount} links`, attr: { style: "font-size:0.75em;color:var(--text-muted);" } });
    }
    const created = p.created ? String(p.created).slice(0, 10) : "";
    if (created) {
      bottom.createEl("span", { text: created, attr: { style: "font-size:0.75em;color:var(--text-faint);margin-left:auto;" } });
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

const ICONS = {
  review:
    '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10a9 9 0 1 1 2.4 8.6M3 4v6h6"/><path d="m9 12 2 2 4-4"/></svg>',
  task: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M12 3v18M3 12h18"/></svg>',
  journal:
    '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3h12a2 2 0 0 1 2 2v16H6a2 2 0 0 1-2-2V5a2 2 0 0 1 1-2Z"/><path d="M8 7h7M8 11h7M8 15h4"/></svg>',
  learning:
    '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="m2 9 10-5 10 5-10 5-10-5ZM6 11v6c4 3 8 3 12 0v-6M22 9v7"/></svg>',
  books:
    '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5c-3-2-7-2-10-1v15c3-1 7-1 10 1 3-2 7-2 10-1V4c-3-1-7-1-10 1Zm0 0v15"/></svg>',
  algo: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="m8 5-6 7 6 7M16 5l6 7-6 7M14 3l-4 18"/></svg>',
  sysd: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="2" width="8" height="6" rx="1"/><rect x="1" y="16" width="8" height="6" rx="1"/><rect x="15" y="16" width="8" height="6" rx="1"/><path d="M12 8v4M5 16v-4h14v4"/></svg>',
  frontend:
    '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="18" rx="2"/><path d="M2 8h20M8 8v13M5 5.5h.1M8 5.5h.1M11 5.5h.1"/></svg>',
  zettel:
    '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="3"/><circle cx="5" cy="18" r="3"/><circle cx="19" cy="18" r="3"/><path d="m10 8-4 7M14 8l4 7M8 18h8"/></svg>',
  articles:
    '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="2" width="18" height="20" rx="2"/><path d="M7 6h10M7 10h5M7 14h10M7 18h10"/></svg>',
  essays:
    '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="m16 3 5 5L9 20l-6 1 1-6L16 3ZM13 6l5 5"/></svg>',
  work: '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M8 7V3h8v4M2 12c6 4 14 4 20 0M10 13h4v4h-4z"/></svg>',
  brownbag:
    '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3h18v13H3zM12 16v6M7 22h10M7 12V9M12 12V6M17 12V8"/></svg>',
  profile:
    '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="7" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3"/></svg>',
};
// Shared, scoped presentation primitives for Dataview module dashboards.
const app = input.app;
const root = dv.el("main", "", { cls: "mdash" });
const el = (parent, tag, text, cls) => parent.createEl(tag, { text, cls });
function link(parent, path, label) {
  const anchor = parent.createEl("a", {
    text: label,
    cls: "internal-link",
    attr: { href: path, "data-href": path },
  });
  anchor.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    void app.workspace.openLinkText(path, "", event.metaKey || event.ctrlKey);
  });
  return anchor;
}
function button(parent, label, action) {
  const node = parent.createEl("button", {
    text: label,
    attr: { type: "button" },
  });
  node.addEventListener("click", action);
  return node;
}
const nav = el(root, "nav", "", "mdash-nav");
nav.setAttribute("aria-label", "Dashboard navigation");
if (input.title !== "Home") link(nav, "Home.md", "← Home");
for (const [label, path] of input.links || []) link(nav, path, label);
const heading = el(root, "header", "", "mdash-header");
const aliases = {
  Algorithm: "algo",
  "System Design": "sysd",
  Frontend: "frontend",
  Learning: "learning",
  Books: "books",
  Articles: "articles",
  Essays: "essays",
  Brownbag: "brownbag",
  Work: "work",
  Profile: "profile",
  Journal: "journal",
  Zettelkasten: "zettel",
  "Task Board": "task",
  "Practice Review": "review",
};
const glyph = el(heading, "span", "", "mdash-icon");
glyph.setAttribute("aria-hidden", "true");
if (ICONS[aliases[input.title]]) glyph.innerHTML = ICONS[aliases[input.title]];
else glyph.textContent = "⌂";
const title = el(heading, "div", "", "mdash-title");
el(title, "h1", input.title);
if (input.description) el(title, "p", input.description, "mdash-muted");
const actions = el(root, "div", "", "mdash-actions");
function command(text, label = `Copy ${text}`) {
  const node = button(actions, label, async () => {
    try {
      await navigator.clipboard.writeText(text);
      feedback.textContent = `Copied ${text}. Paste it into your agent chat.`;
    } catch {
      feedback.textContent = `Copy this command into your agent chat: ${text}`;
    }
  });
  node.title = `Copies ${text}; run it in your agent chat`;
  return node;
}
const feedback = el(root, "p", "", "mdash-feedback");
feedback.setAttribute("role", "status");
const content = el(root, "div", "", "mdash-content");
function metrics(items) {
  const row = el(content, "section", "", "mdash-metrics");
  row.setAttribute("aria-label", "Overview");
  row.style.setProperty("--metric-count", String(items.length));
  for (const [value, label, caption] of items) {
    const card = el(row, "div", "", "mdash-metric");
    el(card, "span", label, "mdash-muted");
    el(card, "strong", String(value));
    if (caption) el(card, "small", caption, "mdash-muted");
  }
}
function section(label, caption) {
  const panel = el(content, "section", "", "mdash-section");
  el(panel, "h2", label);
  if (caption) el(panel, "p", caption, "mdash-muted");
  return panel;
}
function bars(parent, values, caption, scaleMax) {
  const chart = el(parent, "div", "", "mdash-bars");
  chart.setAttribute("role", "img");
  chart.setAttribute(
    "aria-label",
    `${caption}: ${values.map((x) => `${x[0]} ${x[1]}`).join(", ")}`,
  );
  const max = scaleMax || Math.max(1, ...values.map((x) => x[1]));
  for (const [name, value] of values) {
    const row = el(chart, "div", "", "mdash-bar-row");
    el(row, "span", name);
    const track = el(row, "div", "", "mdash-track");
    const fill = el(track, "div", "", "mdash-fill");
    fill.style.width = `${(Math.max(0, value) / max) * 100}%`;
    el(row, "strong", String(value));
  }
  if (!values.length)
    el(chart, "p", "No activity recorded yet.", "mdash-empty");
}
function trend(parent, values, caption) {
  const scroll = el(parent, "div", "", "mdash-trend-scroll");
  const chart = el(scroll, "div", "", "mdash-trend");
  chart.setAttribute("role", "img");
  chart.setAttribute(
    "aria-label",
    `${caption}: ${values.map((x) => `${x[0]} ${x[1]}`).join(", ")}`,
  );
  chart.style.setProperty("--trend-count", String(values.length));
  const max = Math.max(1, ...values.map((x) => x[1]));
  for (const [name, value] of values) {
    const column = el(chart, "div", "", "mdash-trend-column");
    el(column, "strong", String(value));
    const track = el(column, "div", "", "mdash-trend-track");
    el(track, "div", "", "mdash-trend-fill").style.height =
      `${(Math.max(0, value) / max) * 100}%`;
    el(column, "small", name);
  }
}
function browser(
  parent,
  {
    rows,
    columns,
    filters = [],
    initial = {},
    sort,
    placeholder = "Search titles and metadata…",
    empty = "No items yet.",
    renderCard,
  },
) {
  const wrap = el(parent, "div", "", "mdash-browser");
  const controls = el(wrap, "div", "", "mdash-controls");
  const search = controls.createEl("input", {
    attr: { type: "search", placeholder, "aria-label": placeholder },
  });
  const selectors = filters.map((filter) => {
    const select = controls.createEl("select", {
      attr: { "aria-label": filter.label },
    });
    for (const [value, label] of filter.options)
      select.createEl("option", { text: label, attr: { value } });
    select.value = initial[filter.key] || "";
    return { filter, select };
  });
  const reset = button(controls, "Reset", () => {
    search.value = "";
    selectors.forEach(({ select }) => {
      select.value = "";
    });
    page = 0;
    render();
  });
  const summary = el(wrap, "p", "", "mdash-muted mdash-result-count");
  summary.setAttribute("role", "status");
  const results = el(
    wrap,
    "div",
    "",
    renderCard ? "mdash-cards" : "mdash-table-scroll",
  );
  const pager = el(wrap, "nav", "", "mdash-pager");
  pager.setAttribute("aria-label", "Results pages");
  let page = 0;
  const pageSize = 20;
  function render() {
    const query = search.value.trim().toLocaleLowerCase();
    const filtered = rows.filter(
      (row) =>
        (!query ||
          String(row.search || "")
            .toLocaleLowerCase()
            .includes(query)) &&
        selectors.every(
          ({ filter, select }) =>
            !select.value || filter.match(row, select.value),
        ),
    );
    if (sort) filtered.sort(sort);
    page = Math.min(
      page,
      Math.max(0, Math.ceil(filtered.length / pageSize) - 1),
    );
    results.empty();
    pager.empty();
    const active = !!query || selectors.some(({ select }) => select.value);
    reset.disabled = !active;
    const start = page * pageSize;
    const subset = filtered.slice(start, start + pageSize);
    summary.textContent = filtered.length
      ? `${start + 1}-${start + subset.length} of ${filtered.length}${active ? ` matches (${rows.length} total)` : " items"}`
      : `0${active ? ` matches (${rows.length} total)` : " items"}`;
    if (!subset.length) {
      el(
        results,
        "p",
        active ? "No matches. Change your search or reset the filters." : empty,
        "mdash-empty",
      );
    } else if (renderCard) {
      for (const row of subset)
        renderCard(el(results, "article", "", "mdash-card"), row);
    } else {
      const table = el(results, "table", "", "mdash-table");
      const head = el(el(table, "thead"), "tr");
      for (const column of columns)
        head.createEl("th", { text: column.label, attr: { scope: "col" } });
      const body = el(table, "tbody");
      for (const row of subset) {
        const tr = el(body, "tr");
        for (const column of columns) {
          const cell = el(tr, "td");
          if (column.render) column.render(cell, row);
          else cell.textContent = String(row[column.key] ?? "-");
          if (/^\d{4}-\d{2}-\d{2}$/.test(cell.textContent))
            cell.classList.add("mdash-date");
        }
      }
    }
    if (filtered.length > pageSize) {
      button(pager, "Previous", () => {
        page--;
        render();
      }).disabled = page === 0;
      el(
        pager,
        "span",
        `${page + 1} / ${Math.ceil(filtered.length / pageSize)}`,
      );
      button(pager, "Next", () => {
        page++;
        render();
      }).disabled = start + pageSize >= filtered.length;
    }
  }
  search.addEventListener("input", () => {
    page = 0;
    render();
  });
  selectors.forEach(({ select }) =>
    select.addEventListener("change", () => {
      page = 0;
      render();
    }),
  );
  render();
  return wrap;
}
input.ui = {
  icons: ICONS,
  root,
  content,
  actions,
  el,
  link,
  button,
  command,
  metrics,
  section,
  bars,
  trend,
  browser,
};

const DOMAIN_LABELS = {
  algorithm: "Algorithm",
  "system-design": "System Design",
  behavioral: "Behavioral Interview",
};
const OUTCOME_LABELS = {
  independent: "Independent",
  assisted: "With help",
  incomplete: "Incomplete",
};
const ICONS = {
  review:
    '<path d="M3 10a9 9 0 1 1 2.4 8.6M3 4v6h6"/><path d="m9 12 2 2 4-4"/>',
  due: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 2v6M17 2v6M3 11h18m-13 5 2 2 4-4"/>',
  overdue: '<circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 17h.01"/>',
  upcoming: '<path d="M4 4h16v16H4zM4 9h16M8 2v5M16 2v5m-6 8 3 3 4-5"/>',
  rounds: '<path d="M5 3h14v18H5zM8 7h8M8 11h8M8 15h5"/>',
};

function dateKey(value) {
  if (value?.isValid === false) return null;
  const raw =
    value?.toISODate?.() ??
    (value instanceof Date
      ? `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}-${String(value.getDate()).padStart(2, "0")}`
      : value);
  if (typeof raw !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(raw)) return null;
  const parsed = new Date(`${raw}T12:00:00Z`);
  return Number.isFinite(+parsed) && parsed.toISOString().slice(0, 10) === raw
    ? raw
    : null;
}
function shiftDay(day, offset) {
  const d = new Date(`${day}T12:00:00Z`);
  d.setUTCDate(d.getUTCDate() + offset);
  return d.toISOString().slice(0, 10);
}
function byDue(a, b) {
  return (
    (a.nextReview ?? "9999-99-99").localeCompare(
      b.nextReview ?? "9999-99-99",
    ) ||
    a.id.localeCompare(b.id) ||
    a.path.localeCompare(b.path)
  );
}
function designProgress(page, history, intervals) {
  if (page.domain !== "system-design") return {};
  if (Number.isInteger(page.completed_design_rounds))
    return { completed: page.completed_design_rounds };
  const entries = [...(history ?? "").matchAll(/^### (\d{4}-\d{2}-\d{2}) · (?:Round (\d+)|第 (\d+) 轮)\s*\n\*\*(independent|assisted|incomplete|独立完成|提示后完成|未完成)\*\* · /gmu)];
  if (entries.length !== page.review_count || entries.some((m, i) => Number(m[2] ?? m[3]) !== i + 1))
    return {};
  const full = entries.filter(m => !["incomplete", "未完成"].includes(m[4]));
  const completed = full.length;
  const last = full.at(-1);
  if (page.status === "active" && last && last === entries.at(-1) && completed <= 2 && last[1] === dateKey(page.last_review)) {
    const stage = Math.min(completed - 1, intervals.length - 1);
    return { completed, stage, nextReview: shiftDay(last[1], intervals[stage]) };
  }
  return { completed };
}
function buildSnapshot(pages, today, intervals, histories = new Map()) {
  const items = [];
  for (const page of pages) {
    if (!["active", "archived"].includes(page.status)) continue;
    const progress = designProgress(page, histories.get(page.file.path), intervals);
    const issues = [];
    const id = typeof page.id === "string" ? page.id : page.file.name;
    if (page.id !== page.file.name) issues.push("ID must match the filename");
    const rounds =
      Number.isInteger(page.review_count) && page.review_count >= 0
        ? page.review_count
        : null;
    if (rounds === null) issues.push("Invalid recorded round count");
    const stage =
      Number.isInteger(page.stage) &&
      page.stage >= 0 &&
      page.stage < intervals.length
        ? progress.stage ?? page.stage
        : null;
    if (stage === null) issues.push("Invalid scheduling stage");
    const nextReview =
      progress.nextReview ?? (page.next_review == null ? null : dateKey(page.next_review));
    if (page.next_review != null && !nextReview)
      issues.push("Invalid next review date");
    const lastReview =
      page.last_review == null ? null : dateKey(page.last_review);
    if (page.last_review != null && !lastReview)
      issues.push("Invalid last review date");
    const domain =
      typeof page.domain === "string" && page.domain.trim()
        ? page.domain
        : "unknown";
    if (domain === "unknown") issues.push("Missing domain");
    const bucket =
      page.status === "archived"
        ? "archived"
        : issues.length
          ? "attention"
          : nextReview == null
            ? "unstarted"
            : nextReview < today
              ? "overdue"
              : nextReview === today
                ? "today"
                : "upcoming";
    items.push({
      id,
      title: String(page.title || id),
      domain,
      path: page.file.path,
      status: page.status,
      rounds,
      completed: progress.completed,
      stage,
      nextReview,
      lastReview,
      outcome: page.last_outcome,
      bucket,
      issues,
    });
  }
  items.sort(byDue);
  const active = items.filter((p) => p.status === "active");
  const counts = Object.fromEntries(
    ["overdue", "today", "upcoming", "unstarted", "archived", "attention"].map(
      (k) => [k, items.filter((p) => p.bucket === k).length],
    ),
  );
  counts.rounds = items.reduce((n, p) => n + (p.rounds ?? 0), 0);
  counts.active = active.length;
  counts.nextSeven = active.filter(
    (p) => p.bucket === "upcoming" && p.nextReview <= shiftDay(today, 7),
  ).length;
  const schedule = Array.from({ length: 7 }, (_, i) => {
    const day = shiftDay(today, i + 1);
    return {
      day,
      count: active.filter(
        (p) => p.bucket === "upcoming" && p.nextReview === day,
      ).length,
    };
  });
  const stages = intervals.map((days, index) => ({
    days,
    count: active.filter(
      (p) => p.stage === index && p.rounds > 0 && p.issues.length === 0,
    ).length,
  }));
  return { items, counts, schedule, stages, today };
}
function selectItems(
  snapshot,
  { domain = "all", status = "all", search = "", day = null } = {},
) {
  const q = search.trim().toLocaleLowerCase();
  return snapshot.items.filter((item) => {
    const statusMatches =
      status === "all" ||
      (status === "due"
        ? ["overdue", "today"].includes(item.bucket)
        : item.bucket === status);
    return (
      (domain === "all" || item.domain === domain) &&
      statusMatches &&
      (!day || item.nextReview === day) &&
      (!q ||
        `${item.id} ${item.title} ${DOMAIN_LABELS[item.domain] ?? item.domain}`
          .toLocaleLowerCase()
          .includes(q))
    );
  });
}

function renderDashboard(
  dv,
  app,
  {
    now = () => new Date(),
    page = globalThis.document,
    window: win = globalThis.window,
    container, histories,
  } = {},
) {
  const root = container
    ? container.createEl("section", { cls: "practice-review-dashboard" })
    : dv.el("section", "", { cls: "practice-review-dashboard" });
  function icon(parent, name) {
    const span = parent.createEl("span", {
      cls: "pr-icon",
      attr: { "aria-hidden": "true" },
    });
    span.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${ICONS[name]}</svg>`;
  }
  function link(parent, path, label, cls = "") {
    const a = parent.createEl("a", {
      text: label,
      cls,
      attr: { href: path, "data-href": path, class: "internal-link " + cls },
    });
    a.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      void app.workspace.openLinkText(path, "", false);
    });
    return a;
  }
  if (!container) {
    const header = root.createEl("header", { cls: "pr-header" });
    const heading = header.createEl("div", { cls: "pr-heading" });
    icon(heading, "review");
    heading.createEl("h1", { text: "Practice Review" });
    const navigation = header.createEl("nav");
    link(navigation, "Home.md", "Home ↗");
    link(navigation, "Learning/Practice/Review/AGENTS.md", "Review guide ↗");
  }
  const config = dv.page("system/modules/practice-review/module.md");
  if (!config || config.enabled !== true) {
    root.createEl("p", {
      text: config
        ? "Practice Review is paused."
        : "Practice Review configuration is unavailable.",
    });
    return;
  }
  const intervals = Array.from(config.interval_days ?? []);
  if (
    !intervals.length ||
    !intervals.every((n) => Number.isInteger(n) && n > 0)
  ) {
    root.createEl("p", {
      text: "The review intervals need a valid configuration.",
    });
    return;
  }
  const today = dateKey(now());
  const snapshot = buildSnapshot(
    Array.from(dv.pages('"Learning/Practice/Review/Items"')),
    today,
    intervals, histories,
  );
  root.createEl("p", {
    cls: "pr-subtitle",
    text: `${new Date(`${today}T12:00:00`).toLocaleDateString("en-AU", { weekday: "long", day: "numeric", month: "long", year: "numeric" })} · ${snapshot.counts.active} active items`,
  });
  const summary = root.createEl("div", { cls: "pr-metrics" });
  for (const [name, value, label, description] of [
    ["due", snapshot.counts.today, "Due today", "Scheduled for today"],
    ["overdue", snapshot.counts.overdue, "Overdue", "Earlier than today"],
    [
      "upcoming",
      snapshot.counts.nextSeven,
      "Next 7 days",
      "Scheduled after today",
    ],
    [
      "rounds",
      snapshot.counts.rounds,
      "Recorded rounds",
      "Includes archived item history",
    ],
  ]) {
    const card = summary.createEl("article", {
      cls: "pr-metric" + (name === "overdue" && value ? " has-overdue" : ""),
    });
    icon(card, name);
    card.createEl("strong", { text: String(value) });
    card.createEl("span", { text: label });
    card.createEl("small", { text: description });
  }
  const hint = root.createEl("div", { cls: "pr-next-action" });
  const due = snapshot.counts.today + snapshot.counts.overdue;
  const next = snapshot.items.find((p) => p.bucket === "upcoming");
  hint.createEl("strong", {
    text: due
      ? `${due} item${due === 1 ? "" : "s"} ready for review`
      : "You’re clear for today",
  });
  hint.createEl("span", {
    text: due
      ? "Review overdue items first, then today’s queue."
      : next
        ? `Next review: ${next.nextReview}. Start a new problem whenever you’re ready.`
        : "No scheduled reviews. Start a new problem or add an item.",
  });
  const command = hint.createEl("button", {
    text: "Copy /practice",
    attr: { type: "button" },
  });
  const copyStatus = hint.createEl("small", {
    attr: { role: "status", "aria-live": "polite" },
  });
  command.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText("/practice");
      copyStatus.textContent =
        "Copied. Paste /practice into your practice chat.";
    } catch {
      copyStatus.textContent = "Run /practice in your practice chat.";
    }
  });
  const domainCounts = new Map();
  for (const item of snapshot.items)
    domainCounts.set(item.domain, (domainCounts.get(item.domain) ?? 0) + 1);
  const domains = Array.from(
    new Set([
      ...Object.keys(config.practice_flows ?? DOMAIN_LABELS),
      ...domainCounts.keys(),
    ]),
  );
  const state = {
    domain: "all",
    status: due
      ? "due"
      : snapshot.counts.upcoming
        ? "upcoming"
        : snapshot.counts.unstarted
          ? "unstarted"
          : "all",
    search: "",
    day: null,
    page: 0,
  };
  const charts = root.createEl("div", { cls: "pr-charts" });
  const schedule = charts.createEl("article", { cls: "pr-panel" });
  schedule.createEl("h2", { text: "Next 7 days" });
  schedule.createEl("p", {
    cls: "pr-caption",
    text: "Click a day to see its scheduled items.",
  });
  const dayButtons = new Map();
  const bars = schedule.createEl("div", { cls: "pr-schedule" });
  const max = Math.max(1, ...snapshot.schedule.map((p) => p.count));
  for (const point of snapshot.schedule) {
    const date = new Date(`${point.day}T12:00:00`);
    const b = bars.createEl("button", {
      cls: "pr-day",
      attr: {
        type: "button",
        "aria-label": `${point.day}: ${point.count} scheduled ${point.count === 1 ? "item" : "items"}`,
        "aria-pressed": "false",
      },
    });
    b.createEl("strong", { text: String(point.count) });
    const rail = b.createEl("span", { cls: "pr-bar-rail" });
    rail.createEl("i", {
      attr: { style: `height:${(point.count / max) * 100}%;` },
    });
    b.createEl("span", {
      text: date.toLocaleDateString("en-AU", { weekday: "short" }),
    });
    b.createEl("small", {
      text: date.toLocaleDateString("en-AU", {
        month: "short",
        day: "numeric",
      }),
    });
    dayButtons.set(point.day, b);
    b.addEventListener("click", () => {
      state.day = state.day === point.day ? null : point.day;
      if (state.day) state.status = "upcoming";
      state.page = 0;
      renderList();
    });
  }
  const stagePanel = charts.createEl("article", { cls: "pr-panel" });
  stagePanel.createEl("h2", { text: "Scheduling stages" });
  stagePanel.createEl("p", {
    cls: "pr-caption",
    text: "Active, practiced items by configured interval.",
  });
  const stageMax = Math.max(1, ...snapshot.stages.map((p) => p.count));
  for (const stage of snapshot.stages) {
    const row = stagePanel.createEl("div", { cls: "pr-stage" });
    row.createEl("span", {
      text: `${stage.days} day${stage.days === 1 ? "" : "s"}`,
    });
    const rail = row.createEl("div", { cls: "pr-stage-rail" });
    rail.createEl("i", {
      attr: { style: `width:${(stage.count / stageMax) * 100}%;` },
    });
    row.createEl("strong", { text: String(stage.count) });
  }
  stagePanel.createEl("small", {
    cls: "pr-stage-note",
    text: "These are scheduling intervals, not mastery scores.",
  });
  const library = root.createEl("section", { cls: "pr-library" });
  library.createEl("h2", { text: "Review items" });
  const filters = library.createEl("div", { cls: "pr-filters" });
  const domain = filters.createEl("select", {
    attr: { "aria-label": "Filter by practice domain" },
  });
  domain.createEl("option", {
    text: `All domains (${snapshot.items.length})`,
    attr: { value: "all" },
  });
  for (const id of domains)
    domain.createEl("option", {
      text: `${DOMAIN_LABELS[id] ?? id} (${domainCounts.get(id) ?? 0})`,
      attr: { value: id },
    });
  domain.value = "all";
  domain.addEventListener("change", () => {
    state.domain = domain.value;
    state.page = 0;
    renderList();
  });
  const search = filters.createEl("input", {
    attr: {
      type: "search",
      placeholder: "Search title or ID…",
      "aria-label": "Search review items",
    },
  });
  search.addEventListener("input", () => {
    state.search = search.value;
    state.page = 0;
    renderList();
  });
  const tabs = library.createEl("div", {
    cls: "pr-tabs",
    attr: { role: "group", "aria-label": "Filter by review status" },
  });
  const statusButtons = new Map();
  const states = [
    ["due", "Due now", due],
    ["upcoming", "Upcoming", snapshot.counts.upcoming],
    ["unstarted", "Not started", snapshot.counts.unstarted],
    ["all", "All items", snapshot.items.length],
    ["archived", "Archived", snapshot.counts.archived],
  ];
  if (snapshot.counts.attention)
    states.push(["attention", "Needs attention", snapshot.counts.attention]);
  for (const [id, label, count] of states) {
    const b = tabs.createEl("button", {
      text: `${label} ${count}`,
      attr: { type: "button", "aria-pressed": "false" },
    });
    statusButtons.set(id, b);
    b.addEventListener("click", () => {
      state.status = id;
      state.day = null;
      state.page = 0;
      renderList();
    });
  }
  const selection = library.createEl("div", {
    cls: "pr-selection",
    attr: { role: "status", "aria-live": "polite" },
  });
  const list = library.createEl("div", { cls: "pr-table-wrap" });
  const pager = library.createEl("div", { cls: "pr-pagination" });
  const PAGE_SIZE = 20;
  function renderList() {
    for (const [id, label] of states) {
      const button = statusButtons.get(id);
      const count = selectItems(snapshot, {
        domain: state.domain,
        status: id,
        search: state.search,
      }).length;
      button.textContent = `${label} ${count}`;
      button.setAttribute("aria-pressed", String(state.status === id));
    }
    for (const [day, b] of dayButtons)
      b.setAttribute("aria-pressed", String(state.day === day));
    const rows = selectItems(snapshot, state);
    state.page = Math.min(
      state.page,
      Math.max(0, Math.ceil(rows.length / PAGE_SIZE) - 1),
    );
    selection.empty();
    selection.createEl("span", {
      text: `${rows.length} item${rows.length === 1 ? "" : "s"}${state.day ? ` scheduled for ${state.day}` : ""}`,
    });
    if (state.day) {
      const clear = selection.createEl("button", {
        text: "Clear date",
        attr: { type: "button" },
      });
      clear.addEventListener("click", () => {
        state.day = null;
        state.page = 0;
        renderList();
      });
    }
    list.empty();
    pager.empty();
    if (!rows.length) {
      list.createEl("p", {
        cls: "pr-empty",
        text:
          state.search || state.day || state.domain !== "all"
            ? "No items match these filters."
            : state.status === "due"
              ? "No overdue or due-today reviews. Your upcoming schedule is shown above."
              : state.status === "unstarted"
                ? "No active items are waiting for their first round."
                : state.status === "archived"
                  ? "No archived items."
                  : "No review items yet. Use /practice-review-add to register one.",
      });
      return;
    }
    const table = list.createEl("table");
    const head = table.createEl("thead").createEl("tr");
    for (const text of ["Item", "Next review", "Rounds", "Latest outcome"])
      head.createEl("th", { text, attr: { scope: "col" } });
    const body = table.createEl("tbody");
    for (const item of rows.slice(
      state.page * PAGE_SIZE,
      (state.page + 1) * PAGE_SIZE,
    )) {
      const row = body.createEl("tr");
      const identity = row.createEl("td");
      link(identity, item.path, item.title, "pr-item-link");
      identity.createEl("small", {
        text: `${item.id} · ${DOMAIN_LABELS[item.domain] ?? item.domain}`,
      });
      if (item.status === "active" && item.completed != null)
        identity.createEl("small", { text: `Round ${item.completed + 1} · ${item.completed < 2 ? "Guided learning" : item.completed === 2 ? "First independent review" : "Independent review"}` });
      const date = row.createEl("td");
      date.createEl("span", {
        text:
          item.nextReview ??
          (item.bucket === "attention" ? "Needs attention" : "Not scheduled"),
      });
      if (item.bucket === "overdue" || item.bucket === "today")
        date.createEl("small", {
          cls: "pr-" + item.bucket,
          text: item.bucket === "overdue" ? "Overdue" : "Today",
        });
      if (item.issues.length)
        identity.createEl("small", {
          cls: "pr-issue",
          text: item.issues.join(" · "),
        });
      row.createEl("td", {
        text: item.rounds === null ? "Needs attention" : String(item.rounds),
        cls: "pr-round-count",
      });
      const outcome = row.createEl("td");
      outcome.createEl("span", {
        cls:
          "pr-outcome " +
          (Object.hasOwn(OUTCOME_LABELS, item.outcome) ? item.outcome : ""),
        text: OUTCOME_LABELS[item.outcome] ?? "No recorded outcome",
      });
      if (item.lastReview) outcome.createEl("small", { text: item.lastReview });
    }
    if (rows.length > PAGE_SIZE) {
      const previous = pager.createEl("button", {
        text: "Previous",
        attr: { type: "button" },
      });
      previous.disabled = state.page === 0;
      previous.addEventListener("click", () => {
        state.page--;
        renderList();
      });
      pager.createEl("span", {
        text: `Page ${state.page + 1} of ${Math.ceil(rows.length / PAGE_SIZE)}`,
      });
      const next = pager.createEl("button", {
        text: "Next",
        attr: { type: "button" },
      });
      next.disabled = (state.page + 1) * PAGE_SIZE >= rows.length;
      next.addEventListener("click", () => {
        state.page++;
        renderList();
      });
    }
  }
  renderList();
  root.createEl("p", {
    cls: "pr-footnote",
    text: "Opening an item or changing a filter does not record a round. Review dates and reflections are saved through the existing practice workflow.",
  });
  let current = today,
    timer;
  const refreshDay = () => {
    const day = dateKey(now());
    if (day !== current) {
      current = day;
      app.workspace.trigger("dataview:refresh-views");
    }
  };
  const midnight = () => {
    const clock = now();
    timer = setTimeout(
      () => {
        refreshDay();
        midnight();
      },
      new Date(
        clock.getFullYear(),
        clock.getMonth(),
        clock.getDate() + 1,
        0,
        0,
        1,
      ) - clock,
    );
  };
  const visible = () => {
    if (!page.hidden) refreshDay();
  };
  midnight();
  win?.addEventListener("focus", refreshDay);
  page?.addEventListener("visibilitychange", visible);
  dv.component.register(() => {
    clearTimeout(timer);
    win?.removeEventListener("focus", refreshDay);
    page?.removeEventListener("visibilitychange", visible);
  });
  return root;
}
if (typeof dv === "undefined")
  module.exports = {
    dateKey,
    shiftDay,
    buildSnapshot,
    selectItems,
    renderDashboard,
  };
else {
  return (async () => {
    try {
      const histories = new Map();
      for (const p of dv.pages('"Learning/Practice/Review/Items"')) {
        if (p.domain === "system-design" && p.completed_design_rounds == null && p.review_count > 0)
          histories.set(p.file.path, await dv.io.load(p.file.path));
      }
      renderDashboard(dv, input.app, { container: input.container, histories });
    } catch (error) {
      dv.paragraph(`Practice Review could not load: ${error.message}`);
    }
  })();
}

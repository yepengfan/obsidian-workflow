return (async () => {
  const configs = {
    algorithm: {
      title: "Algorithm",
      folder: "Algorithm",
      tag: "leetcode",
      field: "problems_solved",
      command: "/algo-solve",
      icon: "⌘",
      description: "Practice history, reusable patterns, and building blocks.",
    },
    "system-design": {
      title: "System Design",
      folder: "System-Design",
      tag: "system-design",
      field: "problems_solved",
      command: "/sysd-solve",
      icon: "◇",
      description:
        "Continue a design, browse the roadmap, and revisit patterns.",
    },
    frontend: {
      title: "Frontend",
      folder: "Frontend",
      tag: "frontend",
      field: "challenges_completed",
      command: "/frnt-solve",
      icon: "▣",
      description: "Challenges, implementation patterns, and practice history.",
    },
  };
  const config = configs[input.domain];
  const shared = {
    app: input.app,
    ...config,
    links: [["Practice Review", "Learning/Practice/Review/00_index.md"]],
  };
  await dv.view("scripts/dashboard/ui", shared);
  const ui = shared.ui;
  const base = `Learning/Practice/${config.folder}`;
  const list = (value) =>
    value == null
      ? []
      : Array.isArray(value)
        ? value
        : typeof value.array === "function"
          ? value.array()
          : [value];
  const tagged = (folder, tag) =>
    Array.from(dv.pages(`"${base}/${folder}"`)).filter((p) =>
      list(p.file.tags).includes(`#${config.tag}/${tag}`),
    );
  const patterns = tagged("Patterns", "pattern");
  const logs = tagged("Log", "log");
  const date = (value) => {
    const d = dv.date(value);
    return d?.isValid ? d : null;
  };
  const today = dv.date("today");
  const weekStart = today.minus({ days: today.weekday - 1 });
  const completed = (p) => list(p[config.field]).length;
  const thisWeek = logs
    .filter((p) => {
      const d = date(p.date);
      return d && d >= weekStart && d <= today;
    })
    .reduce((n, p) => n + completed(p), 0);
  const problems = new Set(
    patterns.flatMap((p) => list(p.problems).map(String)),
  );
  ui.command(config.command);
  if (input.domain !== "frontend") ui.command(`/practice ${input.domain}`);
  ui.metrics([
    [patterns.length, "Patterns"],
    [problems.size, "Linked problems", "Unique entries in pattern cards"],
    [thisWeek, "This week", "Recorded completions"],
    [logs.length, "Practice logs"],
  ]);
  if (input.domain === "system-design") {
    const roadmap = list(dv.page("Learning/Plans/SYSD/00_plan")?.roadmap);
    const sessions = Array.from(dv.pages(`"${base}/Solutions"`))
      .filter((p) => p.file.name === "progress")
      .map((p) => {
        const topic = String(
          p.topic ||
            p.file.folder
              .split("/")
              .pop()
              .replace(/-\d{4}-\d{2}-\d{2}$/, ""),
        );
        const status =
          ["wip", "planned", "done"].find((s) =>
            list(p.file.tags).includes(`#system-design/${s}`),
          ) || "unknown";
        const index = roadmap.findIndex((item) =>
          list(item.aliases).some((alias) =>
            topic.toLowerCase().includes(String(alias).toLowerCase()),
          ),
        );
        const entry = roadmap[index];
        const diagrams = input.app.vault
          .getMarkdownFiles()
          .filter(
            (f) =>
              f.path.startsWith(`${p.file.folder}/`) &&
              f.path.endsWith(".excalidraw.md"),
          );
        return {
          path: p.file.path,
          title: String(entry?.title || topic),
          status,
          started: date(p.started)?.toISODate() || "-",
          focus: String(entry?.focus || ""),
          diagram: diagrams[0]?.path,
          order: index < 0 ? Infinity : index,
          search: `${topic} ${entry?.title || ""} ${entry?.focus || ""}`,
        };
      });
    ui.browser(
      ui.section(
        "Design sessions",
        "Open a session to inspect its progress. The roadmap order is preserved within planned sessions.",
      ),
      {
        rows: sessions,
        filters: [
          {
            key: "status",
            label: "Session status",
            options: [
              ["", "All sessions"],
              ["wip", "In progress"],
              ["planned", "Planned"],
              ["done", "Completed"],
              ["unknown", "Needs status"],
            ],
            match: (r, value) => r.status === value,
          },
        ],
        sort: (a, b) =>
          ["wip", "planned", "done", "unknown"].indexOf(a.status) -
            ["wip", "planned", "done", "unknown"].indexOf(b.status) ||
          a.order - b.order ||
          a.path.localeCompare(b.path),
        columns: [
          {
            label: "Session",
            render: (cell, r) => {
              ui.link(cell, r.path, r.title);
              if (r.focus) ui.el(cell, "p", r.focus, "mdash-muted");
            },
          },
          { label: "Status", key: "status" },
          { label: "Started", key: "started" },
          {
            label: "Canvas",
            render: (cell, r) => {
              if (r.diagram) ui.link(cell, r.diagram, "Open diagram");
              else cell.textContent = "Not created";
            },
          },
        ],
        empty:
          "No design sessions yet. Copy /sysd-solve to start one in your agent chat.",
      },
    );
  }
  const activity = [];
  for (let i = 11; i >= 0; i--) {
    const start = weekStart.minus({ weeks: i });
    const end = start.plus({ days: 6 });
    activity.push([
      start.toFormat("MMM dd"),
      logs
        .filter((p) => {
          const d = date(p.date);
          return d && d >= start && d <= end && d <= today;
        })
        .reduce((n, p) => n + completed(p), 0),
    ]);
  }
  ui.trend(
    ui.section(
      "Practice activity",
      "Recorded completions by week, oldest to newest. Current week is partial.",
    ),
    activity,
    "Weekly completions",
  );
  const categories = [
    ...new Set(patterns.map((p) => String(p.category || "Uncategorized"))),
  ].sort();
  ui.browser(ui.section("Pattern library"), {
    rows: patterns.map((p) => ({
      path: p.file.path,
      title: String(p.title || p.file.name),
      category: String(p.category || "Uncategorized"),
      problems: list(p.problems).length,
      updated: date(p.updated)?.toISODate() || "-",
      search: `${p.title || p.file.name} ${p.category || ""} ${list(p.problems).join(" ")}`,
    })),
    filters: [
      {
        key: "category",
        label: "Pattern category",
        options: [["", "All categories"], ...categories.map((c) => [c, c])],
        match: (r, value) => r.category === value,
      },
    ],
    sort: (a, b) =>
      a.category.localeCompare(b.category) || a.title.localeCompare(b.title),
    columns: [
      { label: "Pattern", render: (cell, r) => ui.link(cell, r.path, r.title) },
      { label: "Category", key: "category" },
      { label: "Linked problems", key: "problems" },
      { label: "Updated", key: "updated" },
    ],
    empty:
      "No patterns saved yet. They appear here after you save practice notes.",
  });
  if (input.domain === "algorithm") {
    ui.browser(
      ui.section("Reusable atoms", "Small techniques shared across patterns."),
      {
        rows: tagged("Atoms", "atom").map((p) => ({
          title: String(p.title || p.file.name),
          path: p.file.path,
          links: list(p.file.inlinks).length,
          updated: date(p.updated)?.toISODate() || "-",
          search: String(p.title || p.file.name),
        })),
        columns: [
          {
            label: "Atom",
            render: (cell, r) => ui.link(cell, r.path, r.title),
          },
          { label: "Incoming references", key: "links" },
          { label: "Updated", key: "updated" },
        ],
        sort: (a, b) =>
          b.updated.localeCompare(a.updated) || a.title.localeCompare(b.title),
        empty: "No atoms saved yet.",
      },
    );
    if (dv.page(`${base}/Weekly View`))
      ui.link(ui.actions, `${base}/Weekly View.md`, "Weekly view →");
  }
  ui.browser(ui.section("Practice logs"), {
    rows: logs.map((p) => ({
      path: p.file.path,
      title: p.file.name,
      count: completed(p),
      topics: list(p[config.field]).join(", "),
      search: `${p.file.name} ${list(p[config.field]).join(" ")}`,
    })),
    columns: [
      { label: "Date", render: (cell, r) => ui.link(cell, r.path, r.title) },
      { label: "Completions", key: "count" },
      { label: "Topics", key: "topics" },
    ],
    sort: (a, b) => b.title.localeCompare(a.title),
    empty: "No practice logs yet.",
  });
  if (input.domain === "system-design") {
    const resources = ui.section("Resources");
    const framework = `${base}/Frameworks/Delivery Framework.md`;
    if (input.app.vault.getAbstractFileByPath(framework))
      ui.link(resources, framework, "Delivery Framework");
    resources.createEl("p").createEl("a", {
      text: "Hello Interview",
      attr: { href: "https://www.hellointerview.com/" },
    });
    resources.createEl("p").createEl("a", {
      text: "Codemia",
      attr: { href: "https://codemia.io/" },
    });
  } else if (input.domain === "frontend") {
    ui.section("Resources").createEl("a", {
      text: "GreatFrontEnd",
      attr: { href: "https://www.greatfrontend.com/" },
    });
  }
})().catch((error) =>
  dv.paragraph(`Dashboard could not load: ${error.message}`),
);

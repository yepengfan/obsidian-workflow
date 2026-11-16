return (async () => {
  const shared = {
    app: input.app,
    title: "Learning",
    icon: "◇",
    description: "Active plans, roadmap progress, and weekly learning records.",
    links: [
      ["Practice Review", "Learning/Practice/Review/00_index.md"],
      ["Books", "Learning/Books/Books Index.md"],
    ],
  };
  await dv.view("scripts/dashboard/ui", shared);
  const ui = shared.ui;
  ui.command("/learning-review");
  ui.command("/learning-log");
  const plans = Array.from(dv.pages('"Learning/Plans"')).filter(
    (p) => p.file.name === "00_plan",
  );
  const logs = Array.from(dv.pages('"Learning/Plans"')).filter(
    (p) => p.week !== undefined,
  );
  const sessions = Array.from(
    dv.pages('"Learning/Practice/System-Design/Solutions"'),
  ).filter(
    (p) =>
      p.file.name === "progress" &&
      Array.from(p.file.tags || []).includes("#system-design/done"),
  );
  const rows = plans.map((p) => ({
    title: p.target || p.title || p.file.folder.split("/").pop(),
    code: p.file.folder.split("/").pop(),
    path: p.file.path,
    status: p.file.path.includes("/_archive/")
      ? "archived"
      : String(p.status || "unknown"),
    phase: p.phase || "-",
    plan: p,
    logs: logs.filter((l) => l.file.path.startsWith(`${p.file.folder}/`)),
    search: `${p.target || ""} ${p.title || ""} ${p.file.folder}`,
  }));
  ui.metrics([
    [rows.filter((r) => r.status === "active").length, "Active plans"],
    [rows.filter((r) => r.status === "paused").length, "Paused"],
    [
      rows.filter((r) => ["completed", "archived"].includes(r.status)).length,
      "Completed / archived",
    ],
    [logs.length, "Weekly logs"],
  ]);
  const statuses = [...new Set(rows.map((r) => r.status))].sort();
  ui.browser(
    ui.section(
      "Plans",
      "Active plans are shown first. Open a plan for its phases, milestones, and full context.",
    ),
    {
      rows,
      initial: {
        status: rows.some((r) => r.status === "active") ? "active" : "",
      },
      filters: [
        {
          key: "status",
          label: "Plan status",
          options: [
            ["", "All plans"],
            ...statuses.map((s) => [s, s[0].toUpperCase() + s.slice(1)]),
          ],
          match: (r, value) => r.status === value,
        },
      ],
      sort: (a, b) =>
        (a.status === "active" ? 0 : 1) - (b.status === "active" ? 0 : 1) ||
        a.code.localeCompare(b.code),
      empty: "No learning plans yet. Use /learning-init to create a plan.",
      renderCard(card, row) {
        const title = ui.el(card, "h3");
        ui.link(title, row.path, row.code);
        ui.el(card, "p", String(row.title));
        ui.el(
          card,
          "span",
          `${row.status} · Phase ${row.phase}`,
          "mdash-badge",
        );
        ui.el(
          card,
          "p",
          `${row.logs.length} weekly logs · Latest: ${
            row.logs
              .map((l) => String(l.week))
              .sort()
              .pop() || "none"
          }`,
          "mdash-muted",
        );
        const roadmap = Array.from(row.plan.roadmap || []);
        if (roadmap.length && row.plan.tracking === "system-design-practice") {
          const done = roadmap.filter((item) =>
            sessions.some((s) =>
              Array.from(item.aliases || []).some((alias) =>
                String(s.topic || "")
                  .toLowerCase()
                  .includes(String(alias).toLowerCase()),
              ),
            ),
          ).length;
          ui.el(
            card,
            "p",
            `${done} / ${roadmap.length} roadmap topics completed`,
          );
          card.createEl("progress", {
            cls: "mdash-progress",
            attr: {
              value: done,
              max: roadmap.length,
              "aria-label": `${done} of ${roadmap.length} roadmap topics completed`,
            },
          });
        }
        const actions = ui.el(card, "div", "", "mdash-actions");
        ui.link(actions, row.path, "Open plan →");
        const mapPath = `${row.plan.file.folder}/00_map.md`;
        if (input.app.vault.getAbstractFileByPath(mapPath))
          ui.link(actions, mapPath, "Concept map");
      },
    },
  );
  ui.browser(
    ui.section(
      "Weekly records",
      "Search the full log collection before pagination, including archived plans.",
    ),
    {
      rows: logs.map((p) => ({
        path: p.file.path,
        week: String(p.week),
        code: String(
          p.code ||
            plans
              .find((plan) => p.file.path.startsWith(`${plan.file.folder}/`))
              ?.file.folder.split("/")
              .pop() ||
            "Unknown",
        ),
        title: p.file.name,
        search: `${p.week} ${p.code || ""} ${p.file.path}`,
      })),
      filters: [
        {
          key: "code",
          label: "Learning plan",
          options: [["", "All plans"], ...rows.map((r) => [r.code, r.code])],
          match: (r, value) => r.code === value,
        },
      ],
      sort: (a, b) =>
        b.week.localeCompare(a.week) || a.path.localeCompare(b.path),
      columns: [
        { label: "Week", render: (cell, r) => ui.link(cell, r.path, r.week) },
        { label: "Plan", key: "code" },
      ],
      empty: "No weekly logs yet. Copy /learning-log to record progress.",
    },
  );
})().catch((error) =>
  dv.paragraph(`Dashboard could not load: ${error.message}`),
);

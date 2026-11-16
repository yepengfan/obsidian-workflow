return (async () => {
  const app = input.app;
  const shared = {
    app,
    title: "Work",
    icon: "▣",
    description: "Daily notes, project tasks, and longer views.",
    links: [
      ["Task Board", "Tasks/Board.md"],
      ["Weekly view", "Work/Weekly View.md"],
      ["Monthly view", "Work/Monthly View.md"],
      ["Brownbag", "Work/Brownbag Sessions/Brownbag Sessions.md"],
    ],
  };
  await dv.view("scripts/dashboard/ui", shared);
  const ui = shared.ui;
  ui.command("/work-daily");
  ui.command("/work-project");
  const today = dv.date("today");
  const weekStart = today.minus({ days: today.weekday - 1 });
  const daily = Array.from(dv.pages('"Work"')).filter((p) =>
    Array.from(p.file.tags || []).includes("#work-daily"),
  );
  const open = (p) =>
    Array.from(p.file.tasks || []).filter(
      (t) => !t.completed && ![">", "-"].includes(t.status),
    );
  const done = (p) => Array.from(p.file.tasks || []).filter((t) => t.completed);
  const valid = (value) => {
    const d = dv.date(value);
    return d?.isValid ? d : null;
  };
  const week = daily.filter((p) => {
    const d = valid(p.date);
    return d && d >= weekStart && d <= today;
  });
  const month = daily.filter((p) => {
    const d = valid(p.date);
    return (
      d && d.toFormat("yyyy-MM") === today.toFormat("yyyy-MM") && d <= today
    );
  });
  const todayPath = `Work/${today.toFormat("yyyy")}/${today.toISODate()}.md`;
  const todayNote = dv.page(todayPath);
  ui.metrics([
    [
      todayNote ? open(todayNote).length : 0,
      "Open today",
      todayNote ? "Today's work note" : "No note for today yet",
    ],
    [
      week.reduce((n, p) => n + open(p).length, 0),
      "Open this week",
      "Excludes forwarded and cancelled tasks",
    ],
    [week.reduce((n, p) => n + done(p).length, 0), "Completed this week"],
    [month.length, "Notes this month"],
  ]);
  const todayPanel = ui.section("Today", today.toFormat("cccc, dd MMMM yyyy"));
  if (todayNote) {
    ui.link(todayPanel, todayPath, "Open today's note →");
    const tasks = open(todayNote);
    if (tasks.length) {
      const list = ui.el(todayPanel, "ul");
      tasks.slice(0, 8).forEach((t) => ui.el(list, "li", t.text));
      if (tasks.length > 8)
        ui.el(
          todayPanel,
          "p",
          `+${tasks.length - 8} more in today's note`,
          "mdash-muted",
        );
    } else
      ui.el(todayPanel, "p", "No open tasks in today's note.", "mdash-muted");
  } else
    ui.el(
      todayPanel,
      "p",
      "No work note for today. Copy /work-daily above to create it with task rollover.",
      "mdash-empty",
    );
  const projects = Array.from(dv.pages('"Work/Projects"')).map((p) => {
    const tasks = daily
      .flatMap((note) => Array.from(note.file.tasks || []))
      .filter((t) => t.section?.subpath === p.file.name);
    return {
      title: p.file.name,
      path: p.file.path,
      status: String(p.status || "Unspecified"),
      open: tasks.filter((t) => !t.completed && ![">", "-"].includes(t.status))
        .length,
      done: tasks.filter((t) => t.completed).length,
      search: `${p.file.name} ${p.status || ""}`,
    };
  });
  ui.browser(
    ui.section(
      "Projects",
      "Counts come from matching project headings in work daily notes.",
    ),
    {
      rows: projects,
      sort: (a, b) => b.open - a.open || a.title.localeCompare(b.title),
      columns: [
        {
          label: "Project",
          render: (cell, r) => ui.link(cell, r.path, r.title),
        },
        { label: "Status", key: "status" },
        { label: "Open", key: "open" },
        { label: "Completed", key: "done" },
      ],
      empty: "No project pages yet. Copy /work-project to create one.",
    },
  );
  const rows = daily.map((p) => ({
    title: p.file.name,
    path: p.file.path,
    date: valid(p.date)?.toISODate() || p.file.name,
    year: valid(p.date)?.toFormat("yyyy") || "Unknown",
    open: open(p).length,
    done: done(p).length,
    search: `${p.file.name} ${p.file.path}`,
  }));
  ui.browser(
    ui.section(
      "Daily notes",
      "Use the year filter to browse history. Weekly and monthly views are available in the navigation above.",
    ),
    {
      rows,
      filters: [
        {
          key: "year",
          label: "Work year",
          options: [
            ["", "All years"],
            ...[...new Set(rows.map((r) => r.year))]
              .sort()
              .reverse()
              .map((y) => [y, y]),
          ],
          match: (r, value) => r.year === value,
        },
      ],
      sort: (a, b) => b.date.localeCompare(a.date),
      columns: [
        { label: "Date", render: (cell, r) => ui.link(cell, r.path, r.title) },
        { label: "Open", key: "open" },
        { label: "Completed", key: "done" },
      ],
      empty: "No work daily notes yet.",
    },
  );
})().catch((error) =>
  dv.paragraph(`Dashboard could not load: ${error.message}`),
);

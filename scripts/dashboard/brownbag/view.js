return (async () => {
  const shared = {
    app: input.app,
    title: "Brownbag",
    icon: "◉",
    description: "Sharing sessions and acceptance progress.",
    links: [
      ["Work", "Work/Work Dashboard.md"],
      ["Session template", "Templates/Brownbag Session.md"],
    ],
  };
  await dv.view("scripts/dashboard/ui", shared);
  const ui = shared.ui;
  const rows = Array.from(dv.pages('"Work/Brownbag Sessions"'))
    .filter((p) => String(p.id || "").startsWith("BB-"))
    .map((p) => {
      const criteria = Array.from(p.file.tasks || []).filter(
        (t) => t.section?.subpath === "验收标准",
      );
      const done = criteria.filter((t) => t.completed).length;
      const status =
        criteria.length && done === criteria.length
          ? "done"
          : done
            ? "in-progress"
            : "planning";
      return {
        title: p.title || p.file.name,
        path: p.file.path,
        id: p.id,
        status,
        progress: `${done} / ${criteria.length}`,
        created: p.created ? String(p.created).slice(0, 10) : "-",
        search: `${p.id} ${p.file.name} ${p.source || ""}`,
      };
    });
  ui.metrics([
    [rows.length, "Sessions"],
    [rows.filter((r) => r.status === "planning").length, "Planning"],
    [rows.filter((r) => r.status === "in-progress").length, "In progress"],
    [rows.filter((r) => r.status === "done").length, "Completed"],
  ]);
  ui.browser(
    ui.section(
      "Sessions",
      "Status follows the acceptance checklist in each session note.",
    ),
    {
      rows,
      filters: [
        {
          key: "status",
          label: "Session status",
          options: [
            ["", "All sessions"],
            ["planning", "Planning"],
            ["in-progress", "In progress"],
            ["done", "Completed"],
          ],
          match: (r, value) => r.status === value,
        },
      ],
      sort: (a, b) =>
        a.status === b.status
          ? b.created.localeCompare(a.created) ||
            String(a.id).localeCompare(String(b.id), undefined, {
              numeric: true,
            })
          : ["in-progress", "planning", "done"].indexOf(a.status) -
            ["in-progress", "planning", "done"].indexOf(b.status),
      columns: [
        {
          label: "Session",
          render: (cell, r) => ui.link(cell, r.path, `${r.id} · ${r.title}`),
        },
        { label: "Status", key: "status" },
        { label: "Acceptance", key: "progress" },
        { label: "Created", key: "created" },
      ],
      empty:
        "No sessions yet. Use the session template to plan a sharing session.",
    },
  );
})().catch((error) =>
  dv.paragraph(`Dashboard could not load: ${error.message}`),
);

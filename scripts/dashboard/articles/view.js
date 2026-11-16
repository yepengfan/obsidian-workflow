return (async () => {
  const shared = {
    app: input.app,
    title: "Articles",
    icon: "▤",
    description: "Saved reading from Matter and Instapaper.",
    links: [
      ["Matter index", "Matter/Matter Index.md"],
      ["Instapaper index", "Instapaper Notes/Instapaper Index.md"],
    ],
  };
  await dv.view("scripts/dashboard/ui", shared);
  const ui = shared.ui;
  const rows = [...dv.pages('"Matter"'), ...dv.pages('"Instapaper Notes"')]
    .filter((p) => !["Matter Index", "Instapaper Index"].includes(p.file.name))
    .map((p) => ({
      title: p.file.name,
      path: p.file.path,
      source: p.file.path.startsWith("Matter/") ? "Matter" : "Instapaper",
      updated: p.file.mtime.toFormat("yyyy-MM-dd"),
      time: +p.file.mtime,
      search: `${p.file.name} ${p.author || ""} ${p.file.tags || ""}`,
    }));
  ui.metrics([
    [rows.length, "Saved articles"],
    [rows.filter((r) => r.source === "Matter").length, "Matter"],
    [rows.filter((r) => r.source === "Instapaper").length, "Instapaper"],
  ]);
  ui.browser(
    ui.section(
      "Reading library",
      "Sorted by note update time. Synced highlights remain unchanged.",
    ),
    {
      rows,
      filters: [
        {
          key: "source",
          label: "Article source",
          options: [
            ["", "All sources"],
            ["Matter", "Matter"],
            ["Instapaper", "Instapaper"],
          ],
          match: (r, value) => r.source === value,
        },
      ],
      sort: (a, b) => b.time - a.time || a.title.localeCompare(b.title),
      columns: [
        {
          label: "Article",
          render: (cell, r) => ui.link(cell, r.path, r.title),
        },
        { label: "Source", key: "source" },
        { label: "Updated", key: "updated" },
      ],
      empty:
        "No saved articles yet. Imported Matter and Instapaper notes appear here.",
    },
  );
})().catch((error) =>
  dv.paragraph(`Dashboard could not load: ${error.message}`),
);

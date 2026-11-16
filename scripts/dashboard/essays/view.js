return (async () => {
  const shared = {
    app: input.app,
    title: "Essays",
    icon: "✎",
    description: "Long-form reflections, arguments, and open questions.",
    links: [["Zettelkasten", "Zettelkasten/Zettelkasten Index.md"]],
  };
  await dv.view("scripts/dashboard/ui", shared);
  const ui = shared.ui;
  const rows = Array.from(dv.pages('"Essays"'))
    .filter((p) => p.type === "essay")
    .map((p) => ({
      title: p.title || p.file.name,
      path: p.file.path,
      created: p.created ? String(p.created).slice(0, 10) : "-",
      topics: Array.from(p.file.tags || [])
        .filter((t) => t !== "#essay")
        .join(", "),
      updated: +p.file.mtime,
      search: `${p.title || p.file.name} ${p.file.tags || ""}`,
    }));
  ui.metrics([
    [rows.length, "Essays"],
    [
      new Set(rows.flatMap((r) => r.topics.split(", ")).filter(Boolean)).size,
      "Topics",
    ],
  ]);
  ui.browser(ui.section("Writing library"), {
    rows,
    sort: (a, b) => b.updated - a.updated || a.title.localeCompare(b.title),
    columns: [
      { label: "Essay", render: (cell, r) => ui.link(cell, r.path, r.title) },
      { label: "Created", key: "created" },
      { label: "Topics", key: "topics" },
    ],
    empty: "No essays yet. Notes marked type: essay appear here.",
  });
})().catch((error) =>
  dv.paragraph(`Dashboard could not load: ${error.message}`),
);

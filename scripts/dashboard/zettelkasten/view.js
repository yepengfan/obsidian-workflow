return (async () => {
  const app = input.app;
  const shared = {
    app,
    title: "Zettelkasten",
    icon: "✧",
    description: "Atomic ideas, connected sources, and notes ready for review.",
    links: [["Essays", "Essays/index.md"]],
  };
  await dv.view("scripts/dashboard/ui", shared);
  const ui = shared.ui;
  ui.command("/zettelkasten-inbox-review");
  const notes = Array.from(dv.pages('"Zettelkasten"')).filter(
    (p) => p.file.name !== "Zettelkasten Index",
  );
  const list = (value) =>
    value == null
      ? []
      : Array.isArray(value)
        ? value
        : typeof value.array === "function"
          ? value.array()
          : [value];
  function sourceInfo(value) {
    const raw = String(value || "");
    const match = /^\[\[([^|\]]+)(?:\|([^\]]+))?\]\]$/.exec(raw);
    const path = value?.path || match?.[1] || raw;
    const label =
      value?.display ||
      match?.[2] ||
      path.split("/").pop().replace(/\.md$/, "");
    return { path, label };
  }
  const rows = notes.map((p) => ({
    title: p.file.name,
    path: p.file.path,
    status: String(p.status || "unknown"),
    topics: list(p.topics).map(String),
    source: sourceInfo(p.source),
    references: list(p.file.inlinks).length + list(p.file.outlinks).length,
    time: +p.file.mtime,
    search: `${p.file.name} ${list(p.topics).join(" ")} ${p.source || ""}`,
  }));
  ui.metrics([
    [rows.length, "Zettel"],
    [
      Array.from(dv.pages('"Inbox"')).filter(
        (p) => !p.file.path.includes("/archive/"),
      ).length,
      "Inbox to process",
    ],
    [
      rows.filter((r) => r.status === "candidate").length,
      "Candidates",
      "Ready for your evergreen review",
    ],
    [rows.filter((r) => r.status === "evergreen").length, "Evergreen"],
  ]);
  const statuses = [...new Set(rows.map((r) => r.status))].sort();
  const topics = [...new Set(rows.flatMap((r) => r.topics))].sort();
  ui.browser(
    ui.section(
      "Notes",
      "Newest updates first. Search includes titles, topics, and sources.",
    ),
    {
      rows,
      filters: [
        {
          key: "status",
          label: "Note status",
          options: [
            ["", "All statuses"],
            ...statuses.map((s) => [s, s[0].toUpperCase() + s.slice(1)]),
          ],
          match: (r, value) => r.status === value,
        },
        {
          key: "topic",
          label: "Note topic",
          options: [["", "All topics"], ...topics.map((t) => [t, t])],
          match: (r, value) => r.topics.includes(value),
        },
      ],
      sort: (a, b) => b.time - a.time || a.title.localeCompare(b.title),
      columns: [
        {
          label: "Note",
          render: (cell, r) => {
            ui.link(cell, r.path, r.title);
            if (r.topics.length)
              ui.el(cell, "p", r.topics.join(" · "), "mdash-muted");
            if (r.source.label) {
              const source = ui.el(cell, "p", "", "mdash-muted mdash-source");
              source.title = r.source.label;
              if (
                app.vault.getAbstractFileByPath(r.source.path) ||
                app.vault.getAbstractFileByPath(`${r.source.path}.md`)
              )
                ui.link(source, r.source.path, r.source.label);
              else source.textContent = r.source.label;
            }
          },
        },
        {
          label: "Status",
          render: (cell, r) => {
            ui.el(cell, "span", r.status, "mdash-badge");
            if (r.status === "candidate") {
              const feedback = ui.el(cell, "p", "", "mdash-muted");
              feedback.setAttribute("role", "status");
              const controls = [];
              for (const [status, label] of [
                ["evergreen", "Mark evergreen"],
                ["growing", "Return to growing"],
              ])
                controls.push(
                  ui.button(cell, label, async () => {
                    controls.forEach((b) => (b.disabled = true));
                    try {
                      const file = app.vault.getAbstractFileByPath(r.path);
                      if (!file)
                        throw new Error("Note is no longer available.");
                      await app.fileManager.processFrontMatter(file, (fm) => {
                        if (fm.status !== "candidate")
                          throw new Error(
                            "Status changed. Reopen this dashboard before trying again.",
                          );
                        fm.status = status;
                      });
                      feedback.textContent = `Saved as ${status}.`;
                    } catch (error) {
                      feedback.textContent = error.message;
                      controls.forEach((b) => (b.disabled = false));
                    }
                  }),
                );
            }
          },
        },
        {
          label: "References",
          render: (cell, r) => {
            cell.textContent = String(r.references);
            cell.title =
              "Incoming plus outgoing references; not unique connections";
          },
        },
      ],
      empty: "No zettel yet. Process your Inbox to develop permanent notes.",
    },
  );
})().catch((error) =>
  dv.paragraph(`Dashboard could not load: ${error.message}`),
);

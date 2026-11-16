return (async () => {
  const app = input.app;
  const shared = {
    app,
    title: "Books",
    icon: "▥",
    description: "Reading, chapter understanding, and writing in one library.",
  };
  await dv.view("scripts/dashboard/ui", shared);
  const ui = shared.ui;
  ui.command("/book-read");
  ui.command("/book-init");
  const metas = Array.from(dv.pages('"Learning/Books"')).filter(
    (p) => p.file.name === "meta",
  );
  const captures = Array.from(dv.pages('"WeRead"')).filter(
    (p) => p.doc_type === "weread-highlights-reviews",
  );
  function channel(meta) {
    const raw = String(meta.reading_channel || "").toLowerCase();
    if (raw === "both" || (/weread/.test(raw) && /apple|ibooks/.test(raw)))
      return "both";
    if (/weread/.test(raw)) return "weread";
    if (/apple|ibooks/.test(raw)) return "apple-books";
    return meta.weread_source && meta.ibooks_source
      ? "both"
      : meta.weread_source
        ? "weread"
        : meta.ibooks_source
          ? "apple-books"
          : "unknown";
  }
  const channelNames = {
    weread: "WeRead",
    "apple-books": "Apple Books",
    both: "WeRead + Apple Books",
    unknown: "Channel unspecified",
  };
  function chapters(meta) {
    const all = Array.from(dv.pages(`"${meta.file.folder}/chapters"`))
      .filter((c) => c.chapter !== undefined)
      .sort((a, b) => a.chapter - b.chapter);
    const titled = all.filter(
      (c) => !/^Chapter\s+\d+$/i.test(String(c.title || "").trim()),
    );
    const bare = all.filter((c) =>
      /^Chapter\s+\d+$/i.test(String(c.title || "").trim()),
    );
    const repeated =
      titled.length &&
      bare.length === titled.length &&
      bare.every(
        (c, i) =>
          c.chapter > titled.length &&
          String(c.title).trim().toLowerCase() === `chapter ${i + 1}`,
      );
    return repeated ? titled : all;
  }
  function captureFor(meta) {
    const source =
      meta.weread_source?.path ||
      String(meta.weread_source || "")
        .replace(/^\[\[|\]\]$/g, "")
        .split("|")[0];
    return source ? dv.page(source) : null;
  }
  const rows = metas.map((meta) => {
    const items = chapters(meta);
    const counts = (type) =>
      items.filter(
        (c) =>
          meta.progress?.[`ch${String(c.chapter).padStart(2, "0")}`]?.[type] ===
          "done",
      ).length;
    const done = counts("understanding");
    return {
      meta,
      title: String(meta.title || meta.file.folder.split("/").pop()),
      status: String(meta.status || "unknown"),
      channel: channel(meta),
      chapters: items,
      done,
      mapped: counts("map"),
      search: `${meta.title || meta.file.folder} ${meta.author || ""} ${meta.archetype || ""}`,
      path: app.vault.getAbstractFileByPath(`${meta.file.folder}/MOC.md`)
        ? `${meta.file.folder}/MOC.md`
        : meta.file.path,
    };
  });
  ui.metrics([
    [rows.filter((r) => r.status === "reading").length, "Reading"],
    [rows.filter((r) => r.status === "finished").length, "Finished"],
    [rows.filter((r) => r.status === "paused").length, "Paused"],
    [
      rows.reduce((n, r) => n + r.done, 0),
      "Chapters understood",
      "Saved as done in the progress tracker",
    ],
  ]);
  ui.browser(
    ui.section(
      "Your books",
      "Chapter understanding and reading percentage measure different things.",
    ),
    {
      rows,
      initial: {
        status: rows.some((r) => r.status === "reading") ? "reading" : "",
      },
      filters: [
        {
          key: "status",
          label: "Book status",
          options: [
            ["", "All books"],
            ...[...new Set(rows.map((r) => r.status))]
              .sort()
              .map((s) => [s, s[0].toUpperCase() + s.slice(1)]),
          ],
          match: (r, value) => r.status === value,
        },
        {
          key: "channel",
          label: "Reading channel",
          options: [
            ["", "All reading channels"],
            ...Object.entries(channelNames),
          ],
          match: (r, value) => r.channel === value,
        },
      ],
      sort: (a, b) => a.title.localeCompare(b.title),
      empty:
        "No books onboarded yet. Copy /book-init to add one in your agent chat.",
      renderCard(card, row) {
        const { meta } = row;
        const coverValue = meta.cover || captureFor(meta)?.cover;
        if (coverValue) {
          const value = String(coverValue);
          const file = app.vault.getAbstractFileByPath(value);
          const src = /^https?:\/\//i.test(value)
            ? value
            : file
              ? app.vault.getResourcePath(file)
              : null;
          if (src) {
            const image = card.createEl("img", {
              cls: "mdash-book-cover",
              attr: { src, alt: "", loading: "lazy" },
            });
            image.addEventListener("error", () => image.remove(), {
              once: true,
            });
          }
        }
        const h = ui.el(card, "h3");
        ui.link(h, row.path, row.title);
        ui.el(
          card,
          "p",
          String(meta.author || "Author unspecified"),
          "mdash-muted",
        );
        ui.el(
          card,
          "span",
          `${row.status} · ${channelNames[row.channel]}`,
          "mdash-badge",
        );
        ui.el(
          card,
          "p",
          `${row.done} / ${row.chapters.length} chapters understood · ${row.mapped} mapped`,
        );
        if (row.chapters.length)
          card.createEl("progress", {
            cls: "mdash-progress",
            attr: {
              value: row.done,
              max: row.chapters.length,
              "aria-label": `${row.title}: ${row.done} of ${row.chapters.length} chapters understood`,
            },
          });
        if (["weread", "both"].includes(row.channel)) {
          const percent = String(
            captureFor(meta)?.progress ?? meta.weread_progress ?? "",
          );
          if (percent)
            ui.el(
              card,
              "p",
              `WeRead reading progress: ${percent}`,
              "mdash-muted",
            );
        }
        const links = ui.el(card, "div", "", "mdash-actions");
        ui.link(links, row.path, "Open book →");
        for (const [name, file] of [
          ["Understanding", "understanding"],
          ["Writing", "article"],
        ]) {
          const path = `${meta.file.folder}/${file}.md`;
          if (app.vault.getAbstractFileByPath(path)) ui.link(links, path, name);
        }
        if (row.chapters.length) {
          const details = ui.el(card, "details");
          ui.el(details, "summary", "Browse chapters");
          const list = ui.el(details, "ol");
          for (const c of row.chapters) {
            const state =
              meta.progress?.[`ch${String(c.chapter).padStart(2, "0")}`];
            const label = `${state?.understanding === "done" ? "✓ " : ""}${c.title || c.file.name}`;
            const understanding = `${meta.file.folder}/understanding.md`;
            const heading = `Ch${c.chapter}. ${String(c.title || "").replace(/^\d+[.\s]+/, "")}`;
            const target = app.vault.getAbstractFileByPath(understanding)
              ? `${understanding}#${heading.replace(/#/g, "%23")}`
              : c.file.path;
            ui.link(ui.el(list, "li"), target, label);
          }
        }
      },
    },
  );
  ui.browser(
    ui.section(
      "WeRead highlights",
      "Plugin-synced capture notes. These are separate from onboarded books and chapter understanding.",
    ),
    {
      rows: captures.map((p) => ({
        title:
          p.title || p.file.name.replace(/-CB_.*$/, "").replace(/-\d+$/, ""),
        path: p.file.path,
        progress: p.progress == null ? "Unknown" : String(p.progress),
        status: String(p.readingStatus || "Unknown"),
        search: `${p.title || p.file.name} ${p.author || ""}`,
        time: +p.file.mtime,
      })),
      sort: (a, b) => b.time - a.time || a.title.localeCompare(b.title),
      columns: [
        { label: "Book", render: (cell, r) => ui.link(cell, r.path, r.title) },
        { label: "Reading progress", key: "progress" },
      ],
      empty: "No WeRead capture notes synced yet.",
    },
  );
})().catch((error) =>
  dv.paragraph(`Dashboard could not load: ${error.message}`),
);

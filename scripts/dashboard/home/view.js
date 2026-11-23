// Pure calendar helpers keep counts stable across local midnight and DST.
function dayKey(value) {
  const raw =
    value?.toISODate?.() ??
    (value instanceof Date
      ? `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}-${String(value.getDate()).padStart(2, "0")}`
      : value);
  if (typeof raw !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(raw)) return null;
  const date = new Date(`${raw}T12:00:00Z`);
  return Number.isFinite(+date) && date.toISOString().slice(0, 10) === raw
    ? raw
    : null;
}
function shiftDay(day, days) {
  const d = new Date(`${day}T12:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}
function reviewCounts(items, today) {
  const out = { today: 0, overdue: 0, unstarted: 0, invalid: 0, rounds: 0 };
  for (const p of items) {
    if (!["active", "archived"].includes(p.status)) continue;
    if (Number.isInteger(p.review_count) && p.review_count >= 0)
      out.rounds += p.review_count;
    if (p.status !== "active") continue;
    if (p.next_review == null) {
      out.unstarted++;
      continue;
    }
    const day = dayKey(p.next_review);
    if (!day) out.invalid++;
    else if (day === today) out.today++;
    else if (day < today) out.overdue++;
  }
  return out;
}
function taskCounts(tasks, headings, today) {
  const start = headings.find((h) => h.level === 2 && h.heading === "Tasks")
    ?.position.start.line;
  const end =
    start == null
      ? -1
      : (headings.find((h) => h.level <= 2 && h.position.start.line > start)
          ?.position.start.line ?? Infinity);
  const open =
    start == null
      ? []
      : tasks.filter((t) => t.status === " " && t.line > start && t.line < end);
  const quadrants = [0, 0, 0, 0];
  let unclassified = 0;
  for (const t of open) {
    if (
      !Array.from(t.tags ?? []).some((tag) =>
        /^#?task\/[^\s#]+$/.test(String(tag)),
      )
    ) {
      unclassified++;
      continue;
    }
    const important = t.text.includes("⭐");
    const due = dayKey(t.due),
      urgent = due && due <= shiftDay(today, 7);
    quadrants[important ? (urgent ? 0 : 1) : urgent ? 2 : 3]++;
  }
  return {
    open,
    quadrants,
    unclassified,
    important: quadrants[0] + quadrants[1],
  };
}
function weeklyCounts(logs, field, today, count = 12) {
  const weekday = new Date(`${today}T12:00:00Z`).getUTCDay();
  const monday = shiftDay(today, -((weekday + 6) % 7));
  const start = shiftDay(monday, -7 * (count - 1)),
    values = Array(count).fill(0);
  for (const log of logs) {
    const day = dayKey(log.date);
    if (!day || day < start || day > today) continue;
    const index = Math.floor(
      (Date.parse(`${day}T12:00:00Z`) - Date.parse(`${start}T12:00:00Z`)) /
        604800000,
    );
    const entries = log[field];
    values[index] += Array.isArray(entries) ? entries.length : entries ? 1 : 0;
  }
  return values;
}
function hasTag(page, tag) {
  return Array.from(page.file?.tags ?? []).includes("#" + tag);
}
function countEntries(value) {
  return value == null ? 0 : Array.isArray(value) ? value.length : 1;
}
function sessionStatus(page) {
  const tags = Array.from(page.tags ?? page.file?.tags ?? []).map((t) =>
    String(t).replace(/^#/, ""),
  );
  return (
    ["done", "wip", "planned"].find((s) =>
      tags.includes("system-design/" + s),
    ) ?? "unknown"
  );
}
function brownbagStatus(page) {
  const tasks = Array.from(page.file.tasks ?? []).filter(
    (t) => t.section?.subpath === "验收标准",
  );
  return tasks.length && tasks.every((t) => t.completed)
    ? "done"
    : tasks.some((t) => t.completed)
      ? "in-progress"
      : "planning";
}
function spark(values) {
  const max = Math.max(1, ...values);
  return (
    `<svg role="img" aria-label="Last ${values.length} weeks: ${values.join(", ")}" viewBox="0 0 100 42">` +
    values
      .map(
        (v, i) =>
          `<rect x="${(i * 100) / values.length}" y="${40 - (v / max) * 34}" width="${70 / values.length}" height="${(v / max) * 34}" rx="1" fill="${i === values.length - 1 ? "var(--interactive-accent)" : "var(--home-chart-muted)"}"/>`,
      )
      .join("") +
    "</svg>"
  );
}
function segments(done, total) {
  if (!total) return "";
  return (
    `<div class="home-segments" role="img" aria-label="Completed ${done} of ${total}">` +
    Array.from(
      { length: total },
      (_, i) => `<i${i < done ? ' class="filled"' : ""}></i>`,
    ).join("") +
    "</div>"
  );
}
function distribution(values, labels) {
  const total = values.reduce((a, b) => a + b, 0);
  const title = labels.map((label, i) => `${label} ${values[i]}`).join("，");
  if (!total)
    return `<div class="home-distribution" role="img" aria-label="No records"><i style="flex:1;background:var(--background-modifier-border)"></i></div>`;
  return (
    `<div class="home-distribution" role="img" aria-label="${title}">` +
    values
      .map(
        (n, i) =>
          `<i style="flex:${total ? n : 1};background:var(--home-series-${i})"></i>`,
      )
      .join("") +
    "</div>"
  );
}
async function renderHome(dv, app, Notice) {
  const shared = {
    app,
    title: "Home",
    description: "Your dashboard and starting point.",
  };
  await dv.view("scripts/dashboard/ui", shared);
  const ICONS = shared.ui.icons;
  const root = shared.ui.content;
  root.classList.add("home-dashboard");
  if (dv.page("system/modules/dashboard/module")?.enabled !== true) {
    root.createEl("p", { text: "Home dashboard is paused." });
    return;
  }
  const today = dayKey(new Date());
  const query = (scope) => Array.from(dv.pages('"' + scope + '"'));
  function link(parent, path, label, cls = "") {
    const a = parent.createEl("a", {
      text: label,
      cls,
      attr: { href: path, "data-href": path, class: "internal-link " + cls },
    });
    a.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (!app.vault.getAbstractFileByPath(path)) {
        new Notice(
          path === "Tasks/Board.md"
            ? "Run /task-board to create your task board first"
            : "Dashboard unavailable: " + path,
        );
        return;
      }
      void app.workspace.openLinkText(path, "", false);
    });
    return a;
  }
  function group(title) {
    root.createEl("h2", { text: title });
    return root.createEl("div", { cls: "home-grid" });
  }
  function card(parent, id, title, icon, path) {
    const el = parent.createEl("article", { cls: "home-card" });
    const header = el.createEl("div", { cls: "home-card-head" }),
      name = header.createEl("div", { cls: "home-card-name" });
    const glyph = name.createEl("span", {
      cls: "home-icon",
      attr: { "aria-hidden": "true" },
    });
    glyph.innerHTML = ICONS[icon];
    name.createEl("h3", { text: title });
    link(header, path, "Dashboard ↗", "home-dashboard-link");
    const body = el.createEl("div", { cls: "home-card-body" }),
      footer = el.createEl("div", { cls: "home-card-footer" });
    const active = dv.page(`system/modules/${id}/module`)?.enabled === true;
    if (!active) {
      body.createEl("small", { text: "Module paused" });
      el.classList.add("is-paused");
    }
    return { el, body, footer, active };
  }
  function metric(body, n, label) {
    const el = body.createEl("div", { cls: "home-metric" });
    el.createEl("strong", { text: String(n) });
    el.createEl("small", { text: label });
  }
  function plot(body, markup, label) {
    const el = body.createEl("div", { cls: "home-plot" });
    el.innerHTML = markup;
    if (label) el.createEl("small", { text: label });
  }
  function button(parent, text, action) {
    const b = parent.createEl("button", { text });
    b.addEventListener("click", action);
    return b;
  }
  const daily = group("Daily");
  const review = card(
    daily,
    "practice-review",
    "Practice Review",
    "review",
    "Learning/Practice/Review/00_index.md",
  );
  if (review.active) {
    const stats = reviewCounts(query("Learning/Practice/Review/Items"), today);
    metric(review.body, stats.today, "Due today");
    metric(review.body, stats.overdue, "Overdue");
    metric(review.body, stats.unstarted, "Not started");
    link(
      review.footer,
      "Learning/Practice/Review/00_index.md",
      "Review queue →",
    );
    if (stats.invalid)
      review.footer.createEl("small", {
        text: `${stats.invalid} dates need attention`,
      });
  }
  const task = card(
    daily,
    "task-board",
    "Task Board",
    "task",
    "Tasks/Board.md",
  );
  if (task.active) {
    const p = dv.page("Tasks/Board.md"),
      file = app.vault.getAbstractFileByPath("Tasks/Board.md");
    const stats = taskCounts(
      Array.from(p?.file.tasks ?? []),
      file ? (app.metadataCache.getFileCache(file)?.headings ?? []) : [],
      today,
    );
    metric(task.body, stats.open.length, "Open");
    metric(task.body, stats.important, "Important");
    const matrix = task.body.createEl("div", {
      cls: "home-quadrants",
      attr: { "aria-label": "Task quadrant counts" },
    });
    const names = [
      "Important and urgent",
      "Important, not urgent",
      "Urgent, not important",
      "Neither important nor urgent",
    ];
    stats.quadrants.forEach((n, i) => {
      const cell = matrix.createEl("span", {
        cls: "q" + (i + 1),
        attr: { title: names[i] },
      });
      cell.createEl("small", { text: "Q" + (i + 1) });
      cell.createEl("b", { text: String(n) });
    });
    link(
      task.footer,
      "Tasks/Board.md",
      stats.unclassified
        ? `${stats.unclassified} unclassified →`
        : "Plan tasks →",
    );
  }
  const journal = card(
    daily,
    "journal",
    "Journal",
    "journal",
    "Journal/Dashboard.md",
  );
  if (journal.active) {
    journal.body.remove();
    journal.footer.remove();
    await dv.view("scripts/journal", {
      app,
      compact: true,
      container: journal.el,
    });
  }
  const learning = group("Learning");
  const plans = query("Learning/Plans").filter(
    (p) =>
      p.file.name === "00_plan" &&
      p.status === "active" &&
      !p.file.path.includes("/_archive/"),
  );
  const sessions = query("Learning/Practice/System-Design/Solutions").filter(
    (p) => p.file.name === "progress",
  );
  const plan = card(
    learning,
    "learning",
    "Learning",
    "learning",
    "Learning/Dashboard.md",
  );
  if (plan.active) {
    metric(plan.body, plans.length, "Active plans");
    const roadmapPlan = plans.find(
      (p) => p.tracking === "system-design-practice",
    );
    if (roadmapPlan) {
      const roadmap = Array.from(roadmapPlan.roadmap ?? []);
      const done = roadmap.filter((item) =>
        sessions.some(
          (p) =>
            sessionStatus(p) === "done" &&
            Array.from(item.aliases ?? []).some((a) =>
              String(p.topic ?? "")
                .toLowerCase()
                .includes(String(a).toLowerCase()),
            ),
        ),
      ).length;
      plot(
        plan.body,
        segments(done, roadmap.length),
        `${roadmapPlan.file.folder.split("/").pop()} · ${done} / ${roadmap.length}`,
      );
    }
    link(
      plan.footer,
      "Learning/Dashboard.md",
      plans.length
        ? plans.map((p) => p.file.folder.split("/").pop()).join(" · ") + " →"
        : "Browse plans →",
    );
  }
  const books = card(
    learning,
    "book-learning",
    "Books",
    "books",
    "Learning/Books/Books Index.md",
  );
  if (books.active) {
    const metas = query("Learning/Books").filter((p) => p.file.name === "meta"),
      reading = metas.filter((p) => p.status === "reading").length,
      finished = metas.filter((p) => p.status === "finished").length;
    metric(books.body, reading, "Reading");
    metric(books.body, finished, "Finished");
    const total = reading + finished,
      circ = 2 * Math.PI * 17;
    plot(
      books.body,
      `<svg role="img" aria-label="Reading ${reading}，Finished ${finished}" viewBox="0 0 48 48"><circle cx="24" cy="24" r="17" fill="none" stroke="var(--home-chart-muted)" stroke-width="6"/><circle cx="24" cy="24" r="17" fill="none" stroke="var(--home-series-0)" stroke-width="6" stroke-dasharray="${total ? (circ * finished) / total : 0} ${circ}" transform="rotate(-90 24 24)"/><text x="24" y="29" font-size="13" text-anchor="middle" fill="var(--text-normal)">${total}</text></svg>`,
      "Reading and finished books",
    );
    link(books.footer, "Learning/Books/Books Index.md", "Reading library →");
    button(books.footer, "WeRead library ↗", () => {
      if (
        !app.commands.executeCommandById(
          "obsidian-weread-plugin:open-weread-bookshelf-view",
        )
      )
        new Notice("WeRead library is unavailable");
    });
  }
  for (const [domain, id, title, icon, tag, field] of [
    [
      "Algorithm",
      "algorithm",
      "Algorithm",
      "algo",
      "leetcode",
      "problems_solved",
    ],
    [
      "System-Design",
      "system-design",
      "System Design",
      "sysd",
      "system-design",
      "problems_solved",
    ],
    [
      "Frontend",
      "frontend",
      "Frontend",
      "frontend",
      "frontend",
      "challenges_completed",
    ],
  ]) {
    const c = card(
      learning,
      id,
      title,
      icon,
      `Learning/Practice/${domain}/00_index.md`,
    );
    if (!c.active) continue;
    const patterns = query(`Learning/Practice/${domain}/Patterns`).filter((p) =>
      hasTag(p, tag + "/pattern"),
    );
    const logs = query(`Learning/Practice/${domain}/Log`).filter((p) =>
      hasTag(p, tag + "/log"),
    );
    if (id === "system-design") {
      const done = sessions.filter((p) => sessionStatus(p) === "done").length,
        planned = sessions.filter((p) => sessionStatus(p) === "planned").length,
        wip = sessions.filter((p) => sessionStatus(p) === "wip").length;
      metric(c.body, done, "Completed");
      metric(c.body, planned, "Planned");
      plot(
        c.body,
        distribution(
          [done, planned, wip],
          ["Completed", "Planned", "In progress"],
        ),
        `In progress ${wip}`,
      );
    } else if (id === "algorithm") {
      const values = weeklyCounts(logs, field, today);
      metric(c.body, patterns.length, "Patterns");
      plot(
        c.body,
        spark(values),
        `12-week activity · ${values.at(-1)} this week`,
      );
    } else {
      metric(c.body, patterns.length, "Patterns");
      metric(
        c.body,
        logs.reduce((n, p) => n + countEntries(p[field]), 0),
        "Completed challenges",
      );
    }
    link(
      c.footer,
      `Learning/Practice/${domain}/00_index.md`,
      "Practice library →",
    );
  }
  const knowledge = group("Knowledge & work");
  const zk = card(
    knowledge,
    "zettelkasten",
    "Zettelkasten",
    "zettel",
    "Zettelkasten/Zettelkasten Index.md",
  );
  if (zk.active) {
    metric(
      zk.body,
      query("Zettelkasten").filter((p) => p.file.name !== "Zettelkasten Index")
        .length,
      "Zettel",
    );
    metric(
      zk.body,
      query("Inbox").filter((p) => !p.file.path.includes("/archive/")).length,
      "Inbox to process",
    );
    const add = button(zk.footer, "+ Capture to Inbox", async () => {
      add.disabled = true;
      try {
        if (!app.vault.getAbstractFileByPath("Inbox"))
          await app.vault.createFolder("Inbox");
        let ts = Date.now(),
          path;
        do {
          path = `Inbox/${dayKey(new Date())}-${ts++}.md`;
        } while (app.vault.getAbstractFileByPath(path));
        await app.vault.create(path, "");
        await app.workspace.openLinkText(path, "", false);
      } catch (e) {
        new Notice(e.message);
      } finally {
        add.disabled = false;
      }
    });
  }
  const articles = card(
    knowledge,
    "articles",
    "Articles",
    "articles",
    "Library/Articles.md",
  );
  if (articles.active) {
    const matter = query("Matter").filter(
        (p) => p.file.name !== "Matter Index",
      ).length,
      insta = query("Instapaper Notes").filter(
        (p) => p.file.name !== "Instapaper Index",
      ).length;
    metric(articles.body, matter + insta, "Saved");
    plot(
      articles.body,
      distribution([matter, insta], ["Matter", "Instapaper"]),
      `Matter ${matter} · Instapaper ${insta}`,
    );
    link(articles.footer, "Library/Articles.md", "Reading library →");
  }
  const essays = card(
    knowledge,
    "essays",
    "Essays",
    "essays",
    "Essays/index.md",
  );
  if (essays.active) {
    metric(
      essays.body,
      query("Essays").filter((p) => p.type === "essay").length,
      "Essays",
    );
    link(essays.footer, "Essays/index.md", "Writing library →");
  }
  const work = card(
    knowledge,
    "work",
    "Work",
    "work",
    "Work/Work Dashboard.md",
  );
  if (work.active) {
    const shortcuts = work.body.createEl("div", { cls: "home-shortcuts" });
    for (const label of ["Daily tasks", "Project status", "Week / month views"])
      shortcuts.createEl("span", { text: label });
    link(work.footer, "Work/Work Dashboard.md", "Work overview →");
  }
  const brownbag = card(
    knowledge,
    "brownbag",
    "Brownbag",
    "brownbag",
    "Work/Brownbag Sessions/Brownbag Sessions.md",
  );
  if (brownbag.active) {
    const pages = query("Work/Brownbag Sessions").filter((p) =>
        String(p.id ?? "").startsWith("BB-"),
      ),
      done = pages.filter((p) => brownbagStatus(p) === "done").length;
    metric(brownbag.body, done, "Completed");
    metric(brownbag.body, pages.length - done, "Preparing");
    plot(
      brownbag.body,
      distribution([done, pages.length - done], ["Completed", "Preparing"]),
      `Acceptance complete ${done} / ${pages.length}`,
    );
    link(
      brownbag.footer,
      "Work/Brownbag Sessions/Brownbag Sessions.md",
      "Sessions & progress →",
    );
  }
  const profile = card(
    knowledge,
    "profile",
    "Profile",
    "profile",
    "Profile/Dashboard.md",
  );
  if (profile.active) {
    const p = dv.page("Profile/Personal Baseball Card.md");
    if (p) {
      const keys = [
        "deliberative",
        "detailed",
        "creative",
        "conceptual",
        "leadership",
        "tough",
        "nurturing",
        "extraverted",
        "composed",
        "determined",
        "humble",
        "autonomous",
      ];
      const values = keys.map((k) =>
        Math.max(0, Math.min(100, Number(p["py_" + k]) || 0)),
      );
      const points = values
        .map((v, i) => {
          const a = -Math.PI / 2 + (i * Math.PI) / 6;
          return `${30 + ((22 * v) / 100) * Math.cos(a)},${30 + ((22 * v) / 100) * Math.sin(a)}`;
        })
        .join(" ");
      plot(
        profile.body,
        `<svg role="img" aria-label="Assessment overview. Full dimensions on the Profile dashboard." viewBox="0 0 60 60"><circle cx="30" cy="30" r="22" fill="none" stroke="var(--home-chart-muted)"/><circle cx="30" cy="30" r="11" fill="none" stroke="var(--home-chart-muted)"/><polygon points="${points}" fill="var(--home-chart-muted)" stroke="var(--interactive-accent)" stroke-width="1.4"/></svg>`,
        "PrinciplesYou",
      );
    } else profile.body.createEl("small", { text: "No assessment added yet" });
    link(profile.footer, "Profile/Dashboard.md", "Assessment & profile →");
  }
  const footer = root.createEl("footer");
  link(footer, "system/registry.md", "Module registry");
  link(footer, "GETTING_STARTED.md", "Guide");
  // Dataview handles note changes. Calendar changes also refresh counts after sleep.
  let currentDay = today,
    timer;
  const refreshDay = () => {
    const next = dayKey(new Date());
    if (next !== currentDay) {
      currentDay = next;
      app.workspace.trigger("dataview:refresh-views");
    }
  };
  const midnight = () => {
    const now = new Date();
    timer = setTimeout(
      () => {
        refreshDay();
        midnight();
      },
      new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 0, 0, 1) -
        now,
    );
  };
  midnight();
  globalThis.window?.addEventListener("focus", refreshDay);
  dv.component.register(() => {
    clearTimeout(timer);
    globalThis.window?.removeEventListener("focus", refreshDay);
  });
}
if (typeof dv === "undefined")
  module.exports = {
    dayKey,
    shiftDay,
    reviewCounts,
    taskCounts,
    weeklyCounts,
    sessionStatus,
    brownbagStatus,
  };
else
  return renderHome(dv, input.app, input.Notice).catch((error) =>
    dv.paragraph(`Home could not refresh: ${error.message}`),
  );

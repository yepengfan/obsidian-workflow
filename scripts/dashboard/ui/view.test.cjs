const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
class Element {
  constructor(tag, options = {}) {
    this.tag = tag;
    this.children = [];
    this.textContent = options.text || "";
    this.cls = options.cls || "";
    this.attributes = options.attr || {};
    this.listeners = {};
    this.style = {
      setProperty(key, value) {
        this[key] = value;
      },
    };
    this.value = "";
    this.disabled = false;
    this.classList = {
      add: (name) => {
        this.cls += " " + name;
      },
    };
  }
  createEl(tag, options = {}) {
    const node = new Element(tag, options);
    this.children.push(node);
    if (tag === "option" && this.children.length === 1)
      this.value = node.attributes.value || "";
    return node;
  }
  setAttribute(key, value) {
    this.attributes[key] = value;
  }
  addEventListener(name, callback) {
    this.listeners[name] = callback;
  }
  empty() {
    this.children = [];
  }
  all() {
    return [this, ...this.children.flatMap((x) => x.all())];
  }
}
function clock(value = "2026-11-17") {
  if (value === "today") value = "2026-11-17";
  if (value?.toISODate) return value;
  const date = new Date(`${String(value).slice(0, 10)}T12:00:00Z`);
  const valid = Number.isFinite(+date);
  return {
    isValid: valid,
    weekday: date.getUTCDay() || 7,
    toISODate: () => (valid ? date.toISOString().slice(0, 10) : null),
    toFormat: (format) =>
      format === "yyyy"
        ? String(date.getUTCFullYear())
        : format === "yyyy-MM"
          ? date.toISOString().slice(0, 7)
          : date.toISOString().slice(0, 10),
    valueOf: () => +date,
    minus: ({ days = 0, weeks = 0 }) =>
      clock(
        new Date(+date - (days + weeks * 7) * 86400000)
          .toISOString()
          .slice(0, 10),
      ),
    plus: ({ days = 0 }) =>
      clock(new Date(+date + days * 86400000).toISOString().slice(0, 10)),
  };
}
function page(name, extra = {}) {
  return {
    file: {
      name,
      path: `${name}.md`,
      folder: name,
      tags: [],
      tasks: [],
      inlinks: [],
      outlinks: [],
      mtime: clock(),
    },
    ...extra,
  };
}
async function fixture(data = {}) {
  const roots = [],
    opened = [],
    cleanup = [];
  const app = {
    vault: {
      getAbstractFileByPath: (target) => ({ path: target }),
      getMarkdownFiles: () => [],
    },
    workspace: { openLinkText: async (...args) => opened.push(args) },
    fileManager: {
      processFrontMatter: async () => {
        throw Error("Unexpected write");
      },
    },
  };
  const dv = {
    el(tag, text, options) {
      const node = new Element(tag, options);
      roots.push(node);
      return node;
    },
    pages(scope) {
      return data[scope.slice(1, -1)] || [];
    },
    page(name) {
      return name.startsWith("system/modules/") ? { enabled: true } : null;
    },
    date: (value) => (value == null ? null : clock(value)),
    component: { register: (callback) => cleanup.push(callback) },
  };
  dv.view = async (name, input) => {
    const source = fs.readFileSync(
      path.resolve(__dirname, "../../..", name, "view.js"),
      "utf8",
    );
    return new AsyncFunction("dv", "input", source)(dv, input);
  };
  const shared = { app, title: "Articles" };
  await dv.view("scripts/dashboard/ui", shared);
  return {
    ...shared,
    dv,
    app,
    roots,
    opened,
    all: () => roots.flatMap((r) => r.all()),
    run: (name) => dv.view(name, { app }),
    cleanup: () => cleanup.forEach((fn) => fn()),
  };
}
test("collection search and filters operate on all rows before pagination; reset restores all results", async () => {
  const f = await fixture();
  const rows = Array.from({ length: 45 }, (_, i) => ({
    title: `Item ${i}`,
    search: `Item ${i}`,
    source: i % 2 ? "one" : "two",
  }));
  f.ui.browser(f.ui.section("Library"), {
    rows,
    filters: [
      {
        key: "source",
        label: "Source",
        options: [
          ["", "All"],
          ["one", "One"],
        ],
        match: (r, v) => r.source === v,
      },
    ],
    columns: [{ label: "Title", key: "title" }],
  });
  const search = f.all().find((n) => n.tag === "input");
  const select = f.all().find((n) => n.tag === "select");
  const count = () =>
    f.all().find((n) => n.cls.includes("mdash-result-count")).textContent;
  assert.equal(count(), "1-20 of 45 items");
  await f
    .all()
    .find((n) => n.textContent === "Next")
    .listeners.click();
  assert.equal(count(), "21-40 of 45 items");
  search.value = "Item 43";
  await search.listeners.input();
  assert.equal(count(), "1-1 of 1 matches (45 total)");
  select.value = "one";
  await select.listeners.change();
  assert.equal(count(), "1-1 of 1 matches (45 total)");
  search.value = "Item 44";
  await search.listeners.input();
  assert.equal(count(), "0 matches (45 total)");
  assert.ok(f.all().some((n) => n.textContent.includes("No matches.")));
  await f
    .all()
    .find((n) => n.textContent === "Reset")
    .listeners.click();
  assert.equal(count(), "1-20 of 45 items");
});
test("links navigate exactly once, preserve new-tab intent, and treat note titles as text", async () => {
  const f = await fixture();
  const a = f.ui.link(
    f.ui.content,
    "Example.md",
    "<img src=x onerror=alert(1)>",
  );
  let stopped = 0,
    prevented = 0;
  await a.listeners.click({
    metaKey: true,
    preventDefault() {
      prevented++;
    },
    stopPropagation() {
      stopped++;
    },
  });
  assert.deepEqual(f.opened, [["Example.md", "", true]]);
  assert.equal(stopped, 1);
  assert.equal(prevented, 1);
  assert.equal(a.textContent, "<img src=x onerror=alert(1)>");
  assert.equal(a.innerHTML, undefined);
});
test("all collection dashboards execute in the isolated Dataview scope with explicit empty states", async () => {
  for (const module of [
    "algorithm",
    "system-design",
    "frontend",
    "books",
    "learning",
    "articles",
    "essays",
    "brownbag",
    "work",
    "zettelkasten",
    "profile",
  ]) {
    const f = await fixture();
    await f.run(`scripts/dashboard/${module}`);
    assert.ok(
      f.all().some((n) => n.tag === "h1"),
      module,
    );
    assert.ok(
      f.all().some((n) => n.cls.includes("mdash-empty")),
      module,
    );
    assert.equal(
      f
        .all()
        .some((n) => n.textContent.startsWith("Dashboard could not load:")),
      false,
      module,
    );
    f.cleanup();
  }
});
test("book understanding only counts done, keeps reading channels separate, and never writes capture data", async () => {
  const meta = page("meta", {
    title: "Test book",
    status: "reading",
    reading_channel: "apple-books",
    weread_source: "WeRead/Test",
    progress: {
      ch01: { map: "done", understanding: "in_progress" },
      ch02: { understanding: "done" },
    },
  });
  meta.file.folder = "Learning/Books/Test";
  const f = await fixture({
    "Learning/Books": [meta],
    "Learning/Books/Test/chapters": [
      page("One", { chapter: 1 }),
      page("Two", { chapter: 2 }),
    ],
  });
  await f.run("scripts/dashboard/books");
  assert.ok(
    f
      .all()
      .some((n) => n.textContent === "1 / 2 chapters understood · 1 mapped"),
  );
  assert.ok(f.all().some((n) => n.textContent === "reading · Apple Books"));
  assert.equal(
    f.all().some((n) => n.textContent.includes("WeRead reading progress:")),
    false,
  );
});
test("Work excludes forwarded and cancelled tasks from open counts", async () => {
  const note = page("2026-11-17", { date: "2026-11-17" });
  note.file.tags = ["#work-daily"];
  note.file.tasks = [
    { text: "Open", status: " ", completed: false },
    { text: "Forwarded", status: ">", completed: false },
    { text: "Cancelled", status: "-", completed: false },
    { text: "Done", status: "x", completed: true },
  ];
  const f = await fixture({ Work: [note] });
  await f.run("scripts/dashboard/work");
  const metrics = f.all().filter((n) => n.cls === "mdash-metric");
  // The fixture also has a header-only dashboard; metrics belong to Work.
  assert.equal(
    metrics[1].children.find((n) => n.tag === "strong").textContent,
    "1",
  );
  assert.equal(
    metrics[2].children.find((n) => n.tag === "strong").textContent,
    "1",
  );
});

test("candidate actions preserve other metadata and reject a stale status", async () => {
  const note = page("Candidate", {
    status: "candidate",
    source: { path: "Source.md", display: "Source title" },
    topics: ["systems"],
  });
  const f = await fixture({ Zettelkasten: [note] });
  const metadata = {
    status: "candidate",
    created: "2020-01-01",
    reflection: "Original words",
  };
  f.app.fileManager.processFrontMatter = async (_file, change) =>
    change(metadata);
  await f.run("scripts/dashboard/zettelkasten");
  assert.ok(
    f.all().some((n) => n.tag === "a" && n.textContent === "Source title"),
  );
  const confirm = f.all().find((n) => n.textContent === "Mark evergreen");
  const revert = f.all().find((n) => n.textContent === "Return to growing");
  await confirm.listeners.click();
  assert.deepEqual(metadata, {
    status: "evergreen",
    created: "2020-01-01",
    reflection: "Original words",
  });
  assert.equal(confirm.disabled, true);
  await revert.listeners.click();
  assert.equal(metadata.status, "evergreen");
  assert.ok(f.all().some((n) => n.textContent.includes("Status changed.")));
});

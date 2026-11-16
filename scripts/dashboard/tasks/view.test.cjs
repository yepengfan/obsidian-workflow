const { test } = require("node:test");
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { taskDisplayText, taskArea, taskMatchesArea } = require("./view.js");
class Element {
  constructor(tag, options = {}) {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.parentElement = null;
    this.textContent = options.text || "";
    this.attributes = { ...options.attr };
    this.cls = options.cls || options.attr?.class || "";
    this.style = {};
    this.listeners = {};
    this.hidden = false;
    this.value = "";
    this.disabled = false;
    this.clientHeight = 36;
    this.scrollHeight = 18;
    this.classList = {
      add: (name) => {
        this.cls += " " + name;
      },
      toggle: (name, on) => {
        this.cls =
          this.cls
            .split(" ")
            .filter((c) => c !== name)
            .join(" ") + (on ? " " + name : "");
      },
    };
  }
  get childElementCount() {
    return this.children.length;
  }
  createEl(tag, options = {}) {
    const node = new Element(tag, options);
    this.appendChild(node);
    return node;
  }
  appendChild(node) {
    if (node.parentElement)
      node.parentElement.children = node.parentElement.children.filter(
        (n) => n !== node,
      );
    node.parentElement = this;
    this.children.push(node);
    return node;
  }
  setAttribute(name, value) {
    this.attributes[name] = value;
  }
  getAttribute(name) {
    return this.attributes[name];
  }
  addEventListener(name, handler) {
    this.listeners[name] = handler;
  }
  all() {
    return [this, ...this.children.flatMap((c) => c.all())];
  }
  querySelectorAll(selector) {
    if (selector === "li.dataview.task-list-item")
      return this.all().filter(
        (n) => n.tagName === "LI" && n.cls.includes("task-list-item"),
      );
    throw Error(selector);
  }
  focus() {}
  click() {
    if (!this.disabled)
      return this.listeners.click?.({
        preventDefault() {},
        stopPropagation() {},
      });
  }
}
class Rows extends Array {
  where(fn) {
    return new Rows(...this.filter(fn));
  }
  array() {
    return Array.from(this);
  }
}
function date(value) {
  const ms = Date.parse(
    (value === "today" ? "2026-11-17" : value) + "T00:00:00Z",
  );
  return {
    isValid: Number.isFinite(ms),
    valueOf: () => ms,
    plus: ({ days }) =>
      date(new Date(ms + days * 86400000).toISOString().slice(0, 10)),
    endOf: () => ({ valueOf: () => ms + 86399999 }),
    toFormat: () => new Date(ms).toISOString().slice(0, 10),
  };
}
function fixture(tasks) {
  const container = new Element("div"),
    cleanups = [],
    notices = [];
  const rows = new Rows(
    ...tasks.map((t, i) => ({ status: " ", line: i + 1, ...t })),
  );
  let content =
    "## Tasks\n" +
    rows.map((t) => "- [ ] " + t.text).join("\n") +
    "\n## Done\n";
  let writes = 0;
  const app = {
    isMobile: false,
    vault: {
      getAbstractFileByPath: (path) => ({ path }),
      process: async (_file, change) => {
        writes++;
        content = change(content);
      },
    },
    metadataCache: {
      getFileCache: () => ({
        headings: [
          { level: 2, heading: "Tasks", position: { start: { line: 0 } } },
          {
            level: 2,
            heading: "Done",
            position: { start: { line: rows.length + 1 } },
          },
        ],
      }),
    },
    workspace: { trigger() {} },
  };
  const dv = {
    container,
    page: () => ({ file: { tasks: rows } }),
    date,
    component: { register: (fn) => cleanups.push(fn) },
    taskList(items) {
      const root = container.createEl("div");
      const list = root.createEl("ul");
      for (const item of items) {
        const li = list.createEl("li", { cls: "dataview task-list-item" });
        li.createEl("input");
        const span = li.createEl("span", { text: item.visual });
        span.scrollHeight = item.visual.length > 70 ? 72 : 18;
      }
    },
  };
  class Observer {
    constructor(callback) {
      this.callback = callback;
    }
    observe() {
      this.callback();
    }
    disconnect() {}
  }
  new Function(
    "dv",
    "input",
    "ResizeObserver",
    readFileSync(__dirname + "/view.js", "utf8"),
  )(
    dv,
    {
      app,
      Notice: class {
        constructor(message) {
          notices.push(message);
        }
      },
      Menu: class {},
    },
    Observer,
  );
  return {
    container,
    all: () => container.all(),
    cleanup: () => cleanups.forEach((fn) => fn()),
    content: () => content,
    writes: () => writes,
    notices,
  };
}
const tasks = [
  { text: "⭐ Prepare a story #task/work", tags: ["#task/work"] },
  { text: "Book an appointment #task/life", tags: ["#task/life"] },
  { text: "Decide an area later", tags: [] },
];
test("display text strips scheduling metadata while preserving links, code, and the source text", () => {
  const source =
    "⭐ 📅 2026-11-18 Read [[Note|#task/work]] and `#task/life` [guide](https://example.com/#task/work) #task/work [due:: 2026-11-18]";
  assert.equal(
    taskDisplayText(source),
    "Read [[Note|#task/work]] and `#task/life` [guide](https://example.com/#task/work)",
  );
  assert.ok(source.startsWith("⭐"));
  assert.equal(
    taskDisplayText("Read [[Two  spaces]] and `a  b` #task/work"),
    "Read [[Two  spaces]] and `a  b`",
  );
  assert.equal(taskArea({ tags: ["#task/"] }), null);
  assert.equal(taskMatchesArea({ tags: ["#task/work"] }, "life"), false);
  assert.equal(taskMatchesArea({ tags: [] }, "life"), true);
});
test("area filters synchronize quadrant counts, empty states, and the editable task list", () => {
  const f = fixture(tasks);
  const filter = f
    .all()
    .find((n) => n.attributes["aria-label"] === "Filter tasks by area");
  const life = filter.children.find((n) => n.textContent === "Life");
  life.click();
  const quads = f.all().filter((n) => n.cls === "tb-quadrant");
  assert.deepEqual(
    quads.map((q) => q.all().find((n) => n.cls === "tb-count").textContent),
    ["0", "0", "0", "1"],
  );
  assert.equal(quads[1].all().find((n) => n.cls === "tb-empty").hidden, false);
  assert.equal(
    quads[1].all().find((n) => n.cls === "tb-empty").textContent,
    "No Life tasks",
  );
  const list = f.all().find((n) => n.cls === "tb-list");
  const visible = list
    .all()
    .filter((n) => n.cls.includes("tb-task-row") && !n.hidden);
  assert.equal(visible.length, 2); // Life plus the task requiring classification.
  assert.equal(
    visible.some((n) =>
      n.all().some((c) => c.textContent.includes("Prepare a story")),
    ),
    false,
  );
  assert.ok(f.all().some((n) => n.cls === "tb-unclassified"));
  assert.equal(f.writes(), 0);
  filter.children.find((n) => n.textContent === "All").click();
  assert.equal(
    list.all().filter((n) => n.cls.includes("tb-task-row") && !n.hidden).length,
    3,
  );
  f.cleanup();
});
test("zero-match filters show zero counts and empty states, without an empty unclassified panel", () => {
  const f = fixture([tasks[0]]);
  const filter = f
    .all()
    .find((n) => n.attributes["aria-label"] === "Filter tasks by area");
  filter.children.find((n) => n.textContent === "Life").click();
  assert.equal(
    f.all().some((n) => n.cls === "tb-unclassified"),
    false,
  );
  assert.ok(
    f
      .all()
      .filter((n) => n.cls === "tb-count")
      .every((n) => n.textContent === "0"),
  );
  assert.equal(
    f.all().find((n) => n.cls === "tb-filter-status").textContent,
    "0 Life tasks",
  );
  assert.equal(
    f
      .all()
      .find((n) => n.cls === "tb-list")
      .all()
      .some((n) => n.cls === "tb-empty" && !n.hidden),
    true,
  );
  assert.equal(f.writes(), 0);
});
test("importance and due date preview all quadrants without writing a task", () => {
  const f = fixture([]),
    star = f.all().find((n) => n.cls === "tb-important"),
    due = f.all().find((n) => n.attributes["aria-label"] === "Due date");
  const preview = () =>
    f.all().find((n) => n.cls === "tb-destination").textContent;
  assert.equal(preview(), "Will add to Q4 · Later");
  star.click();
  assert.equal(preview(), "Will add to Q2 · Schedule");
  due.value = "2026-11-24";
  due.listeners.input();
  assert.equal(preview(), "Will add to Q1 · Do now");
  star.click();
  assert.equal(preview(), "Will add to Q3 · Handle quickly");
  due.value = "2026-11-25";
  due.listeners.input();
  assert.equal(preview(), "Will add to Q4 · Later");
  assert.equal(f.writes(), 0);
});
test("long task previews expand and collapse without rewriting records", () => {
  const f = fixture([
    { text: "A long task ".repeat(12) + "#task/work", tags: ["#task/work"] },
  ]);
  const expand = f.all().find((n) => n.cls === "tb-expand");
  const before = f.content();
  assert.equal(expand.hidden, false);
  expand.click();
  assert.equal(expand.attributes["aria-expanded"], "true");
  assert.equal(expand.textContent, "Show less");
  expand.click();
  assert.equal(expand.attributes["aria-expanded"], "false");
  assert.equal(f.content(), before);
  assert.equal(f.writes(), 0);
  f.cleanup();
});
test("rapid repeated capture adds once and retains source metadata", async () => {
  const f = fixture([]),
    title = f.all().find((n) => n.attributes["aria-label"] === "Task title"),
    add = f.all().find((n) => n.textContent === "+ Add task");
  title.value = "A new task";
  await Promise.all([add.click(), add.click()]);
  assert.equal(f.writes(), 1);
  assert.match(f.content(), /- \[ \] A new task #task\/work/);
  assert.equal(title.value, "");
  assert.equal(add.disabled, false);
});

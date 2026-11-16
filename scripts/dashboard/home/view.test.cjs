const { test } = require("node:test");
const assert = require("node:assert/strict");
const {
  dayKey,
  shiftDay,
  reviewCounts,
  taskCounts,
  weeklyCounts,
} = require("./view.js");
test("review counts validate dates, distinguish unscheduled items and retain archived history", () => {
  const items = [
    { status: "active", next_review: null, review_count: 0 },
    { status: "active", next_review: "2026-11-17", review_count: 2 },
    { status: "active", next_review: "2026-11-16", review_count: 3 },
    { status: "active", next_review: "2026-11-18" },
    { status: "active", next_review: "2026-02-30" },
    { status: "archived", next_review: "2020-01-01", review_count: 7 },
  ];
  assert.deepEqual(reviewCounts(items, "2026-11-17"), {
    today: 1,
    overdue: 1,
    unstarted: 1,
    invalid: 1,
    rounds: 12,
  });
});
test("task summary only counts the real Tasks section and keeps unclassified work separate", () => {
  const h = (heading, line) => ({
    level: 2,
    heading,
    position: { start: { line } },
  });
  const t = (line, text, due, tags = ["#task/work"], status = " ") => ({
    line,
    text,
    due,
    tags,
    status,
  });
  const tasks = [
    t(1, "before"),
    t(6, "⭐", "2026-11-24"),
    t(7, "⭐", "2026-11-25"),
    t(8, "plain", "2020-01-01"),
    t(9, "plain"),
    t(10, "⭐", null, []),
    t(11, "finished", null, undefined, "x"),
    t(15, "other section"),
    t(22, "done section"),
  ];
  const result = taskCounts(
    tasks,
    [h("Tasks", 5), h("Notes", 14), h("Done", 20)],
    "2026-11-17",
  );
  assert.equal(result.open.length, 5);
  assert.deepEqual(result.quadrants, [1, 1, 1, 1]);
  assert.equal(result.unclassified, 1);
  assert.equal(result.important, 2);
  assert.equal(taskCounts(tasks, [], "2026-11-17").open.length, 0);
});
test("weekly activity uses calendar weeks and excludes future/invalid records", () => {
  const logs = [
    { date: "2026-11-15", problems_solved: [1, 2] },
    { date: "2026-11-16", problems_solved: [3] },
    { date: "2026-11-17", problems_solved: [4] },
    { date: "2026-11-18", problems_solved: [5] },
    { date: "bad", problems_solved: [6] },
  ];
  assert.deepEqual(
    weeklyCounts(logs, "problems_solved", "2026-11-17", 2),
    [2, 2],
  );
  assert.equal(shiftDay("2026-10-03", 1), "2026-10-04");
  assert.equal(dayKey("2026-02-30"), null);
  assert.equal(dayKey({ toISODate: () => "2024-02-29" }), "2024-02-29");
});

test("the isolated Dataview custom view renders every module and handles internal links once", async (t) => {
  const fs = require("node:fs"),
    vm = require("node:vm");
  const roots = [],
    cleanup = [],
    opened = [];
  class Element {
    constructor(tag, options = {}) {
      this.tag = tag;
      this.textContent = options.text ?? "";
      this.cls = options.cls ?? "";
      this.children = [];
      this.listeners = {};
      this.classList = { add: () => {} };
    }
    createEl(tag, options) {
      const child = new Element(tag, options);
      this.children.push(child);
      return child;
    }
    addEventListener(name, fn) {
      this.listeners[name] = fn;
    }
    remove() {}
    all() {
      return [this, ...this.children.flatMap((c) => c.all())];
    }
  }
  const dv = {
    el(tag, text, options) {
      const el = new Element(tag, options);
      roots.push(el);
      return el;
    },
    page(path) {
      return path.startsWith("system/modules/") ? { enabled: true } : null;
    },
    pages() {
      return [];
    },
    view: async () => {},
    paragraph(text) {
      roots.push(new Element("p", { text }));
    },
    component: {
      register(fn) {
        cleanup.push(fn);
      },
    },
  };
  const app = {
    vault: { getAbstractFileByPath: (path) => ({ path }) },
    metadataCache: { getFileCache: () => ({ headings: [] }) },
    workspace: {
      openLinkText: async (path) => opened.push(path),
      trigger() {},
    },
  };
  t.after(() => cleanup.forEach((fn) => fn()));
  const source = fs.readFileSync(__dirname + "/view.js", "utf8");
  // dv.view uses a separate Function scope: plugin-local require is unavailable there.
  await vm.runInNewContext(
    "(async function(dv,input){" + source + "})(dv,input)",
    { dv, input: { app, Notice: class {} }, setTimeout, clearTimeout, Date },
  );
  const all = roots.flatMap((r) => r.all());
  assert.equal(all.filter((el) => el.tag === "h3").length, 14);
  assert.equal(
    all.some((el) => el.textContent.startsWith("Home 未能更新")),
    false,
  );
  const link = all.find(
    (el) => el.tag === "a" && el.textContent === "仪表盘 ↗",
  );
  let prevented = false,
    stopped = false;
  await link.listeners.click({
    preventDefault() {
      prevented = true;
    },
    stopPropagation() {
      stopped = true;
    },
  });
  assert.equal(prevented, true);
  assert.equal(stopped, true);
  assert.deepEqual(opened, ["Learning/Practice/Review/00_index.md"]);
});

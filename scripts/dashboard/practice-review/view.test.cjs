const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const {
  dateKey,
  shiftDay,
  buildSnapshot,
  selectItems,
  renderDashboard,
} = require("./view.js");
const TODAY = "2026-11-17",
  INTERVALS = [1, 3, 7, 14, 30];
function item(id, overrides = {}) {
  return {
    id,
    title: "Review " + id,
    domain: "algorithm",
    status: "active",
    review_count: 1,
    stage: 0,
    last_review: "2026-11-16",
    next_review: "2026-11-18",
    last_result: "passed",
    unmet_criteria: [],
    file: { name: id, path: `Learning/Practice/Review/Items/${id}.md` },
    ...overrides,
  };
}
test("totals separate the live queue from archived history and future dates", () => {
  const snapshot = buildSnapshot(
    [
      item("overdue", { next_review: "2026-11-16" }),
      item("today", { next_review: TODAY }),
      item("tomorrow"),
      item("day-seven", { next_review: "2026-11-24" }),
      item("later", { next_review: "2026-11-25" }),
      item("first", { next_review: null, last_review: null, review_count: 0 }),
      item("old", {
        status: "archived",
        review_count: 8,
        next_review: "2020-01-01",
      }),
    ],
    TODAY,
    INTERVALS,
  );
  assert.deepEqual(snapshot.counts, {
    overdue: 1,
    today: 1,
    upcoming: 3,
    unstarted: 1,
    archived: 1,
    attention: 0,
    attempts: 13,
    active: 6,
    nextSeven: 2,
  });
  assert.deepEqual(
    snapshot.schedule.map((p) => [p.day, p.count]),
    [
      ["2026-11-18", 1],
      ["2026-11-19", 0],
      ["2026-11-20", 0],
      ["2026-11-21", 0],
      ["2026-11-22", 0],
      ["2026-11-23", 0],
      ["2026-11-24", 1],
    ],
  );
  assert.equal(snapshot.stages[0].count, 5);
});
test("invalid metadata remains visible without entering the scheduled queue", () => {
  const snapshot = buildSnapshot(
    [
      item("date", { next_review: "2026-02-30" }),
      item("attempts", { review_count: -1 }),
      item("stage", { stage: 6 }),
      item("last", { last_review: "not-a-date" }),
      item("missing-id", { id: null }),
    ],
    TODAY,
    INTERVALS,
  );
  assert.equal(snapshot.counts.attention, 5);
  assert.equal(snapshot.counts.upcoming, 0);
  assert.equal(selectItems(snapshot, { status: "attention" }).length, 5);
  assert.ok(snapshot.items.every((p) => p.issues.length > 0));
  assert.equal(
    snapshot.stages.reduce((n, p) => n + p.count, 0),
    0,
  );
});
test("dates are strict calendar dates and advance across month, year and DST boundaries", () => {
  assert.equal(dateKey("2024-02-29"), "2024-02-29");
  assert.equal(dateKey("2026-02-29"), null);
  assert.equal(dateKey("2026-11-17T00:00:00Z"), null);
  assert.equal(dateKey({ isValid: false, toISODate: () => TODAY }), null);
  assert.equal(dateKey({ isValid: true, toISODate: () => TODAY }), TODAY);
  assert.equal(shiftDay("2026-12-31", 1), "2027-01-01");
  assert.equal(shiftDay("2026-10-03", 1), "2026-10-04");
});
test("domain, status, search and selected calendar day compose without losing stable due order", () => {
  const snapshot = buildSnapshot(
    [
      item("b"),
      item("a"),
      item("c", { domain: "system-design", next_review: TODAY }),
      item("d", { domain: "system-design", status: "archived" }),
      item("e", { next_review: "2026-11-16" }),
    ],
    TODAY,
    INTERVALS,
  );
  assert.deepEqual(
    selectItems(snapshot, { status: "due" }).map((p) => p.id),
    ["e", "c"],
  );
  assert.deepEqual(
    selectItems(snapshot, {
      domain: "algorithm",
      status: "upcoming",
      search: "REVIEW",
      day: "2026-11-18",
    }).map((p) => p.id),
    ["a", "b"],
  );
  assert.deepEqual(
    selectItems(snapshot, { status: "archived" }).map((p) => p.id),
    ["d"],
  );
  assert.equal(
    selectItems(snapshot, { domain: "system-design", search: "algorithm" })
      .length,
    0,
  );
});
class Element {
  constructor(tag, options = {}) {
    this.tag = tag;
    this.textContent = options.text ?? "";
    this.cls = options.cls ?? "";
    this.attributes = options.attr ?? {};
    this.children = [];
    this.listeners = {};
    this.value = "";
  }
  createEl(tag, options) {
    const el = new Element(tag, options);
    this.children.push(el);
    return el;
  }
  addEventListener(name, fn) {
    this.listeners[name] = fn;
  }
  setAttribute(name, value) {
    this.attributes[name] = value;
  }
  empty() {
    this.children = [];
  }
  all() {
    return [this, ...this.children.flatMap((p) => p.all())];
  }
}
function fixture(
  pages,
  { enabled = true, intervals = INTERVALS, archiveAfterFinal = false } = {},
) {
  const roots = [],
    cleanup = [],
    opened = [],
    events = [];
  const config = {
    enabled,
    schedule: {
      intervals,
      on_fail: { step_back: 1, retry_days: 1 },
      archive_after_final: archiveAfterFinal,
    },
    consumers: {
      algorithm: { enabled: true, flow: "algo-solve" },
      "system-design": { enabled: true, flow: "sysd-solve" },
    },
  };
  const dv = {
    el(tag, text, options) {
      const root = new Element(tag, options);
      roots.push(root);
      return root;
    },
    page: () => config,
    pages: () => pages,
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
    workspace: {
      openLinkText: async (path) => opened.push(path),
      trigger: (event) => events.push(event),
    },
  };
  return {
    dv,
    app,
    roots,
    cleanup,
    opened,
    events,
    elements: () => roots.flatMap((p) => p.all()),
  };
}
async function mount(t, f) {
  t.after(() => f.cleanup.forEach((fn) => fn()));
  return renderDashboard(f.dv, f.app, {
    now: () => new Date(2026, 10, 17, 12),
  });
}
test("an empty due queue still shows upcoming items, with working calendar and search filters", async (t) => {
  const f = fixture([item("a"), item("b", { next_review: "2026-11-19" })]);
  await mount(t, f);
  assert.ok(
    f
      .elements()
      .some(
        (p) =>
          p.textContent === "Upcoming 2" &&
          p.attributes["aria-pressed"] === "true",
      ),
  );
  const day = f
    .elements()
    .find((p) => p.attributes["aria-label"] === "2026-11-18: 1 scheduled item");
  day.listeners.click();
  assert.ok(
    f
      .elements()
      .some((p) => p.textContent === "1 item scheduled for 2026-11-18"),
  );
  const clear = f.elements().find((p) => p.textContent === "Clear date");
  clear.listeners.click();
  const search = f
    .elements()
    .find((p) => p.attributes["aria-label"] === "Search review items");
  search.value = "review b";
  search.listeners.input();
  assert.ok(f.elements().some((p) => p.textContent === "Upcoming 1"));
  assert.equal(f.elements().filter((p) => p.cls === "pr-item-link").length, 1);
  assert.equal(
    f.elements().find((p) => p.cls === "pr-item-link").textContent,
    "Review b",
  );
});
test("the paged item list and navigation never write or record a practice attempt", async (t) => {
  const f = fixture(
    Array.from({ length: 23 }, (_, i) =>
      item("item-" + String(i).padStart(2, "0")),
    ),
  );
  await mount(t, f);
  assert.equal(f.elements().filter((p) => p.cls === "pr-item-link").length, 20);
  f.elements()
    .find((p) => p.tag === "button" && p.textContent === "Next")
    .listeners.click();
  assert.equal(f.elements().filter((p) => p.cls === "pr-item-link").length, 3);
  let stopped = false;
  await f
    .elements()
    .find((p) => p.cls === "pr-item-link")
    .listeners.click({
      preventDefault() {},
      stopPropagation() {
        stopped = true;
      },
    });
  assert.equal(stopped, true);
  assert.deepEqual(f.opened, ["Learning/Practice/Review/Items/item-20.md"]);
  assert.equal(f.events.length, 0);
});
test("paused or misconfigured modules do not query learner records", async () => {
  for (const options of [{ enabled: false }, { intervals: [0] }]) {
    const f = fixture([], options);
    f.dv.pages = () => {
      throw new Error("must not read");
    };
    renderDashboard(f.dv, f.app);
    assert.ok(
      f
        .elements()
        .some((p) => /paused|valid configuration/.test(p.textContent)),
    );
  }
});
test("the dashboard executes in the isolated Dataview scope without plugin imports", async (t) => {
  const f = fixture([item("a")]);
  t.after(() => f.cleanup.forEach((fn) => fn()));
  const source = fs.readFileSync(__dirname + "/view.js", "utf8");
  await vm.runInNewContext(
    "(async function(dv,input){" + source + "})(dv,input)",
    { dv: f.dv, input: { app: f.app }, Date, setTimeout, clearTimeout },
  );
  assert.ok(f.elements().some((p) => p.textContent === "Practice Review"));
  assert.equal(f.elements().filter((p) => p.cls === "pr-item-link").length, 1);
  assert.equal(
    f
      .elements()
      .some((p) => p.textContent.startsWith("Practice Review could not load")),
    false,
  );
});

const ATTEMPTS = JSON.parse(
  fs.readFileSync(__dirname + "/fixtures/review-attempts.json", "utf8"),
);
test("each stored attempt shows its stage, date and unmet criteria as recorded", () => {
  ATTEMPTS.attempts.forEach((step, index) => {
    const snapshot = buildSnapshot(
      [
        item("design", {
          domain: "system-design",
          status: step.status,
          review_count: index + 1,
          stage: step.stage,
          last_review: step.date,
          next_review: step.next_review,
          last_result: step.unmet.length ? "failed" : "passed",
          unmet_criteria: step.unmet,
        }),
      ],
      step.date,
      ATTEMPTS.schedule.intervals,
    );
    const shown = snapshot.items[0];
    assert.deepEqual(
      [shown.stage, shown.nextReview, shown.status, shown.unmet, shown.issues],
      [step.stage, step.next_review, step.status, step.unmet, []],
    );
    assert.equal(
      shown.bucket,
      step.status === "archived" ? "archived" : "upcoming",
    );
  });
  const top = buildSnapshot(
    [item("top", { stage: 6 }), item("above", { stage: 7 })],
    TODAY,
    ATTEMPTS.schedule.intervals,
  );
  assert.deepEqual(
    top.items.map((p) => [p.id, p.stage]),
    [
      ["above", null],
      ["top", 6],
    ],
  );
  assert.deepEqual(
    top.stages.map((p) => [p.stage, p.days, p.count]),
    [
      [0, null, 0],
      [1, 1, 0],
      [2, 3, 0],
      [3, 7, 0],
      [4, 14, 0],
      [5, 30, 0],
      [6, 60, 1],
    ],
  );
});
test("the item list groups modules and shows each failed item's unmet criteria", async (t) => {
  const f = fixture(
    [
      item("design", {
        domain: "system-design",
        stage: 2,
        next_review: TODAY,
        last_result: "failed",
        unmet_criteria: ["no_substantive_help", "within_time_limit"],
      }),
      item("algo", { next_review: "2026-11-16" }),
      item("algo-2", { next_review: TODAY, last_result: undefined }),
    ],
    { intervals: ATTEMPTS.schedule.intervals },
  );
  await mount(t, f);
  const groups = f
    .elements()
    .filter((p) => p.attributes.scope === "colgroup")
    .map((p) => p.textContent);
  assert.deepEqual(groups, ["Algorithm · 2", "System Design · 1"]);
  assert.deepEqual(
    f
      .elements()
      .filter((p) => p.cls === "pr-item-link")
      .map((p) => p.textContent),
    ["Review algo", "Review algo-2", "Review design"],
  );
  const text = f.elements().map((p) => p.textContent);
  assert.ok(text.includes("Not met: no substantive help, within time limit"));
  assert.ok(text.includes("2 of 6"));
  assert.ok(text.includes("No recorded result"));
  assert.ok(text.includes("Passed"));
  assert.ok(!text.some((p) => /Round|Guided|Mock/.test(p)));
});

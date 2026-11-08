const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const assert = require('node:assert/strict');

const home = readFileSync(join(__dirname, '..', 'Home.md'), 'utf8');
const logic = home.slice(home.indexOf('  let dragged = null;'), home.indexOf('  root.createEl("div", {\n    text: "拖动'));
assert.ok(logic.includes('async function moveTask'));
const handleCode = home.slice(home.indexOf('      if (d) {\n        const handle'), home.indexOf('      // Click a task'));
const dropCode = home.slice(home.indexOf('    cell.setAttribute("data-quadrant"'), home.indexOf('    const head = cell.createEl', home.indexOf('    cell.setAttribute("data-quadrant"')));

// A fixed calendar isolates tests from the wall clock and the host timezone.
function date(value) {
  const ms = Date.parse((value === 'today' ? '2026-11-08' : value) + 'T00:00:00Z');
  return {
    isValid: Number.isFinite(ms),
    valueOf: () => ms,
    plus: ({ days }) => date(new Date(ms + days * 86400000).toISOString().slice(0, 10)),
    endOf: () => ({ valueOf: () => ms + 86399999 }),
    toFormat: () => new Date(ms).toISOString().slice(0, 10),
  };
}
function fixture(initial = '') {
  let content = initial;
  const notices = [], refreshes = [];
  const bfile = {};
  const app = {
    vault: { process: async (file, change) => { assert.equal(file, bfile); content = change(content); } },
    workspace: { trigger: event => refreshes.push(event) },
  };
  const document = {};
  // Keep the undo button reachable just as it is in the rendered Notice.
  document.createDocumentFragment = () => {
    const fragment = { createSpan() {}, createEl() {
      fragment.button = { addEventListener(event, callback) { this[event] = callback; } };
      return fragment.button;
    } };
    return fragment;
  };
  class Notice {
    constructor(message) { this.message = message; notices.push(this); }
    hide() { this.hidden = true; }
  }
  const api = new Function('app', 'dv', 'bfile', 'Notice', 'document', logic + `
    return { moveLine, taskInSection, moveTask,
      bindHandle(t, li) { const d = 'work'; ${handleCode} },
      bindDrop(cell, q) { ${dropCode} }
    };`)(app, { date }, bfile, Notice, document);
  return { ...api, notices, refreshes, read: () => content, replace: value => { content = value; } };
}

test('all four quadrant destinations update importance and urgency', () => {
  const { moveLine } = fixture();
  const raw = '- [ ] Prepare [[Story Bank]] #task/work';
  assert.equal(moveLine(raw, 'Q1'), '- [ ] ⭐ Prepare [[Story Bank]] #task/work 📅 2026-11-15');
  assert.equal(moveLine(raw, 'Q2'), '- [ ] ⭐ Prepare [[Story Bank]] #task/work');
  assert.equal(moveLine('- [ ] ⭐ Prepare [[Story Bank]] #task/work', 'Q3'), raw + ' 📅 2026-11-15');
  assert.equal(moveLine('- [ ] ⭐ 📅 2026-11-09 Prepare [[Story Bank]] #task/work', 'Q4'), raw);
});

test('urgent dates include overdue and day seven; day eight is nonurgent', () => {
  const { moveLine } = fixture();
  for (const day of ['2026-10-01', '2026-11-15']) {
    const raw = `- [ ] 📅 ${day} Story #task/work`;
    assert.equal(moveLine(raw, 'Q3'), raw);
    assert.equal(moveLine(raw, 'Q4'), '- [ ] Story #task/work');
  }
  const later = '- [ ] Story #task/work 📅 2026-11-16';
  assert.equal(moveLine(later, 'Q2'), '- [ ] ⭐ Story #task/work 📅 2026-11-16');
  assert.equal(moveLine(later, 'Q3'), '- [ ] Story #task/work 📅 2026-11-15');
});

test('inline due formats work and unrelated dates, links, indentation survive', () => {
  const { moveLine } = fixture();
  for (const token of ['[due:: 2026-11-09]', '(due:: 2026-11-09)', '📅 2026-11-09']) {
    const raw = `  - [ ] ${token} Story [[2026-11-09]] [start:: 2026-11-01] #task/custom`;
    assert.equal(moveLine(raw, 'Q2'), '  - [ ] ⭐ Story [[2026-11-09]] [start:: 2026-11-01] #task/custom');
  }
  assert.equal(moveLine('- [ ] Story #task/work\r', 'Q1'), '- [ ] ⭐ Story #task/work 📅 2026-11-15\r');
});

test('ambiguous dates and unclassified tasks fail without rewriting', () => {
  const { moveLine } = fixture();
  for (const raw of [
    '- [ ] Story',
    '- [ ] Story #task/work [due:: tomorrow]',
    '- [ ] Story #task/work 📅 tomorrow',
    '- [ ] Story #task/work 📅 2026-11-09 [due:: 2026-11-10]',
  ]) assert.throws(() => moveLine(raw, 'Q1'));
});

test('section checks reject code fences, Done, and completed tasks', () => {
  const { taskInSection } = fixture();
  const lines = ['# Board', '```md', '## Tasks', '- [ ] Fake', '```', '## Tasks', '- [ ] Real', '- [x] Done', '~~~', '- [ ] Fake', '~~~', '## Done', '- [ ] Old'];
  assert.equal(taskInSection(lines, 6), true);
  for (const i of [3, 7, 9, 12]) assert.equal(taskInSection(lines, i), false);
});

test('move persists one line and undo restores the exact original', async () => {
  const raw = '- [ ] Prepare [[Story Bank]] #task/work';
  const initial = `## Tasks\n${raw}\n- [ ] Another #task/life\n## Done\n`;
  const f = fixture(initial);
  await f.moveTask({ line: 1, text: raw.slice(6) }, 'Q1');
  assert.equal(f.read(), initial.replace(raw, '- [ ] ⭐ Prepare [[Story Bank]] #task/work 📅 2026-11-15'));
  assert.equal(f.refreshes.length, 1);
  await f.notices[0].message.button.click();
  assert.equal(f.read(), initial);
  assert.equal(f.refreshes.length, 2);
});

test('stale task positions and completed tasks cannot overwrite current content', async () => {
  for (const content of ['## Tasks\n- [ ] Changed #task/work\n', '## Tasks\n- [x] Original #task/work\n', '## Done\n- [ ] Original #task/work\n']) {
    const f = fixture(content);
    await f.moveTask({ line: 1, text: 'Original #task/work' }, 'Q1');
    assert.equal(f.read(), content);
    assert.equal(typeof f.notices[0].message, 'string');
    assert.equal(f.refreshes.length, 0);
  }
});

test('undo refuses a concurrent edit', async () => {
  const f = fixture('## Tasks\n- [ ] Original #task/work\n');
  await f.moveTask({ line: 1, text: 'Original #task/work' }, 'Q1');
  const edited = f.read().replace('Original', 'Edited');
  f.replace(edited);
  await f.notices[0].message.button.click();
  assert.equal(f.read(), edited);
  assert.match(f.notices[1].message, /任务已再次变化/);
});

test('drag events persist the destination, clear highlights, and ignore external drops', async () => {
  const f = fixture('## Tasks\n- [ ] Story #task/work\n');
  const element = () => ({
    style: {}, children: [], listeners: {},
    setAttribute() {}, contains: () => false,
    addEventListener(name, callback) { this.listeners[name] = callback; },
    createEl() { const child = element(); this.children.push(child); return child; },
  });
  const row = element(), cell = element();
  f.bindHandle({ line: 1, text: 'Story #task/work' }, row);
  f.bindDrop(cell, { id: 'Q1' });
  const event = {
    prevented: false, preventDefault() { this.prevented = true; }, stopPropagation() {},
    dataTransfer: { setData() {} },
  };
  // Text dragged from elsewhere has no local task identity.
  cell.listeners.drop(event);
  assert.equal(event.prevented, false);
  assert.equal(f.read(), '## Tasks\n- [ ] Story #task/work\n');
  const handle = row.children[0];
  assert.equal(handle.draggable, true);
  handle.listeners.dragstart(event);
  cell.listeners.dragover(event);
  assert.equal(event.dataTransfer.dropEffect, 'move');
  assert.match(cell.style.outline, /2px solid/);
  cell.listeners.drop(event);
  handle.listeners.dragend();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(f.read(), '## Tasks\n- [ ] ⭐ Story #task/work 📅 2026-11-15\n');
  assert.equal(cell.style.outline, '');
  assert.equal(row.style.opacity, '');
});

test('all Home Dataview scripts parse', () => {
  const blocks = [...home.matchAll(/^```dataviewjs\n([\s\S]*?)^```/gm)];
  assert.ok(blocks.length > 0);
  const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
  for (const [, source] of blocks) new AsyncFunction(source);
});

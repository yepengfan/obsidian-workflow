const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { enabled, localDay, validDay, dayPath, parseDaily, snapshot, initialize, launch, renderJournal } = require('./view.js');
const dailyTemplate = fs.readFileSync('Templates/Journal Daily.md', 'utf8');
const reviewTemplate = fs.readFileSync('Templates/Journal Review.md', 'utf8');

function fixture({ active = true, configured = true } = {}) {
  const files = new Map();
  const events = new Map();
  const callbacks = [];
  let sends = 0, creates = 0;
  const put = (path, text, extension = 'md') => files.set(path, { path, text, extension });
  put('system/modules/journal/module.md', `---\nenabled: ${active}\n---\n`);
  put('Templates/Journal Daily.md', dailyTemplate);
  put('Templates/Journal Review.md', reviewTemplate);
  const view = {
    running: false,
    newChat() { plugin.activeConversationId = `chat-${++creates}`; plugin.conversations.push({ id: plugin.activeConversationId }); },
    sendMessage(text) { sends++; view.prompt = text; },
    async openConversation(id) { plugin.activeConversationId = id; }, focus() {},
  };
  const plugin = {
    conversations: [], activeConversationId: 'other', activeConversation: { chatHistory: ['existing chat'] },
    async openChat() { return configured ? view : null; },
    listConversations() { return plugin.conversations; },
  };
  const vault = {
    getName: () => 'test-vault',
    getAbstractFileByPath: path => files.get(path),
    getMarkdownFiles: () => [...files.values()].filter(f => f.extension === 'md'),
    read: async file => file.text,
    async createFolder(path) { if (files.has(path)) throw new Error('exists'); files.set(path, { path }); },
    async create(path, text) { if (files.has(path)) throw new Error('exists'); put(path, text); return files.get(path); },
    on(name, callback) { const ref = { name, callback }; events.set(ref, ref); return ref; },
  };
  const app = { vault, plugins: { getPlugin: () => plugin }, workspace: { openLinkText: async path => { app.opened = path; } } };
  const storageMap = new Map();
  const storage = { getItem: key => storageMap.get(key), setItem: (key, value) => storageMap.set(key, value) };
  const dv = { el: tag => new Element(tag), component: { register: fn => callbacks.push(fn), registerEvent: ref => callbacks.push(() => events.delete(ref)) } };
  return { app, files, put, plugin, view, storage, events, dv, callbacks, count: () => ({ sends, creates }) };
}
class Element {
  constructor(tag, options = {}) { this.tag = tag; this.children = []; this.listeners = {}; this.textContent = options.text ?? ''; this.cls = options.cls; this.attributes = options.attr ?? {}; this.disabled = false; }
  createEl(tag, options) { const el = new Element(tag, options); this.children.push(el); return el; }
  addEventListener(name, callback) { this.listeners[name] = callback; }
  empty() { this.children = []; }
  all() { return [this, ...this.children.flatMap(child => child.all())]; }
}

test('enabled flag is read only from frontmatter and fails closed', () => {
  assert.equal(enabled('---\nenabled: true\n---\n'), true);
  assert.equal(enabled('---\nenabled: false\n---\nenabled: true'), false);
  assert.equal(enabled('enabled: true'), false);
});
test('local calendar dates survive leap days, midnight and DST windows', () => {
  assert.equal(validDay('2024-02-29'), true);
  assert.equal(validDay('2026-02-29'), false);
  assert.equal(validDay('2026-13-01'), false);
  assert.throws(() => dayPath('../oops'));
  assert.equal(localDay(new Date(2026, 0, 1, 0, 1)), '2026-01-01');
  const result = snapshot([], new Date(2026, 2, 10, 0, 1));
  assert.deepEqual(result.recent.map(d => d.day), ['2026-03-04','2026-03-05','2026-03-06','2026-03-07','2026-03-08','2026-03-09','2026-03-10']);
});
test('empty templates do not count; real source, AAR or later result does', () => {
  const path = 'Journal/Daily/2026-11-09.md';
  assert.equal(parseDaily(path, dailyTemplate).recorded, false);
  for (const section of ['原始记录','AAR 整理','后续补充']) assert.equal(parseDaily(path, `## ${section}\n演练尚未完成。`).recorded, true);
  assert.equal(parseDaily(path, '## AAR 整理\n### 事件\n- \n**实际行动与结果：**\n').recorded, false);
  assert.equal(parseDaily(path, '## 原始记录\n<!-- journal-session: test -->\n<!-- /journal-session: test -->').recorded, false);
  assert.equal(parseDaily('Inbox/Journal Mobile Verification.md', '## 原始记录\n测试'), null);
});
test('pending checklist excludes completed items, other sections and fenced examples', () => {
  const note = parseDaily('Journal/Daily/2026-11-09.md', '## 原始记录\n- [ ] unrelated\n## 想再回看的事\n- [ ] 等演练结果\n- [x] 已完成\n```md\n- [ ] 仅示例\n## 原始记录\n```\n- [ ] 看看尝试是否有效\n## 后续补充\n- [ ] unrelated');
  assert.deepEqual(note.pending.map(p => p.text), ['等演练结果','看看尝试是否有效']);
});
test('overview counts recorded days across total, month and seven-day windows, including old pending', () => {
  const notes = [
    {path:'Journal/Daily/2026-11-09.md',text:'## 原始记录\n今天的决定'},
    {path:'Journal/Daily/2026-11-08.md',text:dailyTemplate},
    {path:'Journal/Daily/2026-10-01.md',text:'## 想再回看的事\n- [ ] 还在等结果'},
    {path:'Journal/Daily/nope.md',text:'## 原始记录\n不计'},
  ];
  const result = snapshot(notes, new Date(2026,10,9));
  assert.equal(result.monthCount, 1); assert.equal(result.pending.length,1);
  assert.equal(result.recent.at(-1).recorded,true); assert.equal(result.recent.at(-2).recorded,false);
  assert.equal(result.totalCount,1); assert.equal(result.weekCount,1);
});
test('initialization is concurrent-safe and preserves existing user content', async () => {
  const f = fixture();
  await Promise.all([initialize(f.app,'2026-11-09'), initialize(f.app,'2026-11-09')]);
  const path = dayPath('2026-11-09');
  assert.match(f.files.get(path).text, /date: "2026-11-09"/);
  assert.match(f.files.get(path).text, /# Monday/);
  f.put(path, '用户已经手写的内容');
  await initialize(f.app,'2026-11-09');
  assert.equal(f.files.get(path).text,'用户已经手写的内容');
});
test('button flow initializes before AI, sends once and resumes same-day conversation', async () => {
  const f = fixture();
  const open = f.plugin.openChat;
  f.plugin.openChat = async () => { assert.ok(f.files.has(dayPath('2026-11-09'))); return open(); };
  const options = { now: new Date(2026,10,9,20),storage:f.storage };
  const first = await launch(f.app,options);
  assert.equal(first.resumed,false);
  assert.match(f.view.prompt,/Journal\/Guide.md/);
  assert.match(f.view.prompt,/目标 Journal\/Daily\/2026-11-09.md/);
  assert.equal((await launch(f.app,options)).resumed,true);
  assert.deepEqual(f.count(),{sends:1,creates:1});
  assert.equal((await launch(f.app,{...options,now:new Date(2026,10,10)})).resumed,false);
  assert.deepEqual(f.count(),{sends:2,creates:2});
});
test('concurrent launches do not start duplicate chats', async () => {
  const f = fixture();
  const results = await Promise.all([launch(f.app,{storage:f.storage}),launch(f.app,{storage:f.storage})]);
  assert.equal(results.filter(r=>r.busy).length,1);
  assert.equal(f.count().sends,1);
});
test('disabled module has no writes; missing auth or APIs retains templates and offers prompt', async () => {
  const off = fixture({active:false});
  assert.match((await launch(off.app,{storage:off.storage})).error,/停用/);
  assert.equal(off.files.has('Journal/Review.md'),false);
  const noAuth = fixture({configured:false});
  const result = await launch(noAuth.app,{storage:noAuth.storage});
  assert.match(result.error,/登录/); assert.ok(noAuth.files.has(result.path)); assert.ok(result.prompt);
  assert.equal(noAuth.count().sends,0);
  const noApi = fixture(); delete noApi.plugin.openChat;
  const missing = await launch(noApi.app,{storage:noApi.storage});
  assert.match(missing.error,/入口已变化/); assert.ok(missing.prompt);
});
test('deleted conversation starts fresh and unavailable storage still permits continuation', async () => {
  const f = fixture(); const storage = {getItem(){throw Error('unavailable');},setItem(){throw Error('unavailable');}};
  const opts = {now:new Date(2026,10,9),storage};
  await launch(f.app,opts); assert.equal((await launch(f.app,opts)).resumed,true);
  f.plugin.conversations=[];
  assert.equal((await launch(f.app,opts)).resumed,false);
  assert.equal(f.count().sends,2);
});
test('view refreshes after data writes and unregisters listeners on unload', async t => {
  const f = fixture(); let root;
  t.after(() => f.callbacks.forEach(fn => fn()));
  f.dv.el = tag => (root = new Element(tag));
  await renderJournal(f.dv,f.app);
  assert.ok(root.all().some(el=>el.textContent==='0'));
  f.put('Journal/Daily/2020-11-09.md','## 原始记录\n先确认顾虑，再提议验证');
  // Uses the current month so this check is independent of the day the test runs.
  f.put(`Journal/Daily/${localDay()}.md`,'## 原始记录\n今天的观察\n## 想再回看的事\n- [ ] 等演练结果');
  for(const {name,callback} of f.events.values()) if(name==='modify')callback({path:`Journal/Daily/${localDay()}.md`});
  await new Promise(resolve=>setTimeout(resolve,200));
  assert.ok(root.all().some(el=>el.textContent==='等演练结果'));
  assert.ok(root.all().some(el=>el.textContent==='待回看 1'));
  f.callbacks.forEach(fn=>fn());
  assert.equal(f.events.size,0);
});

test('Dataview custom-view entry runs in its async dv/input environment', async t => {
  const f = fixture(); let root;
  f.dv.el = tag => (root = new Element(tag));
  t.after(() => f.callbacks.forEach(fn => fn()));
  const AsyncFunction = Object.getPrototypeOf(async function() {}).constructor;
  const execute = new AsyncFunction('dv','input',fs.readFileSync('scripts/journal/view.js','utf8'));
  await execute(f.dv,{app:f.app});
  assert.ok(root.all().some(el=>el.attributes['aria-current']==='date'));
});

test('cleared same-day chat starts the journal prompt again', async () => {
  const f = fixture(); const opts = { now: new Date(2026,10,9),storage:f.storage };
  await launch(f.app,opts);
  f.plugin.activeConversation.chatHistory=[];
  assert.equal((await launch(f.app,opts)).resumed,false);
  assert.equal(f.count().sends,2);
});

function lifecycle() {
  const listeners = new Map();
  return {
    hidden: false,
    addEventListener(name, fn) { listeners.set(name, fn); },
    removeEventListener(name, fn) { if (listeners.get(name) === fn) listeners.delete(name); },
    fire(name) { listeners.get(name)?.(); },
    size: () => listeners.size,
  };
}
const settle = () => new Promise(resolve => setImmediate(resolve));
async function mount(t, f, options = {}) {
  let root;
  f.dv.el = tag => (root = new Element(tag));
  t.after(() => f.callbacks.forEach(fn => fn()));
  await renderJournal(f.dv, f.app, options);
  return () => root.all();
}
test('compact view exposes date entry, check-ins and folded followups without record content', async t => {
  const f = fixture();
  f.put('Journal/Daily/2026-11-09.md', '## 原始记录\nPRIVATE DAILY CONTENT');
  f.put('Journal/Daily/2026-11-08.md', '## AAR 整理\nPRIVATE AAR CONTENT\n## 想再回看的事\n- [ ] 等待验证');
  f.put('Journal/Review.md','## 当前理解\nPRIVATE REVIEW CONTENT');
  const elements = await mount(t,f,{now:()=>new Date(2026,10,9)});
  const buttons = elements().filter(el=>el.tag==='button');
  assert.equal(buttons.length,7);
  assert.deepEqual(buttons.find(el=>el.attributes['aria-current']==='date').children.map(el=>el.textContent),['今天','11/09']);
  assert.equal(buttons.filter(el=>el.disabled).length,5);
  assert.ok(elements().some(el=>el.textContent==='2026-11-09 周一'));
  assert.ok(elements().some(el=>el.tag==='details' && !el.open));
  assert.equal(elements().some(el=>el.textContent.includes('PRIVATE')),false);
  assert.deepEqual(elements().filter(el=>el.cls==='journal-number').map(el=>el.children[0].textContent),['2','2','2']);
  await buttons.find(el=>el.textContent==='11/08').listeners.click();
  assert.equal(f.app.opened,'Journal/Daily/2026-11-08.md');
  assert.equal(f.count().sends,0);
  await buttons.find(el=>el.attributes['aria-current']==='date').listeners.click();
  assert.equal(f.count().sends,1);
  assert.match(f.view.prompt,/目标 Journal\/Daily\/2026-11-09.md/);
});
test('foreground return refreshes local year/day and listener cleanup prevents further updates', async t => {
  const f = fixture(), page = lifecycle(), win = lifecycle();
  let clock = new Date(2026,11,31,23,59);
  const elements = await mount(t,f,{now:()=>clock,page,window:win});
  assert.ok(elements().some(el=>el.cls==='journal-today-date' && el.textContent==='12/31'));
  clock = new Date(2027,0,1,0,1);
  page.hidden = true; page.fire('visibilitychange'); await settle();
  assert.ok(elements().some(el=>el.cls==='journal-today-date' && el.textContent==='12/31'));
  page.hidden = false; page.fire('visibilitychange'); await settle();
  assert.ok(elements().some(el=>el.cls==='journal-today-date' && el.textContent==='01/01'));
  assert.ok(elements().some(el=>el.textContent==='2027-01-01 周五'));
  clock = new Date(2027,0,2); win.fire('focus'); await settle();
  assert.ok(elements().some(el=>el.cls==='journal-today-date' && el.textContent==='01/02'));
  f.callbacks.forEach(fn=>fn());
  assert.equal(page.size(),0); assert.equal(win.size(),0);
});
test('stale today button resolves the current date at click time after midnight', async t => {
  const f = fixture(); let clock = new Date(2026,11,31,23,59);
  const elements = await mount(t,f,{now:()=>clock});
  const today = elements().find(el=>el.attributes['aria-current']==='date');
  clock = new Date(2027,0,1,0,1);
  await today.listeners.click();
  assert.match(f.view.prompt,/目标 Journal\/Daily\/2027-01-01.md/);
  assert.equal(f.files.has('Journal/Daily/2026-12-31.md'),false);
  assert.ok(elements().some(el=>el.cls==='journal-today-date' && el.textContent==='01/01'));
});
test('midnight timer rolls visible dates without a file or focus event', async t => {
  t.mock.timers.enable({apis:['setTimeout']});
  const f = fixture(); let clock = new Date(2026,11,31,23,59,59);
  const elements = await mount(t,f,{now:()=>clock});
  clock = new Date(2027,0,1,0,0,1);
  t.mock.timers.tick(2000); await settle();
  assert.ok(elements().some(el=>el.cls==='journal-today-date' && el.textContent==='01/01'));
});

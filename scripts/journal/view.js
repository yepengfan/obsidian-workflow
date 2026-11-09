// Dataview custom view. Pure parsing and launch functions are also exported for Node tests.
const DAILY_ROOT = "Journal/Daily/";
const REVIEW_PATH = "Journal/Review.md";
const MODULE_PATH = "system/modules/journal/module.md";
const SECTIONS = ["原始记录", "AAR 整理", "后续补充"];

function scalar(text, key) {
  const fm = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/.exec(text)?.[1] ?? "";
  const value = fm.split(/\r?\n/).find(line => line.startsWith(`${key}:`))?.slice(key.length + 1).trim() ?? "";
  return value.replace(/^(["'])(.*)\1$/, "$2");
}
function enabled(text) { return scalar(text, "enabled") === "true"; }
function localDay(date = new Date()) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}
function validDay(day) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) return false;
  const date = new Date(`${day}T12:00:00`);
  return Number.isFinite(date.getTime()) && localDay(date) === day;
}
function dayPath(day) {
  if (!validDay(day)) throw new Error("Journal 日期无效");
  return `${DAILY_ROOT}${day}.md`;
}
function sections(text) {
  const result = {};
  let current = "", fence = null;
  for (const line of text.replace(/<!--[\s\S]*?-->/g, "").split(/\r?\n/)) {
    const marker = /^\s{0,3}(`{3,}|~{3,})/.exec(line)?.[1];
    if (marker) {
      if (!fence) fence = marker;
      else if (marker[0] === fence[0] && marker.length >= fence.length) fence = null;
      continue;
    }
    const heading = !fence && /^## (.+?)\s*$/.exec(line);
    if (heading) { current = heading[1]; result[current] ??= []; continue; }
    if (current && !(fence && current === "想再回看的事")) result[current].push(line);
  }
  return result;
}
function meaningful(lines = []) {
  return lines.some(line => {
    const plain = line.trim().replace(/\*\*/g, "");
    if (!plain || /^(?:原本希望怎样|实际发生什么|为什么|下次保留或改变什么|目标与情境|实际行动与结果|当时判断|保留\/改变\/待观察)[？?：:]*$/.test(plain)) return false;
    return !/^\s*(?:#{1,6}\s|>\s*\[!|[-*+]\s*(?:\[[ xX]\])?\s*$)/.test(line);
  });
}
function displayText(text) {
  return text.replace(/\[\[([^|\]]+)(?:\|([^\]]+))?\]\]/g, (_, target, alias) => alias ?? target.split("/").pop()).replace(/[*`]/g, "");
}
function summary(lines = [], limit = 110) {
  const line = lines.map(s => s.replace(/^\s*(?:#{1,6}\s+|[-*+]\s+(?:\[[ xX]\]\s*)?)/, "").trim())
    .find(s => s && !s.startsWith("> [!")) ?? "";
  const clean = displayText(line);
  return clean.length > limit ? `${clean.slice(0, limit)}…` : clean;
}
function parseDaily(path, text) {
  const day = path.startsWith(DAILY_ROOT) ? path.slice(DAILY_ROOT.length).replace(/\.md$/, "") : "";
  if (!validDay(day) || path !== dayPath(day)) return null;
  const parts = sections(text);
  const pending = (parts["想再回看的事"] ?? []).flatMap(line => {
    const match = /^\s*[-*+] \[ \] (.+)/.exec(line);
    return match ? [{ path, text: match[1].trim() }] : [];
  });
  return { path, day, recorded: SECTIONS.some(key => meaningful(parts[key])), pending,
    summary: summary(parts["AAR 整理"]) || summary(parts["原始记录"]) || summary(parts["后续补充"]) };
}
function snapshot(notes, review, now = new Date()) {
  const today = localDay(now);
  const daily = notes.map(note => parseDaily(note.path, note.text)).filter(Boolean).sort((a, b) => b.day.localeCompare(a.day));
  const recent = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 6 + i, 12);
    const day = localDay(date);
    return { day, recorded: daily.some(note => note.day === day && note.recorded) };
  });
  return { daily, recent, monthCount: daily.filter(note => note.recorded && note.day.startsWith(today.slice(0, 7))).length,
    pending: daily.flatMap(note => note.pending), lastReflected: scalar(review, "last_reflected"),
    reviewSummary: summary(sections(review)["当前理解"]) || summary(sections(review)["近期经历"]) };
}
async function read(app, path) {
  const file = app.vault.getAbstractFileByPath(path);
  if (!file || typeof file.extension !== "string") throw new Error(`文件尚未同步或不存在：${path}`);
  return app.vault.read(file);
}
async function ensureFolder(app, path) {
  for (const segment of path.split("/").reduce((all, part) => [...all, all.length ? `${all[all.length - 1]}/${part}` : part], [])) {
    if (app.vault.getAbstractFileByPath(segment)) continue;
    try { await app.vault.createFolder(segment); }
    catch (error) { if (!app.vault.getAbstractFileByPath(segment)) throw error; }
  }
}
async function createIfMissing(app, path, content) {
  const existing = app.vault.getAbstractFileByPath(path);
  if (existing) return existing;
  await ensureFolder(app, path.slice(0, path.lastIndexOf("/")));
  try { return await app.vault.create(path, content); }
  catch (error) {
    const raced = app.vault.getAbstractFileByPath(path);
    if (!raced) throw error;
    return raced;
  }
}
async function initialize(app, day) {
  const path = dayPath(day);
  const dailyTemplate = await read(app, "Templates/Journal Daily.md");
  const reviewTemplate = await read(app, "Templates/Journal Review.md");
  const date = new Date(`${day}T12:00:00`);
  const name = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][date.getDay()];
  await createIfMissing(app, path, dailyTemplate.replaceAll("{{date}}", day).replaceAll("{{day}}", name));
  await createIfMissing(app, REVIEW_PATH, reviewTemplate);
  return path;
}
function promptFor(day, path, session) {
  return `开始每天固定的 Journal 流程。日期 ${day}，目标 ${path}，session 标识 ${session}。当天模板已准备，存在内容则继续，禁止覆盖初始化。先读取 ${MODULE_PATH}，仅 enabled: true 时继续；再读取 Journal/Guide.md 并遵循其中七步：回看之前、记录今天、AAR 反思、收尾保存并核对。没有 weekly 模式。只读取 Guide 允许的资料，只修改涉及的 Journal 数据笔记，不修改 Home、Guide、模板或插件设置。用户说“今天到这”等结束信号后，保存原话与 AAR，更新滚动 Review 和待回看原项；全部核对成功后更新 last_reflected。现在读取资料并简短开场。`;
}
const stateSymbol = Symbol.for("workspace.journal.launches");
const launchStates = globalThis[stateSymbol] ??= new WeakMap();
function stateFor(app) {
  if (!launchStates.has(app)) launchStates.set(app, { launching: false, chats: new Map() });
  return launchStates.get(app);
}
async function launch(app, { now = new Date(), storage = globalThis.localStorage } = {}) {
  const state = stateFor(app);
  if (state.launching) return { busy: true };
  state.launching = true;
  let path, prompt;
  try {
    if (!enabled(await read(app, MODULE_PATH))) throw new Error("Journal 模块已停用，请通过 /module-toggle journal 启用");
    const day = localDay(now);
    path = await initialize(app, day);
    const plugin = app.plugins.getPlugin("chatting-with-ai");
    const key = `workspace-journal:${app.vault.getName()}:${day}`;
    let remembered = state.chats.get(day);
    try { remembered ??= storage?.getItem(key); } catch { /* Session memory still works without storage. */ }
    const session = `${day}-${globalThis.crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2)}`;
    prompt = promptFor(day, path, session);
    if (typeof plugin?.openChat !== "function") throw new Error("Chatting with AI 未启用或入口已变化，请打开插件并复制下方指令");
    const view = await plugin.openChat();
    if (!view) throw new Error("请先在 Chatting with AI 中完成登录，再重试；今天的模板已保留");
    if (remembered && plugin.listConversations?.().some(chat => chat.id === remembered) && typeof view.openConversation === "function") {
      await view.openConversation(remembered);
      if (plugin.activeConversationId === remembered && (plugin.activeConversation?.chatHistory?.length ?? 0) > 0) {
        view.focus?.();
        return { path, resumed: true };
      }
    }
    if (typeof view.newChat !== "function" || typeof view.sendMessage !== "function") throw new Error("插件聊天接口已变化，请复制下方指令到聊天");
    const before = plugin.activeConversationId;
    const hadHistory = (plugin.activeConversation?.chatHistory?.length ?? 0) > 0;
    view.newChat();
    if ((hadHistory || view.running) && plugin.activeConversationId === before) throw new Error("插件正在处理其他操作，暂不能开启 Journal；稍后重试");
    view.sendMessage(prompt);
    state.chats.set(day, plugin.activeConversationId);
    try { storage?.setItem(key, plugin.activeConversationId); } catch { /* Local storage is optional. */ }
    return { path, resumed: false };
  } catch (error) {
    return { error: error.message ?? String(error), path, prompt };
  } finally { state.launching = false; }
}

async function renderJournal(dv, app) {
  const root = dv.el("section", "", { cls: "journal-overview" });
  const style = root.createEl("style");
  style.textContent = `.journal-overview{margin:18px 0;padding:18px;border:1px solid var(--background-modifier-border);border-radius:12px}.journal-overview *{box-sizing:border-box;min-width:0}.journal-header{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}.journal-header h2{margin:0}.journal-add{padding:8px 18px;background:var(--interactive-accent);color:var(--text-on-accent);border:0;border-radius:8px;font-weight:600;cursor:pointer;min-height:40px}.journal-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:16px 0}.journal-stat,.journal-panel{padding:12px;border:1px solid var(--background-modifier-border);border-radius:8px}.journal-stat small,.journal-muted{color:var(--text-muted)}.journal-stat strong{display:block;margin-top:5px}.journal-days{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}.journal-day{font-size:11px;min-width:24px;min-height:28px;padding:3px;border-radius:5px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-muted);cursor:pointer}.journal-day[data-recorded=true]{background:var(--interactive-accent);color:var(--text-on-accent)}.journal-columns{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.journal-panel h3{margin:0 0 10px;font-size:1em}.journal-overview a,.journal-overview p,.journal-overview li{overflow-wrap:anywhere}.journal-overview ul{padding-left:20px}.journal-status{font-size:.9em;color:var(--text-muted);margin-top:8px}.journal-overview textarea{width:100%;min-height:130px;font-size:.85em}@media(max-width:700px){.journal-stats{grid-template-columns:repeat(2,minmax(0,1fr))}.journal-columns{grid-template-columns:minmax(0,1fr)}.journal-overview{padding:12px}.journal-add{min-height:44px}}`;
  const header = root.createEl("div", { cls: "journal-header" });
  header.createEl("h2", { text: "Journal" });
  const button = header.createEl("button", { text: "+ 新增 Journal", cls: "journal-add" });
  const status = root.createEl("div", { cls: "journal-status", attr: { "aria-live": "polite" } });
  const fallback = root.createEl("div");
  const body = root.createEl("div");
  let disposed = false, version = 0, timer, recordFilter = "recent";
  const link = (parent, path, label) => {
    const a = parent.createEl("a", { text: label, attr: { href: "#" } });
    a.addEventListener("click", event => { event.preventDefault(); void app.workspace.openLinkText(path, "", false); });
  };
  button.addEventListener("click", async () => {
    if (button.disabled) return;
    button.disabled = true;
    fallback.empty();
    status.textContent = "正在准备今天的记录…";
    const result = await launch(app);
    if (disposed) return;
    button.disabled = false;
    status.textContent = result.error ?? (result.busy ? "正在打开 Journal…" : result.resumed ? "已继续今天的 AI 对话。" : "当天模板已准备，已请求 AI 开始记录。");
    if (result.error && result.path) link(fallback, result.path, "打开今天的记录");
    if (result.error && result.prompt) {
      fallback.createEl("p", { text: "可复制这段启动指令到 Chatting with AI：", cls: "journal-muted" });
      const area = fallback.createEl("textarea", { attr: { readonly: "", "aria-label": "Journal 启动指令" } });
      area.value = result.prompt;
      area.addEventListener("click", () => area.select());
    }
    await refresh();
  });
  async function refresh() {
    const current = ++version;
    try {
      const active = enabled(await read(app, MODULE_PATH));
      const files = app.vault.getMarkdownFiles().filter(file => file.path.startsWith(DAILY_ROOT));
      const notes = await Promise.all(files.map(async file => ({ path: file.path, text: await app.vault.read(file) })));
      const review = app.vault.getAbstractFileByPath(REVIEW_PATH) ? await read(app, REVIEW_PATH) : "";
      const data = snapshot(notes, review);
      if (disposed || current !== version) return;
      body.empty();
      button.disabled = !active || stateFor(app).launching;
      if (!active) { body.createEl("p", { text: "Journal 模块已停用。已有记录仍保留，可通过 /module-toggle journal 启用。", cls: "journal-muted" }); return; }
      const stats = body.createEl("div", { cls: "journal-stats" });
      const stat = title => { const card = stats.createEl("div", { cls: "journal-stat" }); card.createEl("small", { text: title }); return card; };
      const days = stat("近 7 天").createEl("div", { cls: "journal-days" });
      data.recent.forEach(day => {
        const b = days.createEl("button", { text: day.day.slice(8), cls: "journal-day", attr: { "data-recorded": String(day.recorded), "aria-label": `${day.day} ${day.recorded ? "已记录" : "未记录"}`, title: day.day } });
        b.addEventListener("click", async () => {
          b.disabled = true;
          try {
            if (!enabled(await read(app, MODULE_PATH))) throw new Error("Journal 模块已停用");
            await initialize(app, day.day);
            await app.workspace.openLinkText(dayPath(day.day), "", false);
          } catch (error) { status.textContent = error.message; }
          finally { b.disabled = false; }
        });
      });
      const monthCard = stat("本月记录");
      monthCard.createEl("strong", { text: `${data.monthCount} 天` });
      const monthLink = monthCard.createEl("a", { text: "查看本月", attr: { href: "#" } });
      monthLink.addEventListener("click", event => { event.preventDefault(); recordFilter = "month"; void refresh(); });
      const pendingCard = stat("待回看事件");
      pendingCard.createEl("strong", { text: `${data.pending.length} 件` });
      const reflected = data.lastReflected && Number.isFinite(Date.parse(data.lastReflected)) ? new Date(data.lastReflected).toLocaleString() : "尚未完成";
      const lastCard = stat("最近回看").createEl("strong");
      if (review) link(lastCard, REVIEW_PATH, reflected); else lastCard.textContent = reflected;
      const columns = body.createEl("div", { cls: "journal-columns" });
      const records = columns.createEl("div", { cls: "journal-panel" });
      records.createEl("h3", { text: recordFilter === "month" ? "本月记录" : "近期记录" });
      const written = data.daily.filter(note => note.recorded);
      if (!written.length) records.createEl("p", { text: "还没有记录，点击“新增 Journal”开始。", cls: "journal-muted" });
      function list(parent, entries) {
        const ul = parent.createEl("ul");
        entries.forEach(note => link(ul.createEl("li"), note.path, `${note.day} · ${note.summary || "打开记录"}`));
      }
      list(records, recordFilter === "month" ? written.filter(note => note.day.startsWith(localDay().slice(0, 7))) : written.slice(0, 5));
      if (recordFilter === "month") {
        const reset = records.createEl("a", { text: "返回近期记录", attr: { href: "#" } });
        reset.addEventListener("click", event => { event.preventDefault(); recordFilter = "recent"; void refresh(); });
      }
      if (written.length > 5) { const details = records.createEl("details"); details.createEl("summary", { text: `全部记录（${written.length}）` }); list(details, written); }
      const currentReview = columns.createEl("div", { cls: "journal-panel" });
      currentReview.createEl("h3", { text: "当前回顾" });
      currentReview.createEl("p", { text: data.reviewSummary || "完成一次 journal 后，AI 会在这里留下滚动回顾。", cls: data.reviewSummary ? "" : "journal-muted" });
      if (review) link(currentReview, REVIEW_PATH, "打开完整回顾");
      const pending = body.createEl("div", { cls: "journal-panel", attr: { style: "margin-top:12px" } });
      pending.createEl("h3", { text: "待回看事件" });
      const pendingLink = pendingCard.createEl("a", { text: "查看事项", attr: { href: "#" } });
      pendingLink.addEventListener("click", event => { event.preventDefault(); pending.scrollIntoView({ block: "nearest", behavior: "smooth" }); });
      if (!data.pending.length) pending.createEl("p", { text: "目前没有待回看事项。", cls: "journal-muted" });
      const ul = pending.createEl("ul");
      data.pending.forEach(item => link(ul.createEl("li"), `${item.path}#想再回看的事`, displayText(item.text)));
    } catch (error) {
      if (!disposed && current === version) { body.empty(); status.textContent = `Journal 视图未能更新：${error.message}`; }
    }
  }
  const schedule = file => {
    if (file && file.path !== MODULE_PATH && !file.path.startsWith("Journal/")) return;
    clearTimeout(timer);
    timer = setTimeout(() => { void refresh(); }, 150);
  };
  for (const event of ["create", "modify", "delete", "rename"]) {
    dv.component.registerEvent(app.vault.on(event, (file, oldPath) => {
      if (oldPath?.startsWith("Journal/")) schedule(); else schedule(file);
    }));
  }
  dv.component.register(() => { disposed = true; version++; clearTimeout(timer); });
  // Dataview file events refresh data; a local midnight timer also moves the 7-day window.
  function atMidnight() {
    const now = new Date();
    const next = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 0, 0, 1);
    const id = setTimeout(() => { if (!disposed) { void refresh(); atMidnight(); } }, next - now);
    dv.component.register(() => clearTimeout(id));
  }
  atMidnight();
  await refresh();
}

if (typeof dv === "undefined") {
  module.exports = { scalar, enabled, localDay, validDay, dayPath, sections, meaningful, parseDaily, snapshot, initialize, promptFor, launch, renderJournal };
} else {
  return renderJournal(dv, input.app);
}

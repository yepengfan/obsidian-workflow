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
function parseDaily(path, text) {
  const day = path.startsWith(DAILY_ROOT) ? path.slice(DAILY_ROOT.length).replace(/\.md$/, "") : "";
  if (!validDay(day) || path !== dayPath(day)) return null;
  const parts = sections(text);
  const pending = (parts["想再回看的事"] ?? []).flatMap(line => {
    const match = /^\s*[-*+] \[ \] (.+)/.exec(line);
    return match ? [{ path, text: match[1].trim() }] : [];
  });
  return { path, day, recorded: SECTIONS.some(key => meaningful(parts[key])), pending };
}
function snapshot(notes, now = new Date()) {
  const today = localDay(now);
  const daily = notes.map(note => parseDaily(note.path, note.text)).filter(Boolean).sort((a, b) => b.day.localeCompare(a.day));
  const recent = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 6 + i, 12);
    const day = localDay(date);
    return { day, recorded: daily.some(note => note.day === day && note.recorded) };
  });
  return { daily, recent, totalCount: daily.filter(note => note.recorded).length,
    monthCount: daily.filter(note => note.recorded && note.day.startsWith(today.slice(0, 7))).length,
    weekCount: recent.filter(day => day.recorded).length, pending: daily.flatMap(note => note.pending) };
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

async function renderJournal(dv, app, { now = () => new Date(), page = globalThis.document, window: win = globalThis.window } = {}) {
  const root = dv.el("section", "", { cls: "journal-overview" });
  const style = root.createEl("style");
  style.textContent = `.journal-overview{margin:18px 0;padding:18px;border:1px solid var(--background-modifier-border);border-radius:12px}.journal-overview *{box-sizing:border-box;min-width:0}.journal-header{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}.journal-header h2{margin:0}.journal-local-date{font-size:12px;color:var(--text-muted)}.journal-days{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0}.journal-day{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;flex:1 0 58px;min-height:56px;padding:8px;border-radius:8px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:13px;cursor:pointer}.journal-day:disabled{opacity:.4;cursor:default}.journal-day[data-recorded=true]::after{content:"";width:3px;height:3px;border-radius:50%;background:currentColor}.journal-day[aria-current=date]{flex-grow:1.6;background:var(--interactive-accent);color:var(--text-on-accent);border-color:var(--interactive-accent);font-weight:650}.journal-overview details{padding:10px 0}.journal-overview summary{cursor:pointer;font-size:14px}.journal-overview a,.journal-overview li{overflow-wrap:anywhere}.journal-overview ul{padding-left:20px}.journal-numbers{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;padding-top:14px;border-top:1px solid var(--background-modifier-border);margin-top:12px}.journal-number strong{display:block;font-size:19px;font-variant-numeric:tabular-nums}.journal-number small{font-size:11px;color:var(--text-muted)}.journal-status{font-size:13px;color:var(--text-muted);margin-top:12px}.journal-status:empty,.journal-fallback:empty{display:none}.journal-overview textarea{width:100%;min-height:130px;font-size:.85em}@media(max-width:700px){.journal-overview{padding:16px}.journal-days{gap:6px}.journal-day{flex-basis:62px}}`;
  const header = root.createEl("div", { cls: "journal-header" });
  header.createEl("h2", { text: "Journal" });
  const dateLabel = header.createEl("span", { cls: "journal-local-date" });
  const body = root.createEl("div");
  const status = root.createEl("div", { cls: "journal-status", attr: { "aria-live": "polite" } });
  const fallback = root.createEl("div", { cls: "journal-fallback" });
  let disposed = false, version = 0, timer, midnightTimer, followupsOpen = false;
  const link = (parent, path, label) => {
    const a = parent.createEl("a", { text: label, attr: { href: "#" } });
    a.addEventListener("click", event => { event.preventDefault(); void app.workspace.openLinkText(path, "", false); });
  };
  async function start(button) {
    if (button.disabled || stateFor(app).launching) return;
    button.disabled = true;
    fallback.empty();
    status.textContent = "正在准备今天的记录…";
    // Resolve the local date at click time, even if the screen slept through midnight.
    const result = await launch(app, { now: now() });
    if (disposed) return;
    button.disabled = false;
    status.textContent = result.error ?? (result.busy ? "正在打开 Journal…" : result.resumed ? "已继续今天的 AI 对话。" : "当天模板已准备，已请求 AI 开始记录。");
    if (result.error && result.path) link(fallback, result.path, "打开今天的记录");
    if (result.error && result.prompt) {
      fallback.createEl("p", { text: "可复制这段启动指令到 Chatting with AI：" });
      const area = fallback.createEl("textarea", { attr: { readonly: "", "aria-label": "Journal 启动指令" } });
      area.value = result.prompt;
      area.addEventListener("click", () => area.select());
    }
    await refresh();
  }
  async function refresh() {
    const current = ++version;
    try {
      const active = enabled(await read(app, MODULE_PATH));
      const clock = now();
      const today = localDay(clock);
      const weekday = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"][clock.getDay()];
      if (disposed || current !== version) return;
      dateLabel.textContent = `${today} ${weekday}`;
      if (!active) { body.empty(); body.createEl("p", { text: "Journal 模块已停用。已有记录仍保留，可通过 /module-toggle journal 启用。" }); return; }
      const files = app.vault.getMarkdownFiles().filter(file => file.path.startsWith(DAILY_ROOT));
      const notes = await Promise.all(files.map(async file => ({ path: file.path, text: await app.vault.read(file) })));
      const data = snapshot(notes, clock);
      if (disposed || current !== version) return;
      body.empty();
      const days = body.createEl("div", { cls: "journal-days" });
      data.recent.forEach(day => {
        const isToday = day.day === today;
        const label = `${isToday ? "今天 · " : ""}${day.day.slice(5).replace("-", "/")}`;
        const action = isToday ? "开始或继续记录" : day.recorded ? "已记录，打开原笔记" : "未记录";
        const attr = { "data-recorded": String(day.recorded), "aria-label": `${day.day} ${action}`, title: `${day.day} ${action}` };
        if (isToday) attr["aria-current"] = "date";
        const button = days.createEl("button", { text: label, cls: "journal-day", attr });
        button.disabled = (!isToday && !day.recorded) || (isToday && stateFor(app).launching);
        button.addEventListener("click", async () => {
          if (button.disabled) return;
          if (isToday) { await start(button); return; }
          try {
            if (!enabled(await read(app, MODULE_PATH))) throw new Error("Journal 模块已停用");
            const path = dayPath(day.day);
            if (!app.vault.getAbstractFileByPath(path)) throw new Error("记录尚未同步或已被移除");
            await app.workspace.openLinkText(path, "", false);
          } catch (error) { status.textContent = error.message; }
        });
      });
      const pending = body.createEl("details");
      pending.open = followupsOpen;
      pending.addEventListener("toggle", () => { followupsOpen = pending.open; });
      pending.createEl("summary", { text: `待回看 ${data.pending.length}` });
      if (!data.pending.length) pending.createEl("p", { text: "目前没有待回看事项。" });
      const ul = pending.createEl("ul");
      data.pending.forEach(item => link(ul.createEl("li"), `${item.path}#想再回看的事`, displayText(item.text)));
      const numbers = body.createEl("div", { cls: "journal-numbers" });
      for (const [label, count] of [["累计记录天数", data.totalCount], ["本月记录天数", data.monthCount], ["近 7 天记录天数", data.weekCount]]) {
        const stat = numbers.createEl("div", { cls: "journal-number" });
        stat.createEl("strong", { text: String(count) });
        stat.createEl("small", { text: label });
      }
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
  function atMidnight() {
    clearTimeout(midnightTimer);
    const clock = now();
    const next = new Date(clock.getFullYear(), clock.getMonth(), clock.getDate() + 1, 0, 0, 1);
    midnightTimer = setTimeout(() => { if (!disposed) { void refresh(); atMidnight(); } }, next - clock);
  }
  const wake = () => { if (!disposed) { void refresh(); atMidnight(); } };
  const visible = () => { if (!page.hidden) wake(); };
  page?.addEventListener("visibilitychange", visible);
  win?.addEventListener("focus", wake);
  dv.component.register(() => {
    disposed = true;
    version++;
    clearTimeout(timer);
    clearTimeout(midnightTimer);
    page?.removeEventListener("visibilitychange", visible);
    win?.removeEventListener("focus", wake);
  });
  atMidnight();
  await refresh();
}

if (typeof dv === "undefined") {
  module.exports = { scalar, enabled, localDay, validDay, dayPath, sections, meaningful, parseDaily, snapshot, initialize, promptFor, launch, renderJournal };
} else {
  return renderJournal(dv, input.app);
}

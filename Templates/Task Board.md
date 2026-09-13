---
tags: template
for: Tasks/Board
updated: 2026-09-14
---

%% Reference template for Tasks/Board.md. Not used to create new notes — edit the live file directly. Update this file whenever the view structure changes, and bump the `updated:` frontmatter date. Append a new dated `> [!note]` entry to Design Decisions when making structural changes. %%

## Design Decisions

> [!note] 2026-09-14 — Edit moved to a dedicated 任务列表 section (matrix read-only)
> - **Matrix = read-only visualization**: `renderTasks(host, list, withDomainFilter, editable)` — the Q1–Q4 + Unclassified cards are now rendered with `editable=false`, so no `✎` on the matrix.
> - **任务列表 区**: a single section below the matrix (separated by a top border) renders **all** open tasks with `editable=true`. Each entry shows a quadrant chip (`quadOf`: Q1/Q2/Q3/Q4/U) + due + domain, and carries the `✎` edit/delete drawer. This is the one place to modify a task.
> - **Rationale**: per user — task edits belong on the individual entry, not spread across the board's quadrant cards. Matrix stays a clean panorama; checkboxes still complete tasks in place.

> [!note] 2026-09-14 — Inline edit/delete on the board; Home task → open board
> - **Home**: matrix cards are now click-through — clicking a task (not its checkbox) opens `Tasks/Board.md`. Home stays capture + overview (add composer + read-only matrix); editing lives on the board.
> - **Board**: each task li gets a `✎` (`attachEdit`) that toggles an inline drawer prefilled from the **raw** line at `t.line` (parses `⭐` / `📅 date` / `#task/<area>` / title, preserves indent + `[status]`). Fields: title, Work/Life/Other/— area pills (— drops the domain → Unclassified), ⭐ toggle, `type=date` due, 保存 / 删除 / 取消.
> - **Write**: Save rebuilds the line and replaces it at `t.line`; Delete splices it. Both re-read the file and abort with a Notice if that line changed since the drawer opened (stale-guard). `vault.modify` retriggers the board's own dataviewjs so the card re-buckets.

> [!note] 2026-09-14 — Initial structure
> - **Vault-wide matrix**: Eisenhower 2×2 lives in `Tasks/Board.md` (not Work daily notes). The board does not query `Work/` — it only reads tasks on this page.
> - **SoT is `## Tasks` in the live file**: Open tasks are authored under `## Tasks`. Checking them off / moving them to `## Done` is the source of truth; the DataviewJS matrix is a view.
> - **Urgency from 📅 / Dataview `t.due`**: Urgent = due date exists and `dv.date(t.due) <= today+7 days` (`endOf("day")`, rolling one week, including overdue). Raising urgency requires a due date.
> - **Important = ⭐ in text**: Importance is human-marked in the task text, not a Dataview field.
> - **Domain = task tags** `#task/work` `#task/life` `#task/other` via `t.tags` (strip leading `#`). File-tag filter elsewhere is `p.file.tags.includes("#tag")`; here domain is per-task.
> - **Unclassified = no domain tag**: Always rendered full-width below the grid (planning hygiene). Domain filter pills apply only to Q1–Q4; unclassified stays visible.
> - **Filter pills All / Work / Life / Other**: Default All. Toggle `style.display` on `[data-domain]` rows — no page reload.
> - **Open tasks**: `t.status === " "` (not `!t.completed`) so in-progress `[>]` is excluded from the matrix.
> - **Ignore `## Done`**: Only tasks with `t.line` between the `## Tasks` and `## Done` H2s are included.

---

## Reference Content

%% The sections below mirror the live file. Keep in sync when making structural changes. %%

# Task Board

> 重要 = ⭐（人标）· 紧急 = 📅 due ≤ 今天+7 天 · 领域 = `#task/work` `#task/life` `#task/other`
> 上方矩阵只做可视化（只读）。改任务在下方「任务列表」区，点条目后的 ✎（标题/领域/⭐/due/删除），改完自动重新分桶。无领域标签 → Unclassified。命令：`/task-add` `/task-board`

```dataviewjs
const today = dv.date("today");
const page = dv.current();
if (!page) {
  dv.paragraph("Open Tasks/Board.md to render the matrix.");
} else {
  const headings = page.file.headings || [];
  let tasksLine = -1, doneLine = Infinity;
  for (const h of headings) {
    if (h.level === 2 && h.heading === "Tasks" && tasksLine === -1) tasksLine = h.position.start.line;
    if (h.level === 2 && h.heading === "Done") doneLine = h.position.start.line;
  }
  const inOpen = t => t.line > tasksLine && t.line < doneLine && t.status === " ";
  const boardPath = page.file.path;

  function domainOf(t) {
    const tags = (t.tags || []).map(x => String(x).replace(/^#/, ""));
    const hit = tags.find(x => x === "task/work" || x === "task/life" || x === "task/other" || x.startsWith("task/"));
    return hit ? hit.replace(/^task\//, "") : null;
  }
  function isImportant(t) { return (t.text || "").includes("⭐"); }
  function isUrgent(t) {
    if (!t.due) return false;
    const due = dv.date(t.due);
    if (!due) return false;
    const cutoff = today.plus({ days: 7 }).endOf("day");
    return due <= cutoff;
  }

  const open = page.file.tasks.where(inOpen);
  const classified = open.where(t => domainOf(t) != null);
  const unclassified = open.where(t => domainOf(t) == null);
  const q1 = classified.where(t => isImportant(t) && isUrgent(t));
  const q2 = classified.where(t => isImportant(t) && !isUrgent(t));
  const q3 = classified.where(t => !isImportant(t) && isUrgent(t));
  const q4 = classified.where(t => !isImportant(t) && !isUrgent(t));

  const root = dv.el("div", "", { attr: { style: "font-size:0.82em;" } });

  const pillWrap = root.createEl("div", {
    attr: { style: "display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:10px;" }
  });
  const seg = pillWrap.createEl("div", {
    attr: { style: "display:inline-flex;gap:2px;padding:2px;border-radius:9px;background:var(--background-secondary);" }
  });
  const pills = [
    { id: "all", label: "All" },
    { id: "work", label: "Work" },
    { id: "life", label: "Life" },
    { id: "other", label: "Other" }
  ];
  const btns = {};
  let active = "all";

  const cellBase = "background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:8px;padding:10px;min-height:88px;";
  const badgeStyle = "font-size:0.72em;padding:1px 7px;border-radius:10px;background:var(--background-primary);border:1px solid var(--background-modifier-border);color:var(--text-muted);white-space:nowrap;";

  function asArray(list) {
    if (!list) return [];
    if (typeof list.array === "function") return list.array();
    return Array.from(list);
  }

  function attachEdit(li, t) {
    const editBtn = li.createEl("button", { text: "✎" });
    editBtn.setAttribute("style", "margin-left:6px;border:none;background:transparent;cursor:pointer;color:var(--text-faint);font-size:0.82em;");
    editBtn.title = "编辑";
    editBtn.addEventListener("click", async (e) => {
      e.preventDefault(); e.stopPropagation();
      const existing = li.querySelector(".tb-editor");
      if (existing) { existing.remove(); return; }
      const f = app.vault.getAbstractFileByPath(boardPath);
      if (!f) return;
      const fileLines = (await app.vault.read(f)).split("\n");
      const lineNo = t.line;
      const rawLine = fileLines[lineNo] ?? "";
      const indent = (rawLine.match(/^(\s*)/) || ["", ""])[1];
      const status = (rawLine.match(/- \[(.)\]/) || [null, " "])[1];
      let curImp = /⭐/.test(rawLine);
      const curDue = (rawLine.match(/📅\s*(\d{4}-\d{2}-\d{2})/) || [null, ""])[1];
      const curArea = (rawLine.match(/#task\/(\S+)/) || [null, ""])[1];
      const curTitle = rawLine
        .replace(/^\s*- \[.\]\s*/, "")
        .replace(/⭐/g, "")
        .replace(/📅\s*\d{4}-\d{2}-\d{2}/g, "")
        .replace(/#task\/\S+/g, "")
        .replace(/\s+/g, " ").trim();

      const inpStyle2 = "padding:4px 8px;border:1px solid var(--background-modifier-border);border-radius:6px;background:var(--background-primary);color:var(--text-normal);font-size:0.82em;";
      const drawer = li.createEl("div", { cls: "tb-editor", attr: { style: "display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:6px 0;padding:6px;border:1px solid var(--background-modifier-border);border-radius:8px;background:var(--background-primary);" } });
      const tIn = drawer.createEl("input"); tIn.type = "text"; tIn.value = curTitle; tIn.setAttribute("style", inpStyle2 + "flex:1;min-width:120px;");

      const areaOpts = ["work", "life", "other", "none"];
      const aSeg = drawer.createEl("div", { attr: { style: "display:inline-flex;gap:2px;padding:2px;border-radius:9px;background:var(--background-secondary);" } });
      const aBtns = {};
      let areaSel = (curArea || "none");
      function paintA() {
        for (const a of areaOpts) {
          aBtns[a].style.cssText = "padding:3px 8px;border-radius:7px;border:none;cursor:pointer;font-size:0.74em;font-weight:600;" +
            (areaSel === a ? "background:var(--background-primary);color:var(--text-normal);box-shadow:0 1px 3px rgba(0,0,0,0.08);" : "background:transparent;color:var(--text-muted);");
        }
      }
      for (const a of areaOpts) {
        aBtns[a] = aSeg.createEl("button", { text: a === "none" ? "—" : a[0].toUpperCase() + a.slice(1) });
        aBtns[a].addEventListener("click", () => { areaSel = a; paintA(); });
      }
      paintA();

      const sBtn = drawer.createEl("button", { text: "⭐" });
      function paintS() {
        sBtn.style.cssText = "padding:3px 9px;border-radius:6px;cursor:pointer;font-size:0.82em;border:1px solid " +
          (curImp ? "var(--interactive-accent)" : "var(--background-modifier-border)") + ";background:" +
          (curImp ? "var(--interactive-accent)" : "var(--background-secondary)") + ";color:" +
          (curImp ? "var(--text-on-accent)" : "var(--text-muted)") + ";";
      }
      sBtn.addEventListener("click", () => { curImp = !curImp; paintS(); });
      paintS();

      const dIn = drawer.createEl("input"); dIn.type = "date"; dIn.value = curDue; dIn.title = "due（7 天内 = 紧急；空 = 不紧急）"; dIn.setAttribute("style", inpStyle2);

      const saveBtn = drawer.createEl("button", { text: "保存" });
      saveBtn.style.cssText = "padding:3px 12px;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:0.78em;background:var(--interactive-accent);color:var(--text-on-accent);";
      const delBtn = drawer.createEl("button", { text: "删除" });
      delBtn.style.cssText = "padding:3px 10px;border:1px solid var(--background-modifier-border);border-radius:6px;cursor:pointer;font-size:0.78em;background:var(--background-secondary);color:var(--text-error, #c4553a);";
      const cancelBtn = drawer.createEl("button", { text: "取消" });
      cancelBtn.style.cssText = "padding:3px 10px;border:1px solid var(--background-modifier-border);border-radius:6px;cursor:pointer;font-size:0.78em;background:var(--background-secondary);color:var(--text-muted);";

      cancelBtn.addEventListener("click", () => drawer.remove());

      saveBtn.addEventListener("click", async () => {
        const title = (tIn.value || "").trim().replace(/\s+/g, " ");
        if (!title) { new Notice("标题不能为空"); return; }
        const due = (dIn.value || "").trim();
        if (due && !/^\d{4}-\d{2}-\d{2}$/.test(due)) { new Notice("due 必须是 YYYY-MM-DD"); return; }
        const cur = (await app.vault.read(f)).split("\n");
        if ((cur[lineNo] ?? "") !== rawLine) { new Notice("看板已变化，请刷新后重试"); return; }
        const bits = [indent + "- [" + status + "]"];
        if (curImp) bits.push("⭐");
        if (due) bits.push("📅 " + due);
        bits.push(title);
        if (areaSel !== "none") bits.push("#task/" + areaSel);
        cur[lineNo] = bits.join(" ");
        await app.vault.modify(f, cur.join("\n"));
        new Notice("已更新");
      });

      delBtn.addEventListener("click", async () => {
        const cur = (await app.vault.read(f)).split("\n");
        if ((cur[lineNo] ?? "") !== rawLine) { new Notice("看板已变化，请刷新后重试"); return; }
        cur.splice(lineNo, 1);
        await app.vault.modify(f, cur.join("\n"));
        new Notice("已删除");
      });

      tIn.focus();
    });
  }

  function quadOf(t) {
    if (domainOf(t) == null) return "U";
    const imp = isImportant(t), urg = isUrgent(t);
    return imp ? (urg ? "Q1" : "Q2") : (urg ? "Q3" : "Q4");
  }

  function renderTasks(host, list, withDomainFilter, editable) {
    const arr = asArray(list);
    const n = list.length != null ? list.length : arr.length;
    if (n === 0) {
      host.createEl("div", { text: "（空）", attr: { style: "color:var(--text-faint);" } });
      return;
    }
    const start = dv.container.childElementCount;
    dv.taskList(list, false);
    const nodes = Array.from(dv.container.children).slice(start);
    for (const node of nodes) host.appendChild(node);
    const items = host.querySelectorAll("li");
    items.forEach((li, i) => {
      const t = arr[i];
      if (!t) return;
      const d = domainOf(t);
      if (withDomainFilter) li.setAttribute("data-domain", d || "");
      const meta = [];
      if (editable) meta.push(quadOf(t));
      if (t.due) {
        const dd = dv.date(t.due);
        if (dd) meta.push(dd.toFormat("yyyy-MM-dd"));
      }
      if (d) meta.push(d);
      if (meta.length) {
        li.createEl("span", {
          text: meta.join(" · "),
          attr: { style: "margin-left:8px;font-size:0.72em;color:var(--text-muted);" }
        });
      }
      if (editable) attachEdit(li, t);
    });
  }

  function paintPills() {
    for (const p of pills) {
      btns[p.id].style.cssText = "padding:4px 14px;border-radius:7px;border:none;cursor:pointer;font-size:0.82em;font-weight:600;transition:all 0.15s;" +
        (active === p.id
          ? "background:var(--background-primary);color:var(--text-normal);box-shadow:0 1px 3px rgba(0,0,0,0.08);"
          : "background:transparent;color:var(--text-muted);box-shadow:none;");
    }
  }

  function applyFilter(id) {
    active = id;
    paintPills();
    const items = grid.querySelectorAll("[data-domain]");
    for (const el of items) {
      const d = el.getAttribute("data-domain");
      el.style.display = (id === "all" || d === id) ? "" : "none";
    }
  }

  for (const p of pills) {
    btns[p.id] = seg.createEl("button", { text: p.label });
    btns[p.id].addEventListener("click", () => applyFilter(p.id));
  }
  paintPills();

  const grid = root.createEl("div", {
    attr: { style: "display:grid;grid-template-columns:1fr 1fr;gap:10px;" }
  });

  const quads = [
    { list: q1, title: "Q1 重要 · 紧急（立刻做）", border: "#c4553a" },
    { list: q2, title: "Q2 重要 · 不紧急（安排做）", border: "var(--interactive-accent)" },
    { list: q3, title: "Q3 不重要 · 紧急（压缩）", border: "var(--text-muted)" },
    { list: q4, title: "Q4 不重要 · 不紧急（减少）", border: "var(--text-faint)" }
  ];

  for (const q of quads) {
    const n = q.list.length != null ? q.list.length : asArray(q.list).length;
    const cell = grid.createEl("div", {
      attr: { style: cellBase + `border-left:3px solid ${q.border};` }
    });
    const head = cell.createEl("div", {
      attr: { style: "display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px;" }
    });
    head.createEl("div", { text: q.title, attr: { style: "font-weight:600;color:var(--text-normal);" } });
    head.createEl("span", { text: String(n), attr: { style: badgeStyle } });
    const host = cell.createEl("div", "");
    renderTasks(host, q.list, true, false);
  }

  const unN = unclassified.length != null ? unclassified.length : asArray(unclassified).length;
  const unCell = root.createEl("div", {
    attr: { style: cellBase + "margin-top:10px;" }
  });
  const unHead = unCell.createEl("div", {
    attr: { style: "display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px;" }
  });
  unHead.createEl("div", { text: "Unclassified", attr: { style: "font-weight:600;color:var(--text-normal);" } });
  unHead.createEl("span", { text: String(unN), attr: { style: badgeStyle } });
  renderTasks(unCell.createEl("div", ""), unclassified, false, false);

  const n1 = q1.length != null ? q1.length : asArray(q1).length;
  const n2 = q2.length != null ? q2.length : asArray(q2).length;
  const n3 = q3.length != null ? q3.length : asArray(q3).length;
  const n4 = q4.length != null ? q4.length : asArray(q4).length;

  root.createEl("div", {
    text: `Q1 ${n1} · Q2 ${n2} · Q3 ${n3} · Q4 ${n4} · Unclassified ${unN}`,
    attr: { style: "margin-top:10px;color:var(--text-muted);font-size:0.82em;" }
  });

  if (n2 === 0 && n1 >= 1) {
    root.createEl("div", {
      text: "Q1 偏多而 Q2 为空 — 效能在第二象限",
      attr: { style: "margin-top:4px;color:var(--text-faint);font-size:0.82em;" }
    });
  }

  // Editable entries — matrix above is read-only visualization; edit each task here
  const listWrap = root.createEl("div", { attr: { style: "margin-top:16px;border-top:1px solid var(--background-modifier-border);padding-top:10px;" } });
  listWrap.createEl("div", { text: "任务列表（点 ✎ 修改）", attr: { style: "font-weight:600;margin-bottom:6px;font-size:0.82em;color:var(--text-normal);" } });
  renderTasks(listWrap.createEl("div", ""), open, false, true);
}
```

## Tasks

## Done

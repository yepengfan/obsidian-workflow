// Presentation helpers never rewrite the underlying task text.
function taskDisplayText(text) {
  // Split protected Markdown first so normalization cannot change link targets or code.
  return String(text)
    .split(/(\[\[[^\]]+\]\]|\[[^\]]*\]\([^)]*\)|`[^`]*`)/g)
    .map((part, index) =>
      index % 2
        ? part
        : part
            .replace(
              /⭐\uFE0F?|📅\s*\d{4}-\d{2}-\d{2}|\[due::\s*\d{4}-\d{2}-\d{2}\s*\]|\(due::\s*\d{4}-\d{2}-\d{2}\s*\)|(?:^|(?<=\s))#task\/[^\s#]+/gu,
              "",
            )
            .replace(/\s+/g, " "),
    )
    .join("")
    .trim();
}
function taskArea(task) {
  const tag = Array.from(task.tags || [])
    .map(String)
    .find((tag) => /^#?task\/[^\s#]+$/.test(tag));
  return tag ? tag.replace(/^#?task\//, "") : null;
}
function taskMatchesArea(task, filter) {
  // Notes without an area remain visible so they can be classified.
  const area = taskArea(task);
  return filter === "all" || area === null || area === filter;
}
function renderTaskBoard(dv, input) {
  const app = input.app;
  const { Notice, Menu } = input;
  const isMobile = app.isMobile;
  const boardPath = "Tasks/Board.md";
  const fence = String.fromCharCode(96).repeat(3);
  const section = (input.container || dv.container).createEl("div", {
    cls: "task-dashboard-body",
    attr: { style: "margin-bottom:16px;" },
  });
  const form = section.createEl("div", {
    cls: "tb-composer",
    attr: { role: "group", "aria-label": "Add a task" },
  });
  const titleRow = form.createEl("div", { cls: "tb-compose-title" });
  const titleInp = titleRow.createEl("input", {
    attr: {
      type: "text",
      placeholder: "What needs doing?",
      "aria-label": "Task title",
    },
  });
  const addBtn = titleRow.createEl("button", {
    text: "+ Add task",
    cls: "mod-cta",
    attr: { type: "button" },
  });
  const options = form.createEl("div", { cls: "tb-compose-options" });
  const areaField = options.createEl("div", { cls: "tb-compose-field" });
  areaField.createEl("span", { text: "Area", cls: "tb-field-label" });
  const areaSeg = areaField.createEl("div", {
    cls: "tb-segments",
    attr: { role: "group", "aria-label": "New task area" },
  });
  const areas = ["work", "life", "other"];
  let area = "work",
    important = false,
    destination;
  const areaBtns = {};
  function updateDestination() {
    if (!destination) return;
    const due = dueInp.value ? dv.date(dueInp.value) : null;
    const urgent =
      due?.isValid !== false &&
      due &&
      due <= dv.date("today").plus({ days: 7 }).endOf("day");
    const quadrant = important
      ? urgent
        ? "Q1 · Do now"
        : "Q2 · Schedule"
      : urgent
        ? "Q3 · Handle quickly"
        : "Q4 · Later";
    destination.textContent = `Will add to ${quadrant}`;
  }
  function paintArea() {
    for (const a of areas)
      areaBtns[a].setAttribute("aria-pressed", String(area === a));
  }
  for (const a of areas) {
    areaBtns[a] = areaSeg.createEl("button", {
      text: a[0].toUpperCase() + a.slice(1),
      attr: { type: "button" },
    });
    areaBtns[a].addEventListener("click", () => {
      area = a;
      paintArea();
    });
  }
  paintArea();
  const starBtn = options.createEl("button", {
    attr: { type: "button", "aria-label": "Mark task important" },
    cls: "tb-important",
  });
  function paintStar() {
    starBtn.textContent = important ? "★ Important" : "☆ Important";
    starBtn.setAttribute("aria-pressed", String(important));
    updateDestination();
  }
  starBtn.addEventListener("click", () => {
    important = !important;
    paintStar();
  });
  paintStar();
  const dueField = options.createEl("label", { cls: "tb-compose-field" });
  dueField.createEl("span", {
    text: "Due (optional)",
    cls: "tb-field-label",
  });
  const dueInp = dueField.createEl("input", {
    attr: {
      type: "date",
      "aria-label": "Due date",
      title: "Due within 7 days = urgent; no date = not urgent",
    },
  });
  dueInp.addEventListener("input", updateDestination);
  destination = form.createEl("div", {
    cls: "tb-destination",
    attr: { role: "status", "aria-live": "polite" },
  });
  updateDestination();

  function headingIndex(lines, heading) {
    let inFence = false;
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].trim().startsWith(fence)) {
        inFence = !inFence;
        continue;
      }
      if (!inFence && lines[i].trim() === heading) return i;
    }
    return -1;
  }

  async function ensureBoard() {
    if (!app.vault.getAbstractFileByPath("Tasks"))
      await app.vault.createFolder("Tasks");
    let f = app.vault.getAbstractFileByPath(boardPath);
    if (f) return f;
    // Build the full board (matrix + edit UI) from the template's Reference Content,
    // so a Home-created board is identical to one made by /task-add or /task-board.
    let body = null;
    const tmpl = app.vault.getAbstractFileByPath("Templates/Task Board.md");
    if (tmpl) {
      const traw = await app.vault.read(tmpl);
      const mi = traw.indexOf("## Reference Content");
      if (mi >= 0) {
        const reference = traw.slice(mi + "## Reference Content".length);
        const bi = reference.indexOf("\n---\n");
        if (bi >= 0) body = reference.slice(bi).trim() + "\n";
      }
    }
    if (!body)
      throw new Error(
        "Task Board template is unavailable. Restore Templates/Task Board.md and retry.",
      );
    return await app.vault.create(boardPath, body);
  }

  addBtn.addEventListener("click", async () => {
    if (addBtn.disabled) return;
    const title = (titleInp.value || "").trim().replace(/\s+/g, " ");
    if (!title) {
      new Notice("Enter a task title first");
      return;
    }
    const due = (dueInp.value || "").trim();
    if (due && !/^\d{4}-\d{2}-\d{2}$/.test(due)) {
      new Notice("Use YYYY-MM-DD for the due date");
      return;
    }
    const bits = ["- [ ]"];
    if (important) bits.push("⭐");
    if (due) bits.push("📅 " + due);
    bits.push(title);
    bits.push("#task/" + area);
    const line = bits.join(" ");
    addBtn.disabled = true;
    try {
      const f = await ensureBoard();
      await app.vault.process(f, (raw) => {
        const lines = raw.split("\n");
        let at = headingIndex(lines, "## Tasks");
        if (at < 0) {
          lines.push("", "## Tasks", "");
          at = lines.length - 2;
        }
        let ins = at + 1;
        while (ins < lines.length && lines[ins].trim() === "") ins++;
        lines.splice(ins, 0, line);
        if (headingIndex(lines, "## Done") < 0) lines.push("", "## Done", "");
        return lines.join("\n");
      });
      titleInp.value = "";
      dueInp.value = "";
      const today = dv.date("today");
      const urgent =
        due && dv.date(due) <= today.plus({ days: 7 }).endOf("day");
      const q = important ? (urgent ? "Q1" : "Q2") : urgent ? "Q3" : "Q4";
      updateDestination();
      titleInp.focus();
      new Notice("Added to " + q + " · " + area);
    } catch (error) {
      new Notice(error.message || "Could not add task. Try again.");
    } finally {
      addBtn.disabled = false;
    }
  });
  titleInp.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.isComposing) {
      e.preventDefault();
      addBtn.click();
    }
  });

  const bfile = app.vault.getAbstractFileByPath(boardPath);
  const bpage = dv.page(boardPath);
  if (!bfile || !bpage) {
    section.createEl("div", {
      text: "No tasks yet. Add your first task above.",
      attr: { style: "color:var(--text-muted);font-size:0.82em;" },
    });
    return;
  }
  const bCache = app.metadataCache.getFileCache(bfile);
  const bHeadings = bCache?.headings || [];
  let tasksLine = -1,
    doneLine = Infinity;
  for (const h of bHeadings) {
    if (h.level === 2 && h.heading === "Tasks" && tasksLine === -1)
      tasksLine = h.position.start.line;
    if (h.level === 2 && h.heading === "Done") doneLine = h.position.start.line;
  }
  const today = dv.date("today");
  const inOpen = (t) =>
    tasksLine !== -1 &&
    t.line > tasksLine &&
    t.line < doneLine &&
    t.status === " ";
  const domainOf = taskArea;
  function isImportant(t) {
    return (t.text || "").includes("⭐");
  }
  function isUrgent(t) {
    if (!t.due) return false;
    const due = dv.date(t.due);
    if (!due) return false;
    return due <= today.plus({ days: 7 }).endOf("day");
  }
  const open = bpage.file.tasks.where(inOpen);
  const classified = open.where((t) => domainOf(t) != null);
  const unclassified = open.where((t) => domainOf(t) == null);
  const q1 = classified.where((t) => isImportant(t) && isUrgent(t));
  const q2 = classified.where((t) => isImportant(t) && !isUrgent(t));
  const q3 = classified.where((t) => !isImportant(t) && isUrgent(t));
  const q4 = classified.where((t) => !isImportant(t) && !isUrgent(t));

  const root = section.createEl("div", { cls: "tb-board" });
  const pillWrap = root.createEl("div", { cls: "tb-filter-bar" });
  pillWrap.createEl("span", { text: "Filter", cls: "tb-field-label" });
  const seg = pillWrap.createEl("div", {
    cls: "tb-segments",
    attr: { role: "group", "aria-label": "Filter tasks by area" },
  });
  const pills = [
    { id: "all", label: "All" },
    ...[...new Set([...areas, ...Array.from(classified).map(domainOf)])].map(
      (id) => ({ id, label: id[0].toUpperCase() + id.slice(1) }),
    ),
  ];
  const btns = {};
  let active = "all";
  const filterStatus = pillWrap.createEl("span", {
    cls: "tb-filter-status",
    attr: { role: "status", "aria-live": "polite" },
  });
  const help = pillWrap.createEl("details", { cls: "tb-help" });
  help.createEl("summary", { text: "Board help" });
  help.createEl("p", {
    text: "Important is marked by you. Urgent means due within 7 days, including overdue. Drag the move handle or click it to choose a quadrant. Moving to urgent keeps an urgent due date or sets one 7 days from today; moving out clears an urgent date. You can undo a move. Unclassified tasks stay visible in every filter until you choose an area.",
  });
  function asArray(list) {
    if (!list) return [];
    if (typeof list.array === "function") return list.array();
    return Array.from(list);
  }

  // Keep drag state local: text dragged from other notes must never modify the board.
  let dragged = null;
  let moving = false;
  const dropCells = [];
  function clearDropHints() {
    for (const cell of dropCells) {
      cell.style.outline = "";
      cell.style.background = "var(--background-secondary)";
    }
  }
  function taskInSection(lines, line) {
    let sectionName = "",
      codeFence = null;
    for (let i = 0; i <= line; i++) {
      const value = lines[i] || "";
      const f = value.match(/^\s{0,3}(`{3,}|~{3,})(.*)$/);
      if (f) {
        if (!codeFence) codeFence = { char: f[1][0], length: f[1].length };
        else if (
          f[1][0] === codeFence.char &&
          f[1].length >= codeFence.length &&
          !f[2].trim()
        )
          codeFence = null;
        continue;
      }
      if (codeFence) continue;
      const heading = value.match(/^#{1,2} (.+?)\s*#*\s*$/);
      if (heading) sectionName = heading[1];
      if (i === line)
        return sectionName === "Tasks" && /^\s*[-*+] \[ \] /.test(value);
    }
    return false;
  }
  function moveLine(raw, q) {
    const match = raw.replace(/\r$/, "").match(/^(\s*[-*+] \[ \] )(.+)$/);
    if (!match || !/#task\/[^\s#]+/.test(match[2]))
      throw new Error("Assign an area before moving this task.");
    // Support Tasks emoji dates and Dataview inline due fields, without touching links or other dates.
    const duePattern =
      /📅\s*\d{4}-\d{2}-\d{2}|\[due::\s*\d{4}-\d{2}-\d{2}\s*\]|\(due::\s*\d{4}-\d{2}-\d{2}\s*\)/gi;
    let body = match[2];
    const dues = body.match(duePattern) || [];
    if (
      dues.length > 1 ||
      /📅|\bdue\s*::/i.test(body.replace(duePattern, ""))
    ) {
      throw new Error("Fix the ambiguous due date before moving this task.");
    }
    const urgent = q === "Q1" || q === "Q3";
    const important = q === "Q1" || q === "Q2";
    const due = dues.length
      ? dv.date(dues[0].match(/\d{4}-\d{2}-\d{2}/)[0])
      : null;
    if (dues.length && (!due || due.isValid === false))
      throw new Error("Fix the invalid due date before moving this task.");
    const cutoff = dv.date("today").plus({ days: 7 }).endOf("day");
    const wasUrgent = due && due <= cutoff;
    if (urgent && !wasUrgent) {
      const token =
        "📅 " + dv.date("today").plus({ days: 7 }).toFormat("yyyy-MM-dd");
      body = dues.length ? body.replace(duePattern, token) : body + " " + token;
    } else if (!urgent && wasUrgent) body = body.replace(duePattern, "");
    body = body.replace(/⭐\uFE0F?\s*/gu, "").trim();
    return (
      match[1] +
      (important ? "⭐ " : "") +
      body +
      (raw.endsWith("\r") ? "\r" : "")
    );
  }
  async function moveTask(t, q) {
    if (moving) return;
    moving = true;
    try {
      let before, after;
      await app.vault.process(bfile, (content) => {
        const lines = content.split("\n");
        const raw = lines[t.line];
        const text = raw
          ?.replace(/\r$/, "")
          .match(/^\s*[-*+] \[ \] (.*)$/)?.[1];
        if (!taskInSection(lines, t.line) || text?.trim() !== t.text.trim()) {
          throw new Error(
            "Task changed. Wait for the dashboard to refresh and try again.",
          );
        }
        before = raw;
        after = moveLine(raw, q);
        lines[t.line] = after;
        return lines.join("\n");
      });
      if (before === after) return;
      app.workspace.trigger("dataview:refresh-views");
      const message = document.createDocumentFragment();
      message.createSpan({
        text:
          "Moved to " +
          q +
          ". " +
          (q === "Q1" || q === "Q3"
            ? "Urgent date kept or set to 7 days from today."
            : "Urgent date cleared; later dates kept.") +
          " ",
      });
      const undo = message.createEl("button", { text: "Undo" });
      const notice = new Notice(message, 10000);
      undo.addEventListener("click", async () => {
        undo.disabled = true;
        try {
          await app.vault.process(bfile, (content) => {
            const lines = content.split("\n");
            if (!taskInSection(lines, t.line) || lines[t.line] !== after)
              throw new Error(
                "Task changed again. Undo is no longer available.",
              );
            lines[t.line] = before;
            return lines.join("\n");
          });
          notice.hide();
          app.workspace.trigger("dataview:refresh-views");
        } catch (error) {
          new Notice(error.message || "Undo failed.");
        }
      });
    } catch (error) {
      new Notice(error.message || "Move failed. Try again.");
    } finally {
      moving = false;
    }
  }
  // Task movement UI.

  function attachEdit(li, t) {
    const editBtn = li.createEl("button", {
      text: "Edit",
      cls: "tb-edit",
      attr: { type: "button", "aria-label": "Edit task" },
    });
    editBtn.title = "Edit task";
    editBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const existing = li.querySelector(".tb-editor");
      if (existing) {
        existing.remove();
        return;
      }
      const f = app.vault.getAbstractFileByPath(boardPath);
      if (!f) return;
      const fileLines = (await app.vault.read(f)).split("\n");
      const lineNo = t.line;
      const rawLine = fileLines[lineNo] ?? "";
      if (
        !taskInSection(fileLines, lineNo) ||
        rawLine.replace(/^\s*[-*+] \[ \] /, "").trim() !== t.text.trim()
      ) {
        new Notice("Task changed. Refresh before editing.");
        return;
      }
      const indent = (rawLine.match(/^(\s*)/) || ["", ""])[1];
      const status = (rawLine.match(/- \[(.)\]/) || [null, " "])[1];
      let curImp = /⭐/.test(rawLine);
      const curDue = (rawLine.match(/📅\s*(\d{4}-\d{2}-\d{2})/) || [
        null,
        "",
      ])[1];
      const curArea = (rawLine.match(/#task\/(\S+)/) || [null, ""])[1];
      const curTitle = rawLine
        .replace(/^\s*- \[.\]\s*/, "")
        .replace(/⭐/g, "")
        .replace(/📅\s*\d{4}-\d{2}-\d{2}/g, "")
        .replace(/#task\/\S+/g, "")
        .replace(/\s+/g, " ")
        .trim();

      const inpStyle2 =
        (isMobile ? "padding:6px 10px;" : "padding:4px 8px;") +
        "border:1px solid var(--background-modifier-border);border-radius:6px;background:var(--background-primary);color:var(--text-normal);font-size:12px;";
      const drawer = li.createEl("div", {
        cls: "tb-editor",
        attr: {
          style:
            "display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:6px 0;padding:6px;border:1px solid var(--background-modifier-border);border-radius:8px;background:var(--background-primary);",
        },
      });
      const tIn = drawer.createEl("input");
      tIn.type = "text";
      tIn.setAttribute("aria-label", "Edit task title");
      tIn.value = curTitle;
      tIn.setAttribute(
        "style",
        inpStyle2 + "flex:1 0 100%;width:100%;min-width:0;",
      );

      const editorOptions = drawer.createEl("div", {
        cls: "tb-editor-options",
      });
      const areaOpts = ["work", "life", "other", "none"];
      const areaField = editorOptions.createEl("div", {
        cls: "tb-compose-field",
      });
      areaField.createEl("span", { text: "Area", cls: "tb-field-label" });
      const aSeg = areaField.createEl("div", {
        cls: "tb-segments",
        attr: { role: "group", "aria-label": "Edit task area" },
      });
      const aBtns = {};
      let areaSel = curArea || "none";
      function paintA() {
        for (const a of areaOpts)
          aBtns[a].setAttribute("aria-pressed", String(areaSel === a));
      }
      for (const a of areaOpts) {
        aBtns[a] = aSeg.createEl("button", {
          text: a === "none" ? "-" : a[0].toUpperCase() + a.slice(1),
        });
        aBtns[a].addEventListener("click", () => {
          areaSel = a;
          paintA();
        });
      }
      paintA();

      const sBtn = editorOptions.createEl("button", {
        cls: "tb-important",
        attr: { type: "button" },
      });
      function paintS() {
        sBtn.textContent = curImp ? "★ Important" : "☆ Important";
        sBtn.setAttribute("aria-pressed", String(curImp));
        sBtn.setAttribute("aria-label", "Mark task important");
      }
      sBtn.addEventListener("click", () => {
        curImp = !curImp;
        paintS();
      });
      paintS();

      const dueField = editorOptions.createEl("label", {
        cls: "tb-compose-field",
      });
      dueField.createEl("span", {
        text: "Due (optional)",
        cls: "tb-field-label",
      });
      const dIn = dueField.createEl("input");
      dIn.type = "date";
      dIn.setAttribute("aria-label", "Edit task due date");
      dIn.value = curDue;
      dIn.title = "Due within 7 days = urgent; no date = not urgent";

      const editorActions = drawer.createEl("div", {
        cls: "tb-editor-actions",
      });
      const saveBtn = editorActions.createEl("button", { text: "Save" });
      saveBtn.style.cssText =
        (isMobile ? "padding:6px 12px;" : "padding:3px 12px;") +
        "border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:12px;background:var(--interactive-accent);color:var(--text-on-accent);";
      const delBtn = editorActions.createEl("button", { text: "Delete" });
      delBtn.style.cssText =
        (isMobile ? "padding:6px 12px;" : "padding:3px 10px;") +
        "border:1px solid var(--background-modifier-border);border-radius:6px;cursor:pointer;font-size:12px;background:var(--background-secondary);color:var(--text-error, #c4553a);";
      const cancelBtn = editorActions.createEl("button", { text: "Cancel" });
      cancelBtn.style.cssText =
        (isMobile ? "padding:6px 12px;" : "padding:3px 10px;") +
        "border:1px solid var(--background-modifier-border);border-radius:6px;cursor:pointer;font-size:12px;background:var(--background-secondary);color:var(--text-muted);";

      cancelBtn.addEventListener("click", () => drawer.remove());

      saveBtn.addEventListener("click", async () => {
        const title = (tIn.value || "").trim().replace(/\s+/g, " ");
        if (!title) {
          new Notice("A task title is required");
          return;
        }
        const due = (dIn.value || "").trim();
        if (due && !/^\d{4}-\d{2}-\d{2}$/.test(due)) {
          new Notice("Use YYYY-MM-DD for the due date");
          return;
        }
        const bits = [indent + "- [" + status + "]"];
        if (curImp) bits.push("⭐");
        if (due) bits.push("📅 " + due);
        bits.push(title);
        if (areaSel !== "none") bits.push("#task/" + areaSel);
        try {
          await app.vault.process(f, (content) => {
            const cur = content.split("\n");
            if (cur[lineNo] !== rawLine || !taskInSection(cur, lineNo))
              throw new Error("Task board changed. Refresh and try again.");
            cur[lineNo] = bits.join(" ");
            return cur.join("\n");
          });
        } catch (error) {
          new Notice(error.message);
          return;
        }
        new Notice("Saved");
      });

      delBtn.addEventListener("click", async () => {
        try {
          await app.vault.process(f, (content) => {
            const cur = content.split("\n");
            if (cur[lineNo] !== rawLine || !taskInSection(cur, lineNo))
              throw new Error("Task board changed. Refresh and try again.");
            cur.splice(lineNo, 1);
            return cur.join("\n");
          });
        } catch (error) {
          new Notice(error.message);
          return;
        }
        new Notice("Deleted");
      });

      tIn.focus();
    });
  }

  const taskViews = [];
  function renderTasks(hostEl, list, editable = false) {
    const arr = asArray(list);
    const empty = hostEl.createEl("p", { text: "No tasks", cls: "tb-empty" });
    const view = { items: [], empty, count: null };
    taskViews.push(view);
    if (!arr.length) return view;
    const start = dv.container.childElementCount;
    dv.taskList(
      arr.map((t) => ({
        ...t,
        parent: null,
        children: [],
        visual: taskDisplayText(t.text),
      })),
      false,
    );
    const nodes = Array.from(dv.container.children).slice(start);
    for (const node of nodes) hostEl.appendChild(node);
    const items = hostEl.querySelectorAll("li.dataview.task-list-item");
    items.forEach((li, i) => {
      const t = arr[i];
      if (!t) return;
      const d = domainOf(t);
      view.items.push({ node: li, task: t });
      li.classList.add("tb-task-row");
      li.setAttribute("data-domain", d || "");
      // Dataview's row click opens the raw source. The card's links and controls
      // retain their own actions; plain text stays in the workbench.
      li.addEventListener(
        "click",
        (e) => {
          if (!e.target.closest("a,button,input")) e.stopImmediatePropagation();
        },
        { capture: true },
      );
      const title = Array.from(li.children).find(
        (child) => child.tagName === "SPAN",
      );
      if (title) title.classList.add("tb-task-title");
      const meta = li.createEl("div", { cls: "tb-task-meta" });
      if (d)
        meta.createEl("span", {
          text: d[0].toUpperCase() + d.slice(1),
          cls: "tb-area-badge",
        });
      else meta.createEl("span", { text: "Needs area", cls: "tb-area-badge" });
      if (editable && isImportant(t))
        meta.createEl("span", { text: "Important", cls: "tb-priority" });
      if (t.due) {
        const date = dv.date(t.due);
        if (date?.isValid !== false && date)
          meta.createEl("span", {
            text: date.toFormat("yyyy-MM-dd"),
            cls: date < today ? "tb-overdue" : "tb-due",
          });
      }
      if (title) {
        const expand = meta.createEl("button", {
          text: "Show more",
          cls: "tb-expand",
          attr: { type: "button", "aria-expanded": "false" },
        });
        let expanded = false;
        const measure = () => {
          expand.hidden =
            !expanded && title.scrollHeight <= title.clientHeight + 1;
        };
        const setExpanded = (value) => {
          expanded = value;
          li.classList.toggle("is-expanded", expanded);
          expand.textContent = expanded ? "Show less" : "Show more";
          expand.setAttribute("aria-expanded", String(expanded));
          measure();
        };
        expand.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          setExpanded(!expanded);
        });
        title.addEventListener("focusin", () => {
          if (!expand.hidden) setExpanded(true);
        });
        measure();
        if (typeof ResizeObserver !== "undefined") {
          const observer = new ResizeObserver(measure);
          observer.observe(title);
          dv.component.register(() => observer.disconnect());
        }
      }
      if (d && !editable) {
        const handle = li.createEl("button", {
          text: "⋮⋮",
          attr: {
            "aria-label": "Move task to quadrant",
            title: "Drag to a quadrant, or click to choose",
            class: "tb-move",
            type: "button",
          },
        });
        handle.draggable = true;
        handle.addEventListener("dragstart", (e) => {
          e.stopPropagation();
          if (moving || !e.dataTransfer) {
            e.preventDefault();
            return;
          }
          dragged = t;
          e.dataTransfer.effectAllowed = "move";
          e.dataTransfer.setData("text/plain", "Task Board: " + t.line);
          li.style.opacity = "0.45";
        });
        handle.addEventListener("dragend", () => {
          dragged = null;
          li.style.opacity = "";
          clearDropHints();
        });
        handle.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          const menu = new Menu();
          for (const [q, label] of [
            ["Q1", "Important · Urgent"],
            ["Q2", "Important · Not urgent"],
            ["Q3", "Not important · Urgent"],
            ["Q4", "Not important · Not urgent"],
          ]) {
            menu.addItem((item) =>
              item.setTitle(q + " " + label).onClick(() => moveTask(t, q)),
            );
          }
          const rect = handle.getBoundingClientRect();
          menu.showAtPosition({ x: rect.left, y: rect.bottom });
        });
      }
      if (editable) attachEdit(li, t);
    });
    return view;
  }
  function applyFilter(id) {
    active = id;
    for (const p of pills)
      btns[p.id].setAttribute("aria-pressed", String(active === p.id));
    const matching = asArray(open).filter((t) => taskMatchesArea(t, active));
    const label = pills.find((p) => p.id === active)?.label || active;
    filterStatus.textContent =
      active === "all"
        ? `${matching.length} open`
        : `${matching.filter((t) => domainOf(t) !== null).length} ${label} tasks${unclassified.length ? ` · ${unclassified.length} need an area` : ""}`;
    for (const view of taskViews) {
      let visible = 0;
      for (const { node, task } of view.items) {
        const show = taskMatchesArea(task, active);
        node.hidden = !show;
        if (show) visible++;
      }
      view.empty.hidden = visible > 0;
      view.empty.textContent =
        active === "all" ? "No tasks" : `No ${label} tasks`;
      if (view.count) view.count.textContent = String(visible);
    }
  }
  for (const p of pills) {
    btns[p.id] = seg.createEl("button", {
      text: p.label,
      attr: { type: "button" },
    });
    btns[p.id].addEventListener("click", () => applyFilter(p.id));
  }
  const grid = root.createEl("div", {
    cls: "task-quadrant-grid",
    attr: {
      style: `display:grid;grid-template-columns:${isMobile ? "1fr" : "1fr 1fr"};gap:${isMobile ? "8px" : "10px"};`,
    },
  });
  const quads = [
    {
      id: "Q1",
      list: q1,
      title: "Q1 · Do now",
      subtitle: "Important · Urgent",
      border: "#c4553a",
    },
    {
      id: "Q2",
      list: q2,
      title: "Q2 · Schedule",
      subtitle: "Important · Not urgent",
      border: "var(--interactive-accent)",
    },
    {
      id: "Q3",
      list: q3,
      title: "Q3 · Handle quickly",
      subtitle: "Not important · Urgent",
      border: "var(--text-muted)",
    },
    {
      id: "Q4",
      list: q4,
      title: "Q4 · Later",
      subtitle: "Not important · Not urgent",
      border: "var(--text-faint)",
    },
  ];
  for (const q of quads) {
    const n = q.list.length != null ? q.list.length : asArray(q.list).length;
    const cell = grid.createEl("section", {
      cls: "tb-quadrant",
      attr: {
        style: `--tb-quadrant-accent:${q.border};`,
        "aria-label": q.title,
      },
    });
    cell.setAttribute("data-quadrant", q.id);
    dropCells.push(cell);
    cell.addEventListener("dragover", (e) => {
      if (!dragged || moving) return;
      e.preventDefault();
      e.dataTransfer.dropEffect = "move";
      clearDropHints();
      cell.style.outline = "2px solid var(--interactive-accent)";
      cell.style.background = "var(--background-primary)";
    });
    cell.addEventListener("dragleave", (e) => {
      if (!cell.contains(e.relatedTarget)) clearDropHints();
    });
    cell.addEventListener("drop", (e) => {
      if (!dragged) return;
      e.preventDefault();
      e.stopPropagation();
      const t = dragged;
      dragged = null;
      clearDropHints();
      void moveTask(t, q.id);
    });
    const head = cell.createEl("div", {
      attr: {
        style:
          "display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px;",
      },
    });
    const heading = head.createEl("div");
    heading.createEl("h3", { text: q.title });
    heading.createEl("small", {
      text: q.subtitle,
      cls: "tb-quadrant-subtitle",
    });
    const count = head.createEl("span", {
      text: String(n),
      cls: "tb-count",
      attr: { "aria-label": "Visible tasks" },
    });
    const view = renderTasks(cell.createEl("div"), q.list);
    view.count = count;
  }
  if (unclassified.length) {
    const unCell = root.createEl("section", { cls: "tb-unclassified" });
    unCell.createEl("h3", { text: `Needs an area · ${unclassified.length}` });
    unCell.createEl("p", {
      text: "Choose an area in the task list below. These tasks stay visible in every filter.",
      cls: "tb-quadrant-subtitle",
    });
    renderTasks(unCell.createEl("div"), unclassified);
  }
  const listWrap = root.createEl("section", { cls: "tb-list" });
  listWrap.createEl("h3", { text: "Task list" });
  listWrap.createEl("p", {
    text: "Use Edit to change a task’s title, area, importance, or due date.",
    cls: "tb-quadrant-subtitle",
  });
  renderTasks(listWrap, open, true);
  applyFilter("all");
}
if (typeof dv === "undefined")
  module.exports = { taskDisplayText, taskArea, taskMatchesArea };
else renderTaskBoard(dv, input);

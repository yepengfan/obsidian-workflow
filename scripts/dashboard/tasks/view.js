const app = input.app;
const { Notice, Menu } = input;
const isMobile = app.isMobile;
// ========== TASK BOARD (Eisenhower matrix, vault-wide) ==========
(() => {
  const boardPath = "Tasks/Board.md";
  const fence = String.fromCharCode(96).repeat(3);
  const section = (input.container || dv.container).createEl("div", {
    cls: "task-dashboard-body",
    attr: { style: "margin-bottom:16px;" },
  });
  section.createEl("div", {
    text: "Task quadrants",
    attr: { style: "font-size:0.9em;font-weight:700;margin-bottom:8px;" },
  });

  const inpStyle = `padding:4px 8px;border:1px solid var(--background-modifier-border);border-radius:6px;background:var(--background-primary);color:var(--text-normal);font-size:${isMobile ? "0.78em" : "0.82em"};`;
  const form = section.createEl("div", {
    attr: {
      style:
        "display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:10px;",
    },
  });
  const titleInp = form.createEl("input");
  titleInp.type = "text";
  titleInp.placeholder = "Task title";
  titleInp.setAttribute("aria-label", "Task title");
  titleInp.setAttribute(
    "style",
    inpStyle + `flex:1;min-width:${isMobile ? "100%" : "140px"};`,
  );

  const areas = ["work", "life", "other"];
  let area = "work";
  const areaSeg = form.createEl("div", {
    attr: {
      style:
        "display:inline-flex;gap:2px;padding:2px;border-radius:9px;background:var(--background-secondary);",
    },
  });
  const areaBtns = {};
  function paintArea() {
    for (const a of areas) {
      areaBtns[a].setAttribute("aria-pressed", String(area === a));
      areaBtns[a].style.cssText =
        `padding:${isMobile ? "6px 10px" : "3px 10px"};border-radius:7px;border:none;cursor:pointer;font-size:0.78em;font-weight:600;` +
        (area === a
          ? "background:var(--background-primary);color:var(--text-normal);box-shadow:0 1px 3px rgba(0,0,0,0.08);"
          : "background:transparent;color:var(--text-muted);");
    }
  }
  for (const a of areas) {
    areaBtns[a] = areaSeg.createEl("button", {
      text: a[0].toUpperCase() + a.slice(1),
    });
    areaBtns[a].addEventListener("click", () => {
      area = a;
      paintArea();
    });
  }
  paintArea();

  let important = false;
  const starBtn = form.createEl("button", { text: "⭐" });
  function paintStar() {
    starBtn.style.cssText =
      `padding:${isMobile ? "6px 10px" : "3px 10px"};border-radius:6px;cursor:pointer;font-size:0.82em;border:1px solid ` +
      (important
        ? "var(--interactive-accent)"
        : "var(--background-modifier-border)") +
      ";background:" +
      (important
        ? "var(--interactive-accent)"
        : "var(--background-secondary)") +
      ";color:" +
      (important ? "var(--text-on-accent)" : "var(--text-muted)") +
      ";";
    starBtn.title = important ? "Important" : "Not important";
    starBtn.setAttribute("aria-pressed", String(important));
    starBtn.setAttribute("aria-label", "Mark task important");
  }
  starBtn.addEventListener("click", () => {
    important = !important;
    paintStar();
  });
  paintStar();

  const dueInp = form.createEl("input");
  dueInp.type = "date";
  dueInp.setAttribute("aria-label", "Due date");
  dueInp.title = "Due within 7 days = urgent; no date = not urgent";
  dueInp.setAttribute(
    "style",
    inpStyle + (isMobile ? "padding:6px 10px;" : ""),
  );

  const addBtn = form.createEl("button", { text: "+ Task" });
  addBtn.style.cssText = `padding:${isMobile ? "6px 10px" : "4px 14px"};border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:${isMobile ? "0.78em" : "0.82em"};background:var(--interactive-accent);color:var(--text-on-accent);white-space:nowrap;`;

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
    const urgent = due && dv.date(due) <= today.plus({ days: 7 }).endOf("day");
    const q = important ? (urgent ? "Q1" : "Q2") : urgent ? "Q3" : "Q4";
    new Notice("Added to " + q + " · " + area);
  });
  titleInp.addEventListener("keydown", (e) => {
    if (e.key === "Enter") addBtn.click();
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
  function domainOf(t) {
    const tags = (t.tags || []).map((x) => String(x).replace(/^#/, ""));
    const hit = tags.find((x) => x.startsWith("task/"));
    return hit ? hit.replace(/^task\//, "") : null;
  }
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

  const root = section.createEl("div", {
    attr: { style: "font-size:0.82em;" },
  });
  const pillWrap = root.createEl("div", {
    attr: {
      style:
        "display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:10px;",
    },
  });
  const seg = pillWrap.createEl("div", {
    attr: {
      style:
        "display:inline-flex;gap:2px;padding:2px;border-radius:9px;background:var(--background-secondary);",
    },
  });
  const pills = [
    { id: "all", label: "All" },
    { id: "work", label: "Work" },
    { id: "life", label: "Life" },
    { id: "other", label: "Other" },
  ];
  const btns = {};
  let active = "all";
  const cellBase = `background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:8px;padding:${isMobile ? "8px" : "10px"};min-height:${isMobile ? "56px" : "72px"};`;
  const badgeStyle =
    "font-size:0.72em;padding:1px 7px;border-radius:10px;background:var(--background-primary);border:1px solid var(--background-modifier-border);color:var(--text-muted);white-space:nowrap;";
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
          "。" +
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
  root.createEl("div", {
    text: "Drag ⋮⋮ to move a task, or click it to choose a quadrant. Urgent sets a date within 7 days. Not urgent clears an urgent date.",
    attr: {
      style: "color:var(--text-muted);font-size:0.85em;margin-bottom:8px;",
    },
  });

  function attachEdit(li, t) {
    const editBtn = li.createEl("button", { text: "✎" });
    editBtn.setAttribute(
      "style",
      isMobile
        ? "margin-left:6px;border:none;background:transparent;cursor:pointer;color:var(--text-faint);font-size:0.95em;padding:6px 8px;"
        : "margin-left:6px;border:none;background:transparent;cursor:pointer;color:var(--text-faint);font-size:0.82em;",
    );
    editBtn.title = "Edit";
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
        "border:1px solid var(--background-modifier-border);border-radius:6px;background:var(--background-primary);color:var(--text-normal);font-size:0.82em;";
      const drawer = li.createEl("div", {
        cls: "tb-editor",
        attr: {
          style:
            "display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:6px 0;padding:6px;border:1px solid var(--background-modifier-border);border-radius:8px;background:var(--background-primary);",
        },
      });
      const tIn = drawer.createEl("input");
      tIn.type = "text";
      tIn.value = curTitle;
      tIn.setAttribute(
        "style",
        inpStyle2 + "flex:1;min-width:" + (isMobile ? "100%" : "120px") + ";",
      );

      const areaOpts = ["work", "life", "other", "none"];
      const aSeg = drawer.createEl("div", {
        attr: {
          style:
            "display:inline-flex;gap:2px;padding:2px;border-radius:9px;background:var(--background-secondary);",
        },
      });
      const aBtns = {};
      let areaSel = curArea || "none";
      function paintA() {
        for (const a of areaOpts) {
          aBtns[a].style.cssText =
            (isMobile ? "padding:6px 10px;" : "padding:3px 8px;") +
            "border-radius:7px;border:none;cursor:pointer;font-size:0.74em;font-weight:600;" +
            (areaSel === a
              ? "background:var(--background-primary);color:var(--text-normal);box-shadow:0 1px 3px rgba(0,0,0,0.08);"
              : "background:transparent;color:var(--text-muted);");
        }
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

      const sBtn = drawer.createEl("button", { text: "⭐" });
      function paintS() {
        sBtn.style.cssText =
          "padding:3px 9px;border-radius:6px;cursor:pointer;font-size:0.82em;border:1px solid " +
          (curImp
            ? "var(--interactive-accent)"
            : "var(--background-modifier-border)") +
          ";background:" +
          (curImp
            ? "var(--interactive-accent)"
            : "var(--background-secondary)") +
          ";color:" +
          (curImp ? "var(--text-on-accent)" : "var(--text-muted)") +
          ";";
      }
      sBtn.addEventListener("click", () => {
        curImp = !curImp;
        paintS();
      });
      paintS();

      const dIn = drawer.createEl("input");
      dIn.type = "date";
      dIn.value = curDue;
      dIn.title = "Due within 7 days = urgent; no date = not urgent";
      dIn.setAttribute("style", inpStyle2);

      const saveBtn = drawer.createEl("button", { text: "Save" });
      saveBtn.style.cssText =
        (isMobile ? "padding:6px 12px;" : "padding:3px 12px;") +
        "border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:0.78em;background:var(--interactive-accent);color:var(--text-on-accent);";
      const delBtn = drawer.createEl("button", { text: "Delete" });
      delBtn.style.cssText =
        (isMobile ? "padding:6px 12px;" : "padding:3px 10px;") +
        "border:1px solid var(--background-modifier-border);border-radius:6px;cursor:pointer;font-size:0.78em;background:var(--background-secondary);color:var(--text-error, #c4553a);";
      const cancelBtn = drawer.createEl("button", { text: "Cancel" });
      cancelBtn.style.cssText =
        (isMobile ? "padding:6px 12px;" : "padding:3px 10px;") +
        "border:1px solid var(--background-modifier-border);border-radius:6px;cursor:pointer;font-size:0.78em;background:var(--background-secondary);color:var(--text-muted);";

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

  function renderTasks(hostEl, list, withDomainFilter, editable = false) {
    const arr = asArray(list);
    const n = list.length != null ? list.length : arr.length;
    if (n === 0) {
      hostEl.createEl("div", {
        text: "No tasks",
        attr: { style: "color:var(--text-faint);" },
      });
      return;
    }
    const start = dv.container.childElementCount;
    // Render each task once; nested tasks can belong to a different quadrant.
    dv.taskList(
      arr.map((t) => ({ ...t, parent: null, children: [] })),
      false,
    );
    const nodes = Array.from(dv.container.children).slice(start);
    for (const node of nodes) hostEl.appendChild(node);
    const items = hostEl.querySelectorAll("li.dataview.task-list-item");
    items.forEach((li, i) => {
      const t = arr[i];
      if (!t) return;
      const d = domainOf(t);
      if (withDomainFilter) li.setAttribute("data-domain", d || "");
      const meta = [];
      if (t.due) {
        const dd = dv.date(t.due);
        if (dd) meta.push(dd.toFormat("yyyy-MM-dd"));
      }
      if (d) meta.push(d);
      if (meta.length)
        li.createEl("span", {
          text: meta.join(" · "),
          attr: {
            style: "margin-left:8px;font-size:0.72em;color:var(--text-muted);",
          },
        });
      if (d && !editable) {
        // Reserve a right-hand column across every wrapped line of the task.
        li.style.position = "relative";
        li.style.paddingRight = "44px";
        li.style.minHeight = "36px";
        const handle = li.createEl("button", {
          text: "⋮⋮",
          attr: {
            "aria-label": "Move task to quadrant",
            title: "Drag to a quadrant, or click to choose",
            style:
              "position:absolute;top:0;right:0;bottom:0;width:36px;height:auto;min-height:36px;display:flex;align-items:center;justify-content:center;cursor:grab;border:none;border-left:1px solid var(--background-modifier-border);border-radius:0 6px 6px 0;background:transparent;color:var(--text-muted);padding:0;margin:0;box-shadow:none;",
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
  }
  function paintPills() {
    for (const p of pills) {
      btns[p.id].style.cssText =
        `padding:${isMobile ? "3px 10px" : "4px 14px"};border-radius:7px;border:none;cursor:pointer;font-size:${isMobile ? "0.78em" : "0.82em"};font-weight:600;transition:all 0.15s;` +
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
      el.style.display = id === "all" || d === id ? "" : "none";
    }
  }
  for (const p of pills) {
    btns[p.id] = seg.createEl("button", { text: p.label });
    btns[p.id].addEventListener("click", () => applyFilter(p.id));
  }
  paintPills();
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
      title: isMobile ? "Q1 Important · Urgent" : "Q1 Important · Urgent",
      border: "#c4553a",
    },
    {
      id: "Q2",
      list: q2,
      title: isMobile
        ? "Q2 Important · Not urgent"
        : "Q2 Important · Not urgent",
      border: "var(--interactive-accent)",
    },
    {
      id: "Q3",
      list: q3,
      title: isMobile
        ? "Q3 Not important · Urgent"
        : "Q3 Not important · Urgent",
      border: "var(--text-muted)",
    },
    {
      id: "Q4",
      list: q4,
      title: isMobile
        ? "Q4 Not important · Not urgent"
        : "Q4 Not important · Not urgent",
      border: "var(--text-faint)",
    },
  ];
  for (const q of quads) {
    const n = q.list.length != null ? q.list.length : asArray(q.list).length;
    const cell = grid.createEl("div", {
      attr: { style: cellBase + `border-left:3px solid ${q.border};` },
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
    head.createEl("div", {
      text: q.title,
      attr: { style: "font-weight:600;color:var(--text-normal);" },
    });
    head.createEl("span", { text: String(n), attr: { style: badgeStyle } });
    renderTasks(cell.createEl("div", ""), q.list, true);
  }
  const unN =
    unclassified.length != null
      ? unclassified.length
      : asArray(unclassified).length;
  const unCell = root.createEl("div", {
    attr: { style: cellBase + "margin-top:10px;" },
  });
  const unHead = unCell.createEl("div", {
    attr: {
      style:
        "display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px;",
    },
  });
  unHead.createEl("div", {
    text: "Unclassified",
    attr: { style: "font-weight:600;color:var(--text-normal);" },
  });
  unHead.createEl("span", { text: String(unN), attr: { style: badgeStyle } });
  renderTasks(unCell.createEl("div", ""), unclassified, false);
  const n1 = q1.length != null ? q1.length : asArray(q1).length;
  const n2 = q2.length != null ? q2.length : asArray(q2).length;
  const n3 = q3.length != null ? q3.length : asArray(q3).length;
  const n4 = q4.length != null ? q4.length : asArray(q4).length;
  root.createEl("div", {
    text: `Q1 ${n1} · Q2 ${n2} · Q3 ${n3} · Q4 ${n4} · Unclassified ${unN}`,
    attr: {
      style: "margin-top:10px;color:var(--text-muted);font-size:0.82em;",
    },
  });
  if (n2 === 0 && n1 >= 1)
    root.createEl("div", {
      text: "Q1 is filling up. Reserve time for important tasks in Q2.",
      attr: {
        style: "margin-top:4px;color:var(--text-faint);font-size:0.82em;",
      },
    });
  const listWrap = root.createEl("div", {
    attr: {
      style:
        "margin-top:16px;border-top:1px solid var(--background-modifier-border);padding-top:10px;",
    },
  });
  listWrap.createEl("h3", { text: "Task list · click ✎ to edit" });
  renderTasks(listWrap, open, false, true);
})();

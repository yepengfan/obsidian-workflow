---
date: {{date:YYYY-MM-DD}}
day: {{date:dddd}}
tags: work-daily
---

# {{date:YYYY-MM-DD}} {{date:dddd}}

## Tasks

```dataviewjs
const file = app.workspace.getActiveFile();
const config = dv.page("Work/Projects");
const projects = (config?.projects || []).map(String);
const prios = [
  { e: "🔴", l: "Urgent" }, { e: "🟠", l: "High" },
  { e: "🟡", l: "Medium" }, { e: "🟢", l: "Low" },
];
let sel = projects[0] || "";

const w = dv.container.createEl("div", {
  attr: { style: "display:flex;align-items:center;gap:6px;flex-wrap:wrap;padding:4px 0;" }
});

// Project selector
const pbs = [];
for (const p of projects) {
  const a = p === sel;
  const b = w.createEl("button", { text: p, attr: {
    style: `padding:3px 12px;border-radius:6px;font-size:0.82em;font-weight:600;cursor:pointer;border:1px solid ${a ? "var(--interactive-accent)" : "var(--background-modifier-border)"};background:${a ? "var(--interactive-accent)" : "var(--background-secondary)"};color:${a ? "var(--text-on-accent)" : "var(--text-normal)"};`
  }});
  pbs.push({ b, p });
  b.addEventListener("click", () => {
    sel = p;
    pbs.forEach(x => {
      const on = x.p === p;
      x.b.style.background = on ? "var(--interactive-accent)" : "var(--background-secondary)";
      x.b.style.color = on ? "var(--text-on-accent)" : "var(--text-normal)";
      x.b.style.borderColor = on ? "var(--interactive-accent)" : "var(--background-modifier-border)";
    });
  });
}

w.createEl("span", { text: "│", attr: { style: "color:var(--text-faint);" } });

// Priority buttons — click to insert task under selected project
for (const pr of prios) {
  const b = w.createEl("button", { text: pr.e + " " + pr.l, attr: {
    title: pr.l,
    style: "padding:3px 10px;border-radius:6px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.82em;"
  }});
  b.addEventListener("click", async () => {
    if (!sel || !file) return;
    const content = await app.vault.read(file);
    const lines = content.split("\n");
    const task = "- [ ] " + pr.e + " ";
    let target;

    let headIdx = -1;
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].trim() === "### " + sel) { headIdx = i; break; }
    }

    if (headIdx >= 0) {
      let ins = headIdx + 1, repl = -1;
      for (let j = headIdx + 1; j < lines.length; j++) {
        const t = lines[j].trim();
        if (t.startsWith("### ") || t.startsWith("## ")) break;
        if (t === "- [ ]" && repl < 0) repl = j;
        ins = j;
      }
      if (repl >= 0) {
        lines[repl] = lines[repl].replace("- [ ]", task);
        target = repl;
      } else {
        lines.splice(ins + 1, 0, task);
        target = ins + 1;
      }
    } else {
      let noteIdx = lines.length;
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].trim() === "## Notes") { noteIdx = i; break; }
      }
      lines.splice(noteIdx, 0, "### " + sel, "", task, "");
      target = noteIdx + 2;
    }

    await app.vault.modify(file, lines.join("\n"));
    setTimeout(() => {
      const ed = app.workspace.activeLeaf?.view?.editor;
      if (ed) { ed.setCursor({ line: target, ch: task.length }); ed.focus(); }
    }, 150);
    new Notice("Added " + pr.e + " " + pr.l + " task to " + sel);
  });
}
```

### IS2

- [ ]

## Notes


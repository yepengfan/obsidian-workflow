---
tags: [zettel]
created: {{date}}
source: ""
status: seedling
topics: []
---

# {{title}}



---

Related::

```dataviewjs
const p = dv.current();
if (p.status === "growing") {
  const wrap = dv.el("div", "", { attr: { style: "margin-top:14px;" } });
  const btn = wrap.createEl("button", {
    text: "\ud83c\udf33 Mark as Evergreen",
    attr: { style: "padding:5px 14px;border:1px solid var(--color-green);border-radius:6px;background:none;color:var(--color-green);cursor:pointer;font-size:0.82em;transition:all 0.15s;" }
  });
  btn.addEventListener("click", async () => {
    const tFile = app.vault.getAbstractFileByPath(p.file.path);
    if (!tFile) return;
    await app.fileManager.processFrontMatter(tFile, fm => { fm.status = "evergreen"; });
    btn.textContent = "\u2713 Marked as Evergreen";
    btn.disabled = true;
    btn.style.opacity = "0.5";
    btn.style.cursor = "default";
  });
}
```

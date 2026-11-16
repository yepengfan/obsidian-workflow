const app = input.app;
dv.header(2, "文章收藏");
const articles = [
  ...dv.pages('"Matter"'),
  ...dv.pages('"Instapaper Notes"'),
].filter((p) => !["Matter Index", "Instapaper Index"].includes(p.file.name));
const source = dv.el("select", "", { attr: { "aria-label": "文章来源" } });
for (const [value, text] of [
  ["all", "全部来源"],
  ["Matter/", "Matter"],
  ["Instapaper Notes/", "Instapaper"],
])
  source.createEl("option", { text, attr: { value } });
const list = dv.el("div", "");
function render() {
  list.empty();
  const rows = articles
    .filter(
      (p) => source.value === "all" || p.file.path.startsWith(source.value),
    )
    .sort((a, b) => b.file.mtime - a.file.mtime);
  for (const p of rows) {
    const row = list.createEl("div", {
      attr: {
        style:
          "padding:8px 0;border-bottom:1px solid var(--background-modifier-border);",
      },
    });
    const a = row.createEl("a", {
      text: p.file.name,
      attr: {
        href: p.file.path,
        class: "internal-link",
        "data-href": p.file.path,
      },
    });
    a.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      void app.workspace.openLinkText(p.file.path, "", false);
    });
  }
  if (!rows.length) list.createEl("p", { text: "当前没有收藏文章。" });
}
source.addEventListener("change", render);
render();
dv.paragraph(
  "[[Matter/Matter Index|Matter 索引]] · [[Instapaper Notes/Instapaper Index|Instapaper 索引]]",
);

---
tags: [MOC]
cssclasses: [wide-page]
---

> 🏠 [[Home]]

# Books Index

## Currently Reading

```dataviewjs
const fmt = (d) => d ? dv.date(d).toFormat("yyyy-MM-dd") : "";
const pages = dv.pages('"Learning/Books"')
  .where(p => p.file.name === "meta" && p.status === "reading")
  .sort(p => p.started, "desc");
const rows = pages.map(p => {
  const moc = dv.page(p.file.folder + "/MOC");
  const link = moc ? dv.fileLink(moc.file.path, false, p.title) : p.file.link;
  return [link, p.author, p.archetype, fmt(p.started)];
});
dv.table(["Book", "Author", "Archetype", "Started"], rows);
```

## Finished

```dataviewjs
const fmt = (d) => d ? dv.date(d).toFormat("yyyy-MM-dd") : "";
const pages = dv.pages('"Learning/Books"')
  .where(p => p.file.name === "meta" && p.status === "finished")
  .sort(p => p.finished, "desc");
const rows = pages.map(p => {
  const moc = dv.page(p.file.folder + "/MOC");
  const link = moc ? dv.fileLink(moc.file.path, false, p.title) : p.file.link;
  return [link, p.author, p.archetype, fmt(p.started), fmt(p.finished)];
});
if (rows.length > 0) dv.table(["Book", "Author", "Archetype", "Started", "Finished"], rows);
else dv.paragraph("*No finished books yet.*");
```

## Paused

```dataviewjs
const fmt = (d) => d ? dv.date(d).toFormat("yyyy-MM-dd") : "";
const pages = dv.pages('"Learning/Books"')
  .where(p => p.file.name === "meta" && p.status === "paused")
  .sort(p => p.started, "desc");
const rows = pages.map(p => {
  const moc = dv.page(p.file.folder + "/MOC");
  const link = moc ? dv.fileLink(moc.file.path, false, p.title) : p.file.link;
  return [link, p.author, p.archetype, fmt(p.started)];
});
if (rows.length > 0) dv.table(["Book", "Author", "Archetype", "Started"], rows);
else dv.paragraph("*No paused books.*");
```

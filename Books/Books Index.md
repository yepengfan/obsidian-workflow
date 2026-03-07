---
tags: [MOC]
cssclasses: [wide-page]
---

# Books Index

## Currently Reading

```dataviewjs
const fmt = (d) => d ? dv.date(d).toFormat("yyyy-MM-dd") : "";
const pages = dv.pages('"Books"').where(p => p.file.name === "00_meta" && p.status === "reading").sort(p => p.started, "desc");
const rows = pages.map(p => {
  const mapFile = dv.page(p.file.folder + "/00_map");
  const link = mapFile ? dv.fileLink(mapFile.file.path, false, p.title) : p.file.link;
  return [link, p.author, fmt(p.started)];
});
dv.table(["Book", "Author", "Started"], rows);
```

## Finished

```dataviewjs
const fmt = (d) => d ? dv.date(d).toFormat("yyyy-MM-dd") : "";
const pages = dv.pages('"Books"').where(p => p.file.name === "00_meta" && p.status === "finished").sort(p => p.finished, "desc");
const rows = pages.map(p => {
  const mapFile = dv.page(p.file.folder + "/00_map");
  const link = mapFile ? dv.fileLink(mapFile.file.path, false, p.title) : p.file.link;
  return [link, p.author, fmt(p.started), fmt(p.finished)];
});
if (rows.length > 0) dv.table(["Book", "Author", "Started", "Finished"], rows);
else dv.paragraph("*No finished books yet.*");
```

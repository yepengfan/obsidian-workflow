---
tags: [leetcode/index]
---

# Algorithm Pattern Library

## Overview

```dataviewjs
await dv.view("scripts/dashboard/algorithm", { app });
```


[Weekly View →](Learning/Practice/Algorithm/Weekly%20View.md)

## 🗂 Patterns by Category

```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Pattern",
  category AS "Category",
  length(problems) AS "Problems",
  updated AS "Updated"
FROM "Learning/Practice/Algorithm/Patterns"
WHERE contains(file.tags, "#leetcode/pattern")
SORT category ASC, id ASC
```

## 🧬 Atoms（跨 pattern 复用的原子技术）

```dataviewjs
const atoms = dv.pages('"Learning/Practice/Algorithm/Atoms"').where(p => p.file.tags.includes("#leetcode/atom"));

if (atoms.length === 0) {
  dv.paragraph("_(暂无 atom card)_");
} else {
  dv.table(
    ["Atom", "Used By", "Updated"],
    atoms.array().map(p => [
      p.file.link,
      p.file.inlinks.length,
      p.updated
    ])
  );
}
```

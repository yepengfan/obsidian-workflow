---
type: atom
title: "{{title}}"
tags: [leetcode/atom]
created: {{date}}
updated: {{date}}
---

# {{title}}

## Insight



## Template

```python

```

## Used By

```dataviewjs
const inlinks = dv.current().file.inlinks;
if (inlinks.length === 0) {
  dv.paragraph("_(暂无 pattern card 引用此原子)_");
} else {
  dv.list(inlinks.map(l => l.markdown()));
}
```

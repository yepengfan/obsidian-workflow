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

<!-- 可选：仅当原子有清晰、可直接复用的代码骨架时才填写；偏概念/设计类的原子可以删除这一节。 -->

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

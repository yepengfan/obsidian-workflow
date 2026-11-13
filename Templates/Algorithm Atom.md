---
type: atom
title: "{{title}}"
tags: [leetcode/atom]
created: {{date}}
updated: {{date}}
---

# {{title}}

## Insight

<!-- Explain the independently reusable technique, the capability it provides, and its prerequisites without relying on a particular problem. Keep learner-specific evidence in logs. -->

## Template

<!-- Optional: include a clear, directly reusable code skeleton. Remove this section for conceptual or design-oriented atoms without one. -->

```python

```

## Used By

```dataviewjs
const inlinks = dv.current().file.inlinks;
if (inlinks.length === 0) {
  dv.paragraph("_(No pattern cards reference this atom yet)_");
} else {
  dv.list(inlinks.map(l => l.markdown()));
}
```

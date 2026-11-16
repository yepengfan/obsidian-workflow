---
tags: [system-design/index]
---

# System Design Pattern Library

## Overview

```dataviewjs
await dv.view("scripts/dashboard/system-design", { app });
```


## 🗂 Patterns by Category

```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Pattern",
  category AS "Category",
  length(problems) AS "Problems",
  updated AS "Updated"
FROM "Learning/Practice/System-Design/Patterns"
WHERE contains(file.tags, "#system-design/pattern")
SORT category ASC, id ASC
```

## 📚 学习资源

### 课程
- Hello Interview — 主线课程

### 练习平台
- [Codemia](https://codemia.io/) — SD 刷题平台（LeetCode 式系统设计练习，120+ 题 + 多角度题解）

### 关联
- [[../Algorithm/00_index|Algorithm]] — LeetCode 刷题系统

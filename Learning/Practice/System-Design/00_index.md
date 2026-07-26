---
tags: [system-design/index]
---

# System Design Pattern Library

## 📊 Stats

```dataviewjs
const patterns = dv.pages('"Learning/System-Design/Patterns"').where(p => p.file.tags.includes("#system-design/pattern"));
const logs = dv.pages('"Learning/System-Design/Log"').where(p => p.file.tags.includes("#system-design/log"));

const totalPatterns = patterns.length;
const pArr = patterns.array();
const totalProblems = pArr.reduce((sum, p) => sum + (p.problems ? (Array.isArray(p.problems) ? p.problems.length : 1) : 0), 0);

const weekAgo = dv.date("today").minus({ days: 7 });
const monthAgo = dv.date("today").minus({ days: 30 });

const lArr = logs.array();
const weekProblems = lArr.filter(l => dv.date(l.date) >= weekAgo).reduce((sum, l) => sum + (l.problems_solved ? (Array.isArray(l.problems_solved) ? l.problems_solved.length : 1) : 0), 0);
const monthProblems = lArr.filter(l => dv.date(l.date) >= monthAgo).reduce((sum, l) => sum + (l.problems_solved ? (Array.isArray(l.problems_solved) ? l.problems_solved.length : 1) : 0), 0);

dv.paragraph(`**${totalPatterns}** patterns · **${totalProblems}** problems covered · 本周 **${weekProblems}** 题 · 本月 **${monthProblems}** 题`);
```

## 🗂 Patterns by Category

```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Pattern",
  category AS "Category",
  length(problems) AS "Problems",
  updated AS "Updated"
FROM "Learning/System-Design/Patterns"
WHERE contains(file.tags, "#system-design/pattern")
SORT category ASC, id ASC
```

## 🔴 需要复习 (30+ 天未更新)

```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Pattern",
  category AS "Category",
  updated AS "Last Updated"
FROM "Learning/System-Design/Patterns"
WHERE contains(file.tags, "#system-design/pattern") AND updated <= date(today) - dur(30 days)
SORT updated ASC
```

## 📝 待练清单

> 添加想练习的 SD 题目

- [ ] Design URL Shortener（入门）
- [ ] Design Rate Limiter（入门）
- [ ] Design News Feed（中级）
- [ ] Design Chat System（中级）
- [ ] Design YouTube（高级）

## 📚 学习资源

### 课程
- Hello Interview — 主线课程

### 练习平台
- [Codemia](https://codemia.io/) — SD 刷题平台（LeetCode 式系统设计练习，120+ 题 + 多角度题解）

### 关联
- [[../SYSD/00_plan|SYSD]] — 实战项目（Docker POC + 生产深度）
- [[../Algorithm/00_index|Algorithm]] — LeetCode 刷题系统

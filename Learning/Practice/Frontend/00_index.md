---
tags: [frontend/index]
---

# Frontend Pattern Library

## 📊 Stats

```dataviewjs
const patterns = dv.pages('"Learning/Practice/Frontend/Patterns"').where(p => p.file.tags.includes("#frontend/pattern"));
const logs = dv.pages('"Learning/Practice/Frontend/Log"').where(p => p.file.tags.includes("#frontend/log"));

const totalPatterns = patterns.length;
const pArr = patterns.array();
const totalProblems = pArr.reduce((sum, p) => sum + (p.problems ? (Array.isArray(p.problems) ? p.problems.length : 1) : 0), 0);

const todayD = dv.date("today");
const weekStart = todayD.weekday === 1 ? todayD : todayD.minus({ days: todayD.weekday - 1 });
const lastMonthStart = todayD.set({ day: 1 }).minus({ months: 1 });
const lastMonthEnd = todayD.set({ day: 1 }).minus({ days: 1 });

const lArr = logs.array();
const weekProblems = lArr.filter(l => dv.date(l.date) >= weekStart).reduce((sum, l) => sum + (l.challenges_completed ? (Array.isArray(l.challenges_completed) ? l.challenges_completed.length : 1) : 0), 0);
const lastMonthProblems = lArr.filter(l => { const d = dv.date(l.date); return d >= lastMonthStart && d <= lastMonthEnd; }).reduce((sum, l) => sum + (l.challenges_completed ? (Array.isArray(l.challenges_completed) ? l.challenges_completed.length : 1) : 0), 0);

dv.paragraph(`**${totalPatterns}** patterns · **${totalProblems}** challenges covered · 本周 **${weekProblems}** 题 · 上月 **${lastMonthProblems}** 题`);
```

## 🗂 Patterns by Category

```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Pattern",
  category AS "Category",
  length(problems) AS "Problems",
  updated AS "Updated"
FROM "Learning/Practice/Frontend/Patterns"
WHERE contains(file.tags, "#frontend/pattern")
SORT category ASC, id ASC
```

## 🔴 需要复习 (30+ 天未更新)

```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Pattern",
  category AS "Category",
  updated AS "Last Updated"
FROM "Learning/Practice/Frontend/Patterns"
WHERE contains(file.tags, "#frontend/pattern") AND updated <= date(today) - dur(30 days)
SORT updated ASC
```

## 📝 待练清单

> 添加想练习的 GFE 题目

### UI Components
- [ ] Accordion
- [ ] Tabs
- [ ] Star Rating
- [ ] Modal Dialog
- [ ] Autocomplete / Typeahead

### JS Utilities
- [ ] debounce
- [ ] throttle
- [ ] Promise.all
- [ ] deepClone
- [ ] curry

### Frontend System Design
- [ ] Autocomplete System
- [ ] Image Carousel
- [ ] News Feed

## 📚 学习资源

### 练习平台
- [GreatFrontEnd](https://www.greatfrontend.com/) — 主线题源

### 关联
- [[../../Algorithm/00_index|Algorithm]] — LeetCode 刷题系统
- [[../../System-Design/00_index|System Design]] — 系统设计练习

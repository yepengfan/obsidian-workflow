---
tags: [grammar/index]
---

# Expressive Grammar Library

## 📊 Stats

```dataviewjs
const structures = dv.pages('"Learning/Grammar/Structures"').where(p => p.file.tags.includes("#grammar/expressive"));
const logs = dv.pages('"Learning/Grammar/Log"').where(p => p.file.tags.includes("#grammar/log"));

const totalStructures = structures.length;
const sArr = structures.array();
const totalExamples = sArr.reduce((sum, s) => sum + (s.examples_count || 0), 0);

const weekAgo = dv.date("today").minus({ days: 7 });
const monthAgo = dv.date("today").minus({ days: 30 });

const lArr = logs.array();
const weekPractice = lArr.filter(l => dv.date(l.date) >= weekAgo).reduce((sum, l) => sum + (l.structures_practiced ? (Array.isArray(l.structures_practiced) ? l.structures_practiced.length : 1) : 0), 0);
const monthPractice = lArr.filter(l => dv.date(l.date) >= monthAgo).reduce((sum, l) => sum + (l.structures_practiced ? (Array.isArray(l.structures_practiced) ? l.structures_practiced.length : 1) : 0), 0);

dv.paragraph(`**${totalStructures}** structures · **${totalExamples}** examples · 本周 **${weekPractice}** 次练习 · 本月 **${monthPractice}** 次练习`);
```

## 🗂 All Structures

```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Structure",
  difficulty AS "Difficulty",
  examples_count AS "Examples",
  updated AS "Last Practiced"
FROM "Learning/Grammar/Structures"
WHERE contains(file.tags, "#grammar/expressive")
SORT updated ASC
```

## 🔴 需要练习 (最久未更新)

```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Structure",
  updated AS "Last Practiced",
  examples_count AS "Examples"
FROM "Learning/Grammar/Structures"
WHERE contains(file.tags, "#grammar/expressive")
SORT updated ASC
LIMIT 5
```

## 📋 Priority Structures (from Plan)

- [x] Graded Modals — calibrating certainty and commitment
- [x] Cleft Sentences — controlling emphasis and attention
- [x] Participle Clauses — packing ideas with clear hierarchy
- [ ] Full Conditional Spectrum — mixed/inverted conditionals, `were to`
- [ ] Nominalisation — compressing verbs/clauses into noun phrases

## 📝 Recent Practice

```dataview
TABLE WITHOUT ID
  link(file.link, date) AS "Date",
  structures_practiced AS "Structures"
FROM "Learning/Grammar/Log"
WHERE contains(file.tags, "#grammar/log")
SORT date DESC
LIMIT 10
```

## 🎯 Workflow

```
练习 → /grammar/practice cleft sentences
         ↓
    Phase 1: 选结构 + 回顾功能
    Phase 2: 用自己的句子重写（Socratic 引导）
    Phase 3: 沉淀 structure card + examples
    Phase 4: 写 log
         ↓
复习 → /grammar/review
         ↓
    挑最久未练的 structure 再练 → 循环
```

## 📚 Reference Books

- [[Practical English Usage (Michael Swan).pdf|Practical English Usage (Swan)]] — lookup reference
- [[Advanced Grammar in Use - Martin Hewings.pdf|Advanced Grammar in Use (Hewings)]] — selective workbook

**Plan:** [[00 Expressive Grammar — Plan & Workflow]]

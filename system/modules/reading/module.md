---
module: reading
label: "Reading 外部阅读"
type: knowledge
status: active
enabled: true
created: 2026-03-29
updated: 2026-03-29
depends_on: []
commands: []
templates: []
scripts: []
hooks: []
folders: [Reading/Matter/, Reading/Instapaper/]
config_files: []
tags: [system/module]
---

# Reading 外部阅读

## Overview
外部文章阅读来源的聚合。被动同步的高亮和笔记，不同于主动创建的 Zettelkasten 或 Books。

## 架构

```
Reading/
├── Matter/             # Matter app 文章笔记
│   └── Matter Index.md
└── Instapaper/         # Instapaper 文章高亮
    └── Instapaper Index.md
```

### 数据流
- **输入**: Matter app / Instapaper 自动同步
- **输出**: 阅读中的洞察可通过 `/zettelkasten/zettel` 提取为永久笔记

## 配置位置
| 组件 | 位置 |
|------|------|
| Matter 索引 | `Reading/Matter/Matter Index.md` |
| Instapaper 索引 | `Reading/Instapaper/Instapaper Index.md` |

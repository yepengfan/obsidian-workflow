---
module: task-board
label: "Task Board 要事第一"
type: utility
status: active
enabled: true
created: 2026-09-14
updated: 2026-09-14
depends_on: []
requires:
  cli: [claude]
  plugins: [dataview]
commands: [task-board, task-add]
templates: [Templates/Task Board.md]
scripts: []
hooks: []
folders: [Tasks/]
config_files:
  - .claude/skills/task-board/SKILL.md
  - .claude/skills/task-add/SKILL.md
tags: [system/module]
---

# Task Board 要事第一

## Overview
全库 Covey / Eisenhower 2×2 任务板：Important（人工 ⭐）× Urgent（由 Dataview `due` 推导 📅）。v1 不摄入 Work 日记任务。

## 架构

```
Tasks/
└── Board.md                 # 活页（gitignore）— source of truth 在 ## Tasks
Templates/Task Board.md      # git 内模板
```

象限规则（Important × Urgent）：

| | Urgent | Not urgent |
|---|---|---|
| Important (⭐) | Q1 | Q2 |
| Not important | Q3 | Q4 |

- **Urgent**：任务行有 Dataview `due` **且** due date ≤ today + 7 个日历日（从今天起一周内，含过期）。无 due → 不紧急。
- **Important**：任务行有 ⭐。无 ⭐ → 不重要（有 domain tag 时：紧急进 Q3，不紧急进 Q4）。
- **Domain tags**（写在**任务行**上，不是 file tags）：`#task/work` `#task/life` `#task/other`，可扩展 `#task/<area>`。
- **Unclassified**：缺 `#task/...` → 永不倒进 Q4。
- **v1**：不从 Work daily notes 摄入任务。

### 数据流
- **添加**: `/task-add` → 追加一条任务到 `Tasks/Board.md` 的 `## Tasks`
- **整理**: `/task-board` → 全景、分类、重排象限
- **任务行格式**: `- [ ] ⭐ 📅 YYYY-MM-DD 标题 #task/work|life|other`

## Quick Start

1. **打开看板** → Home 的 Work tab（默认）直接显示四象限；或顶栏 Task Board 打开 `Tasks/Board.md`
2. **加一条任务** → Home 标题栏填标题，选 Work/Life/Other，可选 ⭐ 和 due，点 `+ Task`（或 `/task-add`）
3. **改现有任务** → Home 点任务 → 打开 Task Board → 在下方「任务列表」区点条目后的 `✎` 改标题/领域/⭐/due 或删除，自动重新分桶（上方矩阵只做可视化）
4. **分类重排** → `/task-board` — 补未分类、改 ⭐/📅

**日常节奏**: `/task-add` 捕获 → `/task-board` 把要事放到 Q1/Q2

## 配置位置
| 组件 | 位置 |
|------|------|
| 命令定义 | `.claude/skills/task-board/SKILL.md` |
| 命令定义 | `.claude/skills/task-add/SKILL.md` |
| 模板 | `Templates/Task Board.md` |
| 活页 | `Tasks/Board.md`（gitignore） |

---
🏠 [[Home]] · 📊 [[system/registry|Registry]] · 🚀 [[GETTING_STARTED|Getting Started]]

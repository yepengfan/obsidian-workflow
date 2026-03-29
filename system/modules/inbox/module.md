---
module: inbox
label: "Inbox 捕获层"
type: knowledge
status: active
enabled: true
created: 2026-03-29
updated: 2026-03-29
depends_on: []
commands: []
templates: [Templates/Inbox.md]
scripts: []
hooks: []
folders: [Inbox/, Inbox/archive/]
config_files: []
tags: [system/module]
---

# Inbox 捕获层

## Overview
零摩擦捕获层。快速记录闪念，不需要任何格式。每周通过 `/inbox-review` 处理：转为 zettel 或归档。

## 架构

```
Inbox/
├── *.md                    # 活跃闪念笔记
└── archive/
    └── YYYY-MM/            # 已处理的归档笔记
```

### 数据流
- **输入**: Home.md 快速捕获按钮、随时手动创建
- **处理**: `/inbox-review` → 逐条审查 → 转为 zettel（确认后）/ 归档到 `Inbox/archive/YYYY-MM/` / 跳过
- **输出**: Zettelkasten 永久笔记 或 归档

### 核心规则
- 不需要格式，capture first
- 什么都可以放（阅读感想、工作灵感、生活想法）
- 每周处理，不积压

## 配置位置
| 组件 | 位置 |
|------|------|
| 命令定义 | `.claude/commands/inbox-review.md` |
| 模板 | `Templates/Inbox.md` |

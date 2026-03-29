---
module: brownbag
label: "Brownbag 分享会"
type: work
status: active
created: 2026-03-29
updated: 2026-03-29
depends_on: [work]
commands: [brownbag]
templates: [Templates/Brownbag Session.md]
scripts: []
hooks: []
folders: [Work/Brownbag Sessions/]
config_files:
  - .claude/commands/brownbag.md
tags: [system/module]
---

# Brownbag 分享会

## Overview
Brownbag 技术分享会管理。每个 session 有唯一 ID（BB-N），通过验收标准清单自动推断状态。

## 架构

```
Work/Brownbag Sessions/
├── Brownbag Sessions.md     # 索引（所有 session 列表）
└── <Topic>/
    └── <Topic>.md           # Session 笔记（验收标准清单）
```

### 数据流
- **创建**: `/brownbag <topic>` → 自动分配下一个 BB-N ID → 创建子文件夹 + 笔记
- **状态追踪**: 自动从 `## 验收标准` 清单推断
  - 全未勾选 → `planning`
  - 部分勾选 → `in-progress`
  - 全勾选 → `done`
- **索引**: `Brownbag Sessions.md` 维护所有 session 元数据

## 配置位置
| 组件 | 位置 |
|------|------|
| 命令定义 | `.claude/commands/brownbag.md` |
| 模板 | `Templates/Brownbag Session.md` |
| 索引 | `Work/Brownbag Sessions/Brownbag Sessions.md` |

---
module: zettelkasten
label: "Zettelkasten 永久笔记"
type: knowledge
status: active
enabled: true
created: 2026-03-29
updated: 2026-03-29
depends_on: []
requires:
  cli: [claude]
  plugins: [dataview]
commands: [zettel, retro, backlink, inbox-review, project-retro]
templates: [Templates/Zettel.md, Templates/Inbox.md]
scripts: []
hooks: [upgrade-zettel-status]
folders: [Zettelkasten/, Inbox/, Inbox/archive/]
config_files:
  - .claude/commands/zettelkasten/zettel.md
  - .claude/commands/zettelkasten/retro.md
  - .claude/commands/zettelkasten/backlink.md
  - .claude/commands/zettelkasten/inbox-review.md
  - .claude/commands/zettelkasten/project-retro.md
  - .claude/scripts/upgrade-zettel-status.py
tags: [system/module]
---

# Zettelkasten 永久笔记

## Overview
原子化永久笔记系统。每条笔记一个想法，用自己的话写，通过 `Related::` 互相链接。

被依赖: [[system/modules/learning/module|learning]]

## 架构

```
Zettelkasten/
├── *.md                    # 永久笔记（311+ 条）
└── (通过 Related:: 字段互相链接)
```

### 数据流
- **输入**: `/zettel` 从任何来源提取 → `/retro` 从工作笔记提取 → `/inbox-review` 从 Inbox 转化
- **自动化**: PostToolUse hook 检测 Write/Edit → 当 Related:: 中有 2+ backlinks 时自动从 `seedling` 升级为 `growing`
- **输出**: 永久知识库，可被 Dataview 查询

### 核心规则
- 一条笔记 = 一个想法
- 用自己的话写（不是复制粘贴）
- 标题是描述性陈述（如 "分布式系统用一致性换可用性"）
- frontmatter: `status` (seedling/growing/evergreen), `source`, `topics`, `Related::`

## Quick Start

1. **捕捉想法** → `/zettelkasten/zettel` — 从任何来源（文章、对话、灵感）提取一条原子想法，写成永久笔记
2. **处理收件箱** → `/zettelkasten/inbox-review` — 每周清理 Inbox/，把有价值的想法转为 zettel，其余归档
3. **工作复盘** → `/zettelkasten/retro` — 从最近的工作日记中提取经验教训，转为 zettel
4. **补充链接** → `/zettelkasten/backlink` — 为已有 zettel 寻找关联笔记，增强网络连接

**日常节奏**: 随时 `/zettel` 捕捉 → 每周 `/inbox-review` 清理 → 每周 `/retro` 复盘

## 配置位置
| 组件 | 位置 |
|------|------|
| 命令定义 | `.claude/commands/zettelkasten/{zettel,retro,backlink,inbox-review,project-retro}.md` |
| 自动升级脚本 | `.claude/scripts/upgrade-zettel-status.py` |
| Hook 配置 | `.claude/settings.json` → PostToolUse |
| 模板 | `Templates/Zettel.md` |

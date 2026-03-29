---
module: zettelkasten
label: "Zettelkasten 永久笔记"
type: knowledge
status: active
created: 2026-03-29
updated: 2026-03-29
depends_on: [inbox]
commands: [zettel, retro, backlink]
templates: [Templates/Zettel.md]
scripts: []
hooks: [upgrade-zettel-status]
folders: [Zettelkasten/]
config_files:
  - .claude/commands/zettel.md
  - .claude/commands/retro.md
  - .claude/commands/backlink.md
  - .claude/scripts/upgrade-zettel-status.py
tags: [system/module]
---

# Zettelkasten 永久笔记

## Overview
原子化永久笔记系统。每条笔记一个想法，用自己的话写，通过 `Related::` 互相链接。

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

## 配置位置
| 组件 | 位置 |
|------|------|
| 命令定义 | `.claude/commands/{zettel,retro,backlink}.md` |
| 自动升级脚本 | `.claude/scripts/upgrade-zettel-status.py` |
| Hook 配置 | `.claude/settings.json` → PostToolUse |
| 模板 | `Templates/Zettel.md` |

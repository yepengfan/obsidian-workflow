---
module: grammar
label: "Grammar 高级语法练习"
type: knowledge
status: active
enabled: true
created: 2026-06-06
updated: 2026-08-03
depends_on: []
requires:
  cli: [claude]
  plugins: [dataview]
commands: [practice, review]
templates: [Templates/Grammar Structure.md, Templates/Grammar Log.md]
scripts: []
hooks: []
folders: [Learning/Practice/Grammar/, Learning/Practice/Grammar/Structures/, Learning/Practice/Grammar/Log/]
config_files:
  - .claude/commands/grammar/practice.md
  - .claude/skills/grammar-practice/SKILL.md
  - .claude/commands/grammar/review.md
  - .claude/skills/grammar-review/SKILL.md
  - Learning/Practice/Grammar/CLAUDE.md
tags: [system/module]
---

## Overview

高级英语语法表达力练习模块。目标不是纠错，而是扩展句法工具箱 — 让复杂想法能精确塑形，而非被压平成简单句。

## 架构

- **Structures/**: 一个语法结构一个文件，含 before→after 重写对 + 变体
- **Log/**: 每日练习记录
- **files/**: 参考书 PDF + 学习计划 MOC

### 数据流

- **输入**: `/grammar/practice [structure]` → 选择结构 → 用自己的句子重写 → 沉淀 card + log
- **回顾**: `/grammar/review` → 按 `updated` 排序展示最久未练的结构

## Quick Start

1. `/grammar/practice cleft sentences` — 练习特定结构
2. `/grammar/practice` — 从最久未练的结构开始
3. `/grammar/review` — 复习统计 + 挑结构练习

## 配置位置

| 文件 | 用途 |
|------|------|
| `Learning/Practice/Grammar/CLAUDE.md` | 模块详细规则 |
| `.claude/commands/grammar/practice.md` | 练习命令 |
| `.claude/commands/grammar/review.md` | 复习命令 |
| `Templates/Grammar Structure.md` | Structure card 模板 |
| `Templates/Grammar Log.md` | 练习 log 模板 |

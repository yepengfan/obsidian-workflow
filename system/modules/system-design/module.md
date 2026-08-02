---
module: system-design
label: "System Design 系统设计练习"
type: knowledge
status: active
enabled: true
created: 2026-05-12
updated: 2026-08-03
depends_on: []
requires:
  cli: [claude]
  plugins: [dataview]
commands: [solve]
templates: [Templates/SD Pattern.md, Templates/SD Log.md]
scripts: []
hooks: []
folders: [Learning/Practice/System-Design/, Learning/Practice/System-Design/Patterns/, Learning/Practice/System-Design/Log/, Learning/Practice/System-Design/Courses/]
config_files:
  - .claude/commands/sysd/solve.md
  - .claude/skills/sysd-solve/SKILL.md
  - Learning/Practice/System-Design/CLAUDE.md
tags: [system/module]
---

## Overview

System Design 练习模块。交互式设计引导 → 方案审核 → Pattern Card 沉淀。类似 Algorithm 模块的永续练习系统。

## 架构

- **Patterns/**: 一个 pattern 一个文件，frontmatter 驱动 Dataview
- **Log/**: 每次练习记录
- **Courses/**: 课程笔记（Hello Interview 等）

### 数据流

- **输入**: `/sysd/solve <题目>` → 引导设计（7 步框架） → 方案审核 → 沉淀 card + log

### 与其他模块关系

- **Algorithm**: LeetCode 刷题，训练编码能力
- **Frontend**: React/Next.js 前端练习

## Quick Start

1. `/sysd/solve Design YouTube` — 开始练题

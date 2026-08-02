---
module: frontend
label: "Frontend 前端练习"
type: knowledge
status: active
enabled: true
created: 2026-06-23
updated: 2026-08-03
depends_on: []
requires:
  cli: [claude, node, npm]
  plugins: [dataview]
commands: [solve]
templates: [Templates/Frontend Pattern.md, Templates/Frontend Log.md]
scripts: []
hooks: []
folders: [Learning/Practice/Frontend/, Learning/Practice/Frontend/Patterns/, Learning/Practice/Frontend/Log/, Learning/Practice/Frontend/sandbox/]
config_files:
  - .claude/commands/frnt/solve.md
  - .claude/skills/frnt-solve/SKILL.md
  - Learning/Practice/Frontend/CLAUDE.md
tags: [system/module]
---

## Overview

前端练习模块（React + Next.js）。交互式引导实现 → Code Review → Pattern Card 沉淀。题源: GreatFrontEnd。

## 架构

- **Patterns/**: 一个 pattern 一个文件，frontmatter 驱动 Dataview
- **Log/**: 每日练习记录
- **sandbox/**: Next.js 15 项目，所有 challenge 代码在此运行

### 数据流

- **输入**: `/frnt/solve <题目>` → 初始化骨架 → 引导实现 → Code Review → 沉淀 card + log

### 与其他模块关系

- **Algorithm**: 训练编码能力 → 前端练习中写逻辑时直接受益
- **System Design**: 训练架构思维 → 前端组件架构、状态管理思路一致

## Quick Start

1. `cd Learning/Practice/Frontend/sandbox && npm install` — 首次安装依赖
2. `/frnt/solve Accordion` — 开始做题

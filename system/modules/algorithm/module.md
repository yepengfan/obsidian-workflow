---
module: algorithm
label: "Algorithm 算法练习"
type: knowledge
status: active
enabled: true
created: 2026-05-07
updated: 2026-06-23
depends_on: []
requires:
  cli: [claude]
  plugins: [dataview]
commands: [solve, migrate]
templates: [Templates/Algorithm Pattern.md, Templates/Algorithm Log.md]
scripts: []
hooks: []
folders: [Learning/Practice/Algorithm/, Learning/Practice/Algorithm/Patterns/, Learning/Practice/Algorithm/Log/]
config_files:
  - .claude/commands/algo/solve.md
  - .claude/commands/algo/migrate.md
  - Learning/Practice/Algorithm/CLAUDE.md
tags: [system/module]
---

## Overview

LeetCode 算法练习模块。交互式解题引导 → 代码审核 → Pattern Card 沉淀。

## 架构

- **Patterns/**: 一个 pattern 一个文件，frontmatter 驱动 Dataview
- **Log/**: 每日解题记录
- **Legacy/**: 迁移前的原始文件（只读参考）

### 数据流

- **输入**: `/algo/solve <LC#>` → 引导解题 → 代码审核 → 沉淀 card + log
- **迁移**: `/algo/migrate` → Legacy/ → Patterns/ 一次性转换

## Quick Start

1. `/algo/solve 543` — 开始解题
2. `/algo/migrate` — 迁移旧数据（仅需运行一次）

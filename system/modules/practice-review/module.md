---
module: practice-review
label: "练习回顾与间隔复习"
type: knowledge
status: active
enabled: true
created: 2026-11-11
updated: 2026-11-11
depends_on: []
requires:
  python: ">=3.10"
  pip: [PyYAML]
  plugins: [dataview]
commands: [add, today]
templates: []
scripts: [scripts/practice-review/review.py]
hooks: []
folders: [Learning/Practice/Review/]
config_files:
  - Learning/Practice/Review/AGENTS.md
  - Learning/Practice/Review/00_index.md
  - Learning/Practice/Review/Flows/
  - Learning/Practice/Review/Content/
  - .agents/skills/practice-review-add/SKILL.md
  - .agents/skills/practice-review-today/SKILL.md
interval_days: [1, 3, 7, 14, 30]
retry_days: 1
tags: [system/module]
---

## Overview

用同一个到期清单管理算法、系统设计和行为面试练习。每轮结束后保存本人心得，按实际表现安排下次复习。

## 架构

- 通用脚本统计今日到期和逾期条目，维护复习日期、轮次与心得。
- `Flows/` 定义各领域怎样作答和评价。`Content/` 定义各领域练什么、作答后回顾哪些问题。
- `Items/` 保存具体题目、复习状态和历次记录，随 vault 同步。`00_index.md` 展示练习队列。

## Quick Start

1. `/practice-review-add algorithm 1071` 加入一道题。`system-design` 和 `behavioral` 也可以作为领域参数。
2. `/practice-review-today` 查看今日到期、逾期和待首次练习的条目。
3. `/practice-review-today lc-1071` 打开条目并开始练习。提交作答和本人心得后记录这一轮。

## 配置位置

`interval_days` 和 `retry_days` 在本文件设置。练习和回顾的交接规则见 [[Learning/Practice/Review/AGENTS|复习模块规则]]。

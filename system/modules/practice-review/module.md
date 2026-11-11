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
commands: [practice, practice-review-add, practice-review-today]
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
  - .agents/skills/practice/SKILL.md
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

1. `/practice` 选择练习或 Review，再选择算法、系统设计或行为面试。
2. 练习模式输入新题或选择已有待练习内容。Review 模式从该模块的到期项目中选题。
3. 完成本轮作答和本人心得后记录结果，更新下一次日期。

直接加入题目可用 `/practice-review-add algorithm 1071`。直接查看复习队列可用 `/practice-review-today`。

## 配置位置

`interval_days` 和 `retry_days` 在本文件设置。练习和回顾的交接规则见 [[Learning/Practice/Review/AGENTS|复习模块规则]]。

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
practice_flows:
  algorithm: .agents/skills/algo-solve/SKILL.md
  system-design: .agents/skills/sysd-solve/SKILL.md
  behavioral: Learning/Practice/Review/Flows/behavioral.md
review_time_limits:
  algorithm: 30
  system-design: 45
  behavioral: 3
interval_days: [1, 3, 7, 14, 30]
retry_days: 1
tags: [system/module]
---

## Overview

用同一个到期清单管理算法、系统设计和行为面试练习。每轮结束后保存本人心得，按实际表现安排下次复习。

## 架构

- 通用脚本统计今日到期和逾期条目，维护复习日期、轮次与心得。
- `practice_flows` 直接引用现有的 `algo-solve` 和 `sysd-solve` 技能。行为面试使用 `Flows/behavioral.md`。`Content/` 定义各领域练什么、作答后回顾哪些问题。
- `Items/` 保存具体题目、复习状态和历次记录，随 vault 同步。`00_index.md` 展示练习队列。
- `Home.md` 的独立 Practice 区块展示高层统计，链接到完整复习看板。

## Quick Start

1. `/practice` 选择练习或 Review，再选择算法、系统设计或行为面试。
2. 练习模式输入新题或选择已有待练习内容。Review 模式从该模块的到期项目中选题。
3. 完成本轮作答和本人心得后记录结果，更新下一次日期。

直接加入题目可用 `/practice-review-add algorithm 1071`。直接查看复习队列可用 `/practice-review-today`。

## 配置位置

本文件设置 `practice_flows`、`review_time_limits`、`interval_days` 和 `retry_days`。练习和回顾的交接规则见 [[Learning/Practice/Review/AGENTS|复习模块规则]]。

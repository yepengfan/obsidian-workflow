---
module: practice-review
label: "练习回顾与间隔复习"
type: knowledge
status: active
enabled: true
created: 2026-11-11
updated: 2026-11-13
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

Manage algorithm, system design, and behavioral interview practice through one due queue. Conversations and learner responses use English throughout reviews and new practice. Clarify unclear replies before assessing their meaning or saving reflections. Each ended round saves the learner's own reflection and schedules the next review from actual performance. See `Learning/Practice/Review/AGENTS.md` for the shared conversation rules.

## 架构

- 通用脚本统计今日到期和逾期条目，维护复习日期、轮次与心得。
- `practice_flows` 直接引用现有的 `algo-solve` 和 `sysd-solve` 技能。行为面试使用 `Flows/behavioral.md`。`Content/` 定义各领域练什么、作答后回顾哪些问题。
- `Items/` 保存具体题目、复习状态和历次记录，随 vault 同步。`00_index.md` 展示练习队列。
- `Home.md` 顶部的独立 Practice 区块展示高层统计，链接到完整复习看板。

## Quick Start

1. `/practice` 先选择算法、系统设计或行为面试。
2. 按日期从早到晚自动开始该模块的逾期和今日到期题目；每题完成作答、评价和本人心得保存后，更新下一次日期并进入下一题。
3. 到期复习全部完成后，自动进入对应的原有流程练新题；没有到期题时直接进入。算法由 `algo-solve` 接收新题号或题名。

直接加入题目可用 `/practice-review-add algorithm 1071`。直接查看复习队列可用 `/practice-review-today`。算法复习开题时附上 LeetCode 题目直达链接，在站点独立完成后将代码和实际用时贴回对话。

## 配置位置

本文件设置 `practice_flows`、`review_time_limits`、`interval_days` 和 `retry_days`。练习和回顾的交接规则见 [[Learning/Practice/Review/AGENTS|复习模块规则]]。

---
module: practice-review
label: "Practice and Spaced Review"
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

Manage algorithm, system design, and behavioral interview practice through one due queue. Conversations and learner responses use English throughout reviews and new practice, including direct entries into the domain workflows. Clarify unclear replies before assessing their meaning or saving reflections. Each ended round saves the learner's own reflection and schedules the next review from actual performance. See `Learning/Practice/Review/AGENTS.md` for the shared conversation rules.

## Architecture

- The shared CLI lists overdue and due items and maintains review dates, rounds, and reflections.
- `practice_flows` maps to `algo-solve`, `sysd-solve`, and `Flows/behavioral.md`. `Content/` defines each domain's review unit and post-attempt focus.
- `Items/` stores problem prompts, review state, and attempt history through vault sync. `00_index.md` displays the queue.
- The separate Practice section at the top of `Home.md` shows high-level counts and links to the full review dashboard.

## Quick Start

1. Run `/practice` and choose Algorithm, System Design, or Behavioral Interview.
2. Complete that domain's overdue and due items in date order. After each submission, assessment, and reflection is saved, update its next date and start the next item.
3. After all due reviews are complete, enter the domain's normal workflow for a new problem. If none are due, start there immediately. Algorithm practice uses `algo-solve` to request a new problem number or title.

Register a problem directly with `/practice-review-add algorithm 1071`. View the queue with `/practice-review-today`. Algorithm review prompts include direct LeetCode links; solve independently on the site and return with code and actual time.

## Configuration

This file owns `practice_flows`, `review_time_limits`, `interval_days`, and `retry_days`. See [[Learning/Practice/Review/AGENTS|Practice review rules]] for practice and review handoffs.

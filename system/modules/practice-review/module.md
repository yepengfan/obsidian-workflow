---
module: practice-review
label: "Practice and Spaced Review"
type: knowledge
status: active
enabled: true
created: 2026-11-11
updated: 2026-11-28
depends_on: [dashboard]
requires:
  plugins: [dataview]
commands: [practice, practice-review-add, practice-review-today]
templates: []
scripts: [scripts/dashboard/practice-review/view.js, scripts/dashboard/practice-review/view.css]
hooks: []
folders: [Learning/Practice/Review/]
config_files:
  - Learning/Practice/Review/AGENTS.md
  - Learning/Practice/Review/00_index.md
  - Learning/Practice/Review/Content/
  - .agents/skills/practice-review-add/SKILL.md
  - .agents/skills/practice-review-today/SKILL.md
  - .agents/skills/practice/SKILL.md
consumers:
  algorithm:
    enabled: true
    module: algorithm
    flow: .agents/skills/algo-solve/SKILL.md
    time_limit: 30
  system-design:
    enabled: true
    module: system-design
    flow: .agents/skills/sysd-solve/SKILL.md
    time_limit: 60
interval_days: [1, 3, 7, 14, 60]
retry_days: 1
archive_after_final: true
tags: [system/module]
---

## Overview

Manage algorithm and system design practice through one spaced review queue. See `Learning/Practice/Review/AGENTS.md` for conversation rules, domain scheduling, evidence-backed profiles, and the MCP tools.

## Architecture

- The Obsidian workspace MCP server is the only scheduler. Its `practice_*` tools list due items and record review dates, rounds, and reflections, both in local sessions and in other clients.
- `consumers` registers each module that uses spaced review: whether it is enabled, its module, its authoritative workflow, and its review time limit. `Content/` defines each domain's review unit and post-attempt focus.
- `Items/` stores problem prompts, review state, and attempt history through vault sync. `00_index.md` opens the read-only dashboard with totals, a seven-day schedule, scheduling-stage distribution, and a searchable queue.
- The Practice Review card on `Home.md` shows high-level counts and links to the full review dashboard.

## Quick Start

1. Run `/practice` and choose Algorithm or System Design.
2. Complete that domain's overdue and due items in date order. After each submission, assessment, and reflection is saved, update its next date and start the next item.
3. After all due reviews are complete, enter the domain's normal workflow for a new problem. If none are due, start there immediately. Algorithm practice uses `algo-solve` to request a new problem number or title.

Register a problem directly with `/practice-review-add algorithm 1071`. View the queue with `/practice-review-today`. Algorithm review prompts include direct LeetCode links; solve independently on the site and return with code and actual time.

## Configuration

This file owns `consumers`, `interval_days`, `retry_days`, and `archive_after_final`. A module can be reviewed only when all five hold: this module is enabled, its `consumers` entry is enabled, its own module is enabled, its entry is valid, and the MCP server has imported its workflow. The `practice` tool reports the failed condition for each unavailable module. See [[Learning/Practice/Review/AGENTS|Practice review rules]] for practice and review handoffs.

## Dashboard UI

The module dashboard uses the shared Home shell in `scripts/dashboard/ui/`. See `scripts/dashboard/README.md` for navigation, controls, private-data boundaries, and validation.

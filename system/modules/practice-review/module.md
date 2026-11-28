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
  mcp: [practice]
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
  sd-blocks:
    enabled: true
    module: sd-blocks
    flow: .agents/skills/sd-blocks/SKILL.md
    time_limit: 20
    placement_interval: 14
schedule:
  intervals: [1, 3, 7, 14, 30, 60]
  on_fail:
    step_back: 1
    retry_days: 1
  archive_after_final: true
shared_criteria:
  - id: no_substantive_help
    rule: The learner proposed every mechanism, approach and answer direction. Neutral interviewer probes, such as asking why or what happens next, are not help. A hint, a named technique, a corrected approach or a revealed answer is.
  - id: within_time_limit
    rule: The attempt reached its completion point within the module's time limit. Overtime work may continue to the end, but the attempt does not pass.
tags: [system/module]
---

## Overview

Manage algorithm, system design and SD Blocks practice through one spaced review queue. See `Learning/Practice/Review/AGENTS.md` for conversation rules, domain scheduling, evidence-backed profiles, and the MCP tools.

## Architecture

- The Obsidian workspace MCP server is the only scheduler. Its `practice_*` tools list due items and record review dates, criteria judgments and reflections, both in local sessions and in other clients.
- `consumers` registers each module that uses spaced review: whether it is enabled, its module, its authoritative workflow, its review time limit and an optional `placement_interval`. `Content/` defines each domain's review unit and post-attempt focus.
- `Items/` stores problem prompts, review state, and attempt history through vault sync. `00_index.md` opens the read-only dashboard with totals, a seven-day schedule, scheduling-stage distribution, and a searchable queue.
- The Practice Review card on `Home.md` shows high-level counts and links to the full review dashboard.

## Setup

Connect the Obsidian workspace MCP server to your agent client. It is deployed from `yepengfan/obsidian-workflow-infra`; see its `docs/practice.md`. `/module-toggle` will not enable this module until the session exposes its `practice` tool.

## Quick Start

1. Run `/practice` and choose Algorithm, System Design or SD Blocks.
2. Complete that domain's overdue and due items in date order. After each submission, assessment, and reflection is saved, update its next date and start the next item.
3. After all due reviews are complete, enter the domain's normal workflow for a new problem. If none are due, start there immediately. Algorithm practice uses `algo-solve` to request a new problem number or title.

Register a problem directly with `/practice-review-add algorithm 1071`. View the queue with `/practice-review-today`. Algorithm review prompts include direct LeetCode links; solve independently on the site and return with code and actual time.

## Configuration

This file owns `consumers`, the global `schedule` and `shared_criteria`.

- `schedule` is the one rule every module follows. An item starts at stage 0, meaning it has never passed. A pass moves it up one stage and waits that stage's interval (1, 3, 7, 14, 30, then 60 days). A pass at the top stage archives it. A failed attempt drops `on_fail.step_back` stages, never below 0, and is retried after `on_fail.retry_days`. Intervals count from the day the attempt ended, and early attempts count. Modules cannot change the rule.
- Each module declares `pass_criteria` in its own `module.md`: shared criteria by id, plus its own with an `id` and a `rule`. `shared_criteria` defines the criteria every module means the same way.
- `placement_interval` lets a module place a familiar item directly. The item's first attempt, recorded as a placement, moves it on a pass to the stage that waits that interval instead of stage 1; it must be one of `schedule.intervals`. A failed placement is an ordinary fail. Only modules that declare it can record placements.
- Every ended attempt is judged, including the first attempt at a new problem. The agent judges each criterion with its evidence; the MCP server checks that every declared criterion was judged and computes the result: an attempt passes only when every criterion is met.

A module can be reviewed only when all five hold: this module is enabled, its `consumers` entry is enabled, its own module is enabled, its entry and pass criteria are valid, and the MCP server has imported its workflow. The `practice` tool reports the failed condition for each unavailable module. See [[Learning/Practice/Review/AGENTS|Practice review rules]] for practice and review handoffs.

## Dashboard UI

The module dashboard uses the shared Home shell in `scripts/dashboard/ui/`. See `scripts/dashboard/README.md` for navigation, controls, private-data boundaries, and validation.

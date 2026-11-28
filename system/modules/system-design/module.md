---
module: system-design
label: "System Design Practice"
type: knowledge
status: active
enabled: true
created: 2026-05-12
updated: 2026-11-28
depends_on: [dashboard, practice-review]
requires:
  cli: [claude, node]
  plugins: [dataview]
commands: [solve]
templates: [Templates/SD Pattern.md, Templates/SD Log.md]
scripts: [scripts/sd-excalidraw-template.js, scripts/dashboard/system-design/view.js, scripts/dashboard/practice/view.js]
hooks: []
folders: [Learning/Practice/System-Design/, Learning/Practice/System-Design/Solutions/, Learning/Practice/System-Design/Patterns/, Learning/Practice/System-Design/Log/, Learning/Practice/System-Design/Courses/]
config_files:
  - .agents/skills/sysd-solve/SKILL.md
  - Learning/Practice/System-Design/AGENTS.md
pass_criteria:
  - no_substantive_help
  - within_time_limit
  - id: all_steps_done
    rule: All six steps were completed - requirements, estimation, core entities, API, high-level design and deep dives.
  - id: core_blocks_partial
    rule: Every core building block of the problem was answered at least partially, with none weak or uncovered. Until Blocks.md exists, the item's concept_ids are its core blocks.
tags: [system/module]
---

## Overview

Ongoing system design practice: interactive guidance → design review → pattern cards and logs. Coach messages, learner explanations and reflections, and new note content use English, including direct `/sysd-solve` sessions. Shared language and clarification rules live in `Learning/Practice/Review/AGENTS.md`.

## Architecture

- **Patterns/**: One file per pattern, with frontmatter driving Dataview.
- **Log/**: Practice session records.
- **Courses/**: Course notes, such as Hello Interview.
- **Solutions/**: One folder per session, following `planned → wip → done`.

### Data Flow

- **Input**: `/sysd-solve <topic>` → six-step guided design → design review → save cards and log.

### Related Modules

- **Algorithm**: LeetCode practice for coding skills.
- **Frontend**: React and Next.js practice.

## Quick Start

1. Run `/sysd-solve Design YouTube` to begin practice.

## Dashboard UI

The module dashboard uses the shared Home shell in `scripts/dashboard/ui/`. See `scripts/dashboard/README.md` for navigation, controls, private-data boundaries, and validation.

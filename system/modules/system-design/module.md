---
module: system-design
label: "System Design Practice"
type: knowledge
status: active
enabled: true
created: 2026-05-12
updated: 2026-11-13
depends_on: []
requires:
  cli: [claude, node]
  plugins: [dataview]
commands: [solve]
templates: [Templates/SD Pattern.md, Templates/SD Log.md]
scripts: [scripts/sd-excalidraw-template.js]
hooks: []
folders: [Learning/Practice/System-Design/, Learning/Practice/System-Design/Solutions/, Learning/Practice/System-Design/Patterns/, Learning/Practice/System-Design/Log/, Learning/Practice/System-Design/Courses/]
config_files:
  - .agents/skills/sysd-solve/SKILL.md
  - Learning/Practice/System-Design/AGENTS.md
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

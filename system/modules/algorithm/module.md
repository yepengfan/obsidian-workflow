---
module: algorithm
label: "Algorithm Practice"
type: knowledge
status: active
enabled: true
created: 2026-05-07
updated: 2026-10-22
depends_on: []
requires:
  cli: [claude]
  plugins: [dataview]
commands: [solve]
templates: [Templates/Algorithm Pattern.md, Templates/Algorithm Log.md, Templates/Algorithm Atom.md]
scripts: []
hooks: []
folders: [Learning/Practice/Algorithm/, Learning/Practice/Algorithm/Patterns/, Learning/Practice/Algorithm/Log/, Learning/Practice/Algorithm/Atoms/]
config_files:
  - .agents/skills/algo-solve/SKILL.md
  - Learning/Practice/Algorithm/CLAUDE.md
tags: [system/module]
---

## Overview

LeetCode practice module. Brute-force baseline → bottleneck and problem-property analysis → pattern recognition and optimization → code review → pattern cards and practice logs.

## Architecture

- **Patterns/**: One file per pattern, with frontmatter driving Dataview queries.
- **Atoms/**: Reusable techniques shared across patterns, one file per atom. Pattern cards reference atoms through `## Composed Of`; each atom's Used By section automatically resolves backlinks through `file.inlinks`.
- **Log/**: Daily problem-solving logs.
- **Legacy/**: Original files from before migration, for read-only reference.

### Data Flow

- **Input**: `/algo-solve <LC#>` → guided problem solving → code review → user confirmation → save a pattern card and log entry.

## Quick Start

1. Run `/algo-solve 543` to start a problem-solving session in Claude Code or Cursor.

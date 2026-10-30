---
module: algorithm
label: "Algorithm Practice"
type: knowledge
status: active
enabled: true
created: 2026-05-07
updated: 2026-10-31
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
  - Learning/Practice/Algorithm/AGENTS.md
tags: [system/module]
---

## Overview

LeetCode coaching focused on recognizing patterns and matching them to corresponding solution tools. Decomposition and bottleneck analysis support these two core skills. Brute-force baseline → bottleneck and property analysis → recognize structure → match tools → derive and review an optimized solution. Teach unfamiliar mechanisms directly; preserve recognition practice for familiar tools.

## Architecture

- **Patterns/**: One file per pattern, with recognition cues, mechanisms, applicability limits, and frontmatter driving Dataview queries.
- **Atoms/**: Reusable techniques shared across patterns, one file per atom. Pattern cards reference atoms through `## Composed Of`; each atom's Used By section automatically resolves backlinks through `file.inlinks`.
- **Log/**: Daily solution outcomes and learning evidence: independent recognition, missing connections, effective support, and the next independent attempt.
- **Legacy/**: Original files from before migration, for read-only reference.

### Data Flow

- **Input**: `/algo-solve <LC#>` → guided problem solving → code review → user confirmation → save a pattern card and log entry.

## Quick Start

1. Run `/algo-solve 543` to start a problem-solving session in Claude Code or Cursor.

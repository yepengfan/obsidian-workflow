---
module: sd-blocks
label: "SD Blocks"
type: knowledge
status: active
enabled: true
created: 2026-11-28
updated: 2026-11-28
depends_on: [dashboard, practice-review, system-design]
requires:
  plugins: [dataview, excalidraw]
  mcp: [practice]
commands: [sd-blocks]
templates: []
scripts: []
hooks: []
folders: [Learning/Practice/System-Design/Blocks/Reviews/]
config_files:
  - .agents/skills/sd-blocks/SKILL.md
  - Learning/Practice/Review/Content/sd-blocks.md
pass_criteria:
  - no_substantive_help
  - within_time_limit
  - id: points_answered
    rule: Every point examined in this review was answered fully, on the canvas or in the follow-up questions. A partial or weak answer to any examined point is not met.
tags: [system/module]
---

## Overview

Spaced review of the system design building blocks: the Core Concepts, Design Patterns, Key Technologies and Advanced Topics articles under `Learning/Practice/System-Design/`. Each article is one block and one review item. A review is a short scenario drawn on a canvas, followed by one or two questions, that examines two or three of the block's points. The aim is fluent command of each block, so it can be combined in full problems.

Coach messages, learner explanations and reflections, and new note content use English. Shared language and clarification rules live in `Learning/Practice/Review/AGENTS.md`.

## Architecture

- **`Learning/Practice/System-Design/Blocks.md`**: the block map and the single source for blocks, their points and the problems that use them. You maintain it; the MCP server only reads it.
- **Articles**: the block notes themselves stay as you maintain them. Reviews never edit them.
- **`Blocks/Reviews/<block>/`**: one canvas per review, named after the attempt.
- **`Learning/Practice/Review/Items/sdb-<block>.md`**: each block's review item. Its practice history records which points each review examined and how each was answered.
- **Patterns/** cards are examples under their block. They are not reviewed on their own.

## Blocks.md

The map has one section per block, then one table of problems:

```markdown
## dealing-with-contention
note: [[Design Patterns/Dealing with Contention]]
cards: [[Patterns/Key Generation]], [[Patterns/Presigned URL]]
- conditional-write: Conditional writes guard the contested row
- occ: A version column detects conflicts; the loser rereads and retries

## Problems

| problem | note | core | uses |
| --- | --- | --- | --- |
| ticketmaster | [[Question Breakdowns/Ticketmaster]] | dealing-with-contention, redis | elasticsearch |
```

- A block heading is its stable id. `note` links its article, relative to `Learning/Practice/System-Design/`. `cards` is optional. Each block lists 4 to 8 points as `- <id>: <text>`, with ids unique within the block.
- Each problem row names its breakdown note, the blocks it cannot be designed without (`core`, at least one) and others it uses (`uses`, may be empty). A block is in one column at most.
- Text before the first block heading is free. Any other line inside a section is an error.

Review records refer to block and point ids only, so the text of a point can change freely. Removing or renaming an id needs a migration of the items that refer to it. The MCP server checks the map on every SD Blocks call: every link resolves, every id is well formed and unique, and every problem refers to defined blocks. Any error makes SD Blocks unavailable with the reason `invalid_block_map`, listing each error; a missing file reports `block_map_missing`.

## Reviews

- **Triage.** A block without a review item is triaged first. A block the learner does not know, or knows only vaguely, starts with a primer. A familiar block takes a placement review instead.
- **Primer.** A guided walk through the block's points, ending with a short drawing check. Like every ended attempt it is judged; guidance usually fails `no_substantive_help`, so the item starts at stage 0 and is reviewed the next day.
- **Placement.** An ordinary review recorded with `placement: true` on the item's first attempt. Passing it starts the item at the stage that waits `placement_interval` days (14), instead of stage 1. Failing it is an ordinary fail.
- **Review.** A 20-minute scenario drawn on a fresh canvas, then one or two follow-up questions. Each review examines two or three points, preferring points never examined, then points last answered weakly, then the least recently examined.

## Quick Start

1. Run `/practice` and choose SD Blocks, or run `/sd-blocks`.
2. Complete the due block reviews, then triage the next unreviewed block.

## Dashboard UI

SD Blocks appears as its own group on the Practice Review dashboard.

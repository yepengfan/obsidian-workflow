<!-- module: work -->
> [!GUARD] Read `system/modules/work/module.md`. If `enabled: false` → reply "⛔ Module **work** is disabled. Enable it via `/module-toggle work`." and STOP. Do NOT proceed.

---

Create a meeting note for: $ARGUMENTS

## Steps

1. Create a new note in `Work/2026/` named `[YYYY-MM-DD] [Meeting Title].md` using today's date and the meeting title from the arguments.

2. Use this template:

```markdown
---
date: [today's date]
tags: [meeting]
attendees:
project:
---

# [Meeting Title]

> [!info] Meeting Info
> - **Date**: [today's date]
> - **Attendees**: [fill in]
> - **Project**: [fill in if known]

## Agenda

- [ ]

## Discussion Notes



## Action Items

- [ ] [action] — **Owner**: [name] — **Due**: [date]

## Decisions Made



## Follow-up

- Next meeting:
- Related:
```

3. If the arguments include context about the meeting topic, pre-fill relevant sections (agenda items, project name, etc.).

4. Report the file path so the user can open it in Obsidian.

## Rules
- Always use today's date for the filename and frontmatter
- Match language to the user's input
- If the meeting relates to an existing project in Work/, add a wikilink
- NEVER modify WeRead/

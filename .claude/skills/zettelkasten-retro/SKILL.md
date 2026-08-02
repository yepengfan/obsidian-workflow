---
name: zettelkasten-retro
description: >-
  Run a zettelkasten retrospective session. Use for /zettelkasten/retro.
disable-model-invocation: true
---

<!-- module: zettelkasten -->
> [!GUARD] Read `system/modules/zettelkasten/module.md`. If `enabled: false` → reply "⛔ Module **zettelkasten** is disabled. Enable it via `/module-toggle zettelkasten`." and STOP. Do NOT proceed.

---

Extract work experience and lessons from: $ARGUMENTS

Workflow:
1. Read the specified source (Work daily note, project page, or date range like "this week")
   - If "this week": read all daily notes from the current week in `Work/{current_year}/`
   - If a project name: read the project page and recent daily note sections for that project
2. Identify insights worth preserving long-term:
   - Technical decisions and their rationale
   - Debugging lessons / root cause patterns
   - Architecture or design patterns that worked (or didn't)
   - Process improvements or workflow optimizations
   - Cross-project patterns or reusable knowledge
3. For each insight, draft a zettel:
   - **Title**: descriptive statement (e.g., "Feature flags reduce deployment risk but add code complexity")
   - **Content**: 3-8 sentences capturing the lesson, context, and why it matters
   - **source**: wikilink to the daily note or project page
   - **domain**: `work`
   - **Related**: search existing `Zettelkasten/` notes for connections
4. Present all drafted zettel to the user for review
5. On confirmation, create each in `Zettelkasten/` using `Templates/Zettel.md` format

Rules:
- Focus on reusable knowledge, not project-specific details
- Ask "would this be useful to future-you on a different project?" as a filter
- Never create zettel without user confirmation

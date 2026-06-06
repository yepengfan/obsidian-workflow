<!-- module: zettelkasten -->
> [!GUARD] Read `system/modules/zettelkasten/module.md`. If `enabled: false` → reply "⛔ Module **zettelkasten** is disabled. Enable it via `/module-toggle zettelkasten`." and STOP. Do NOT proceed.

---

Run a project-focused retrospective on: $ARGUMENTS

A project retro goes deeper than `/retro` — it focuses on technical decisions, pitfalls, and reusable patterns from hands-on work (POCs, implementations, experiments).

## Steps

1. **Read the project** specified in $ARGUMENTS:
   - If a plan code (e.g. `AISA`): resolve to `Learning/Plans/<CODE>/Projects/` and list available projects, ask the user to choose
   - If a folder path (e.g. `Learning/AI-SA/Projects/my-poc`): read all files in that folder
   - If a note path: read that note
   - If unclear: ask the user

2. **Extract insights across three lenses**:

   ### A. Technical Decisions
   What non-obvious choices were made? What was the rationale? Would you make the same choice again?

   ### B. Pitfalls & Root Causes
   What went wrong or took longer than expected? What was the actual root cause? How would you avoid it next time?

   ### C. Reusable Patterns
   What approaches, architectures, or workflows proved effective and could apply to future projects?

3. **Draft a zettel for each high-value insight**:
   - **Title**: descriptive statement (e.g. "Streaming parsers outperform DOM parsers for large payloads")
   - **Content**: 3-8 sentences with context, decision, outcome, and why it matters
   - **source**: wikilink to the project note
   - **Related**: search `Zettelkasten/` for connections

4. **Present all drafts** for user review before creating any files

## Rules

- Focus on transferable knowledge, not project-specific details
- The bar: "would future-me find this useful on a different project?"
- Distinguish clearly between what worked vs what didn't
- Never create zettel without user confirmation

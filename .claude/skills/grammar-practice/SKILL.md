---
name: grammar-practice
description: >-
  Advanced English grammar structure practice with Socratic rewriting. Use for /grammar/practice or grammar drills.
disable-model-invocation: true
---

<!-- module: grammar -->
> [!GUARD] Read `system/modules/grammar/module.md`. If `enabled: false` → reply "⛔ Module **grammar** is disabled. Enable it via `/module-toggle grammar`." and STOP. Do NOT proceed.

Practice grammar structure: $ARGUMENTS

Read `Learning/Practice/Grammar/CLAUDE.md` for module instructions.

## Phase 1 — Pick & Study

1. If user specified a structure name → search `Learning/Practice/Grammar/Structures/` for a matching card
   - Found → read the card, briefly recap "What it does / when to reach for it"
   - Not found → explain the structure's function and usage, offer to create a new card
2. If no structure specified → read all cards in `Learning/Practice/Grammar/Structures/`, find the one with the oldest `updated` date, suggest it
3. Confirm with user before proceeding

## Phase 2 — Rewrite Exercise (Socratic)

1. Ask user to provide a **real sentence** they recently wrote (work email, Slack message, document, etc.) that feels flat or could benefit from the target structure
2. Guide through 4 steps:
   - `[Step 1/4 分析]` What's the main point? What's background/context?
   - `[Step 2/4 重写]` Rewrite using the target structure — make hierarchy/emphasis/certainty explicit
   - `[Step 3/4 变体]` Generate 2-3 variations (different emphasis, different shape of the same structure)
   - `[Step 4/4 对比]` Compare versions: which most accurately expresses the intended meaning? Why?
3. **Do NOT give a "best answer"** — guide the user to generate and evaluate their own versions
4. Discuss trade-offs between versions (formality, emphasis placement, information density)

## Phase 3 — Card Update / Create

1. **Check existing structures first**: `Glob("Learning/Practice/Grammar/Structures/*.md")` — scan filenames for match. **Never skip this step.**

2. **Existing structure → update**:
   - Append a new `> [!example]` block with the before→after pair from this session
   - Update frontmatter `examples_count` (+1)
   - Update frontmatter `updated` to today
   - If new common trap discovered → append to Warning section
   - If new variation discovered → append to "Variations worth trying"

3. **New structure → create**:
   - Use `Templates/Grammar Structure.md`
   - `id`: read all existing cards' id, take max + 1
   - Fill: title, structure slug, source, before→after, tip, variations, warning
   - `examples_count`: 1

## Phase 4 — Log

1. Check if `Learning/Practice/Grammar/Log/YYYY-MM-DD.md` exists (use today's date)
2. Does not exist → create from `Templates/Grammar Log.md`, fill first entry
3. Already exists → append new `##` section, update frontmatter `structures_practiced` array
4. Each section includes: structure wikilink, before→after summary, insight

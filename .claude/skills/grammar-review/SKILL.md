---
name: grammar-review
description: >-
  Review grammar structure cards by recency and show practice stats. Use for /grammar/review.
disable-model-invocation: true
---

<!-- module: grammar -->
> [!GUARD] Read `system/modules/grammar/module.md`. If `enabled: false` → reply "⛔ Module **grammar** is disabled. Enable it via `/module-toggle grammar`." and STOP. Do NOT proceed.

Review grammar structures and practice stats.

Read `Learning/Practice/Grammar/CLAUDE.md` for module instructions.

## Step 1 — Scan & Sort

1. Read all files in `Learning/Practice/Grammar/Structures/` — extract frontmatter (`id`, `title`, `structure`, `difficulty`, `examples_count`, `updated`)
2. Sort by `updated` ascending (oldest first = most in need of practice)
3. Count total structures

## Step 2 — Practice Stats

1. Read all files in `Learning/Practice/Grammar/Log/` — count total practice sessions
2. Calculate:
   - Total structures in library
   - Total practice sessions (log entries)
   - This week's practice count (entries in current calendar week)
   - This month's practice count (entries in current calendar month)
   - Top 3 most-practiced structures (by log mention frequency)
   - Top 3 least-recently-practiced structures (by `updated` date)

## Step 3 — Review Table

Display a table:

| # | Structure | Examples | Last Practiced | Days Ago |
|---|-----------|----------|---------------|----------|

Highlight structures not practiced in 14+ days with ⚠️.

## Step 4 — Drill-down Options

Offer:
1. **Quick practice** — pick a structure from the least-recently-practiced list → enter `/grammar/practice <structure>` flow
2. **Scenario prompt** — give a random work scenario (e.g. "You need to push back on a deadline in a stakeholder meeting") → user picks a structure and writes a sentence using it
3. **Priority structures not yet built** — remind about structures from the plan that don't have cards yet (conditionals, nominalisation)

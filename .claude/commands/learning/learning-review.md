<!-- module: learning -->
> [!GUARD] Read `system/modules/learning/module.md`. If `enabled: false` → reply "⛔ Module **learning** is disabled. Enable it via `/module-toggle learning`." and STOP. Do NOT proceed.

---

Review learning progress for: $ARGUMENTS

Format: "[plan-or-code]" or "[plan-or-code] [week]" (e.g. "AISA" or "AISA 2026-W10")

## Steps

1. **Parse arguments**:
   - `[plan]` only → review most recent week's log; match by code first (e.g. `AISA`), then by plan name
   - `[plan] [week]` → review specific week (e.g. `AISA 2026-W10`)
   - No args → list active plans (showing `[CODE] plan-name`) and ask the user to choose

2. **Read the week log** at `Learning/<CODE>/Weeks/<YYYY-WXX>.md`

3. **Read `Learning/<CODE>/00_plan.md`** to understand goals and current phase

4. **Produce a structured review**:

   ### Review: <Plan> — <Week>

   **Plan alignment:**
   - Was this week on track with the plan? What drifted?
   - Suggested adjustments to `00_plan.md` (if any)

   **Zettel candidates** — concepts understood well enough to externalize:
   - [concept] → draft zettel title + 1-line summary
   - *(Use `/zettel` to convert these)*

   **Still fuzzy** — needs more work next week:
   - [concept] — what's unclear

   **Next week focus** (based on plan + drift):
   - [ ] ...

5. **Offer to run `/zettel`** on the zettel candidates if the user confirms

## Rules

- Be honest about gaps — the value of review is surfacing what's not clear yet
- Zettel candidates must pass the standard: one atomic idea, truly understood, written in your own words
- Never create zettel without user confirmation
- If the week log is sparse, flag it and encourage the user to fill it in before reviewing

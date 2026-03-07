Review learning progress for: $ARGUMENTS

Format: "[plan]" or "[plan] [week]" (e.g. "AI-SA" or "AI-SA 2026-W10")

## Steps

1. **Parse arguments**:
   - `[plan]` only → review most recent week's log for that plan
   - `[plan] [week]` → review specific week
   - No args → list active plans and ask the user to choose

2. **Read the week log** at `Learning/<plan>/Weeks/<YYYY-WXX>.md`

3. **Read `Learning/<plan>/00_plan.md`** to understand goals and current phase

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

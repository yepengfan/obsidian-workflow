Create or open this week's learning log for: $ARGUMENTS

## Steps

1. **Determine the plan**:
   - If $ARGUMENTS is provided, match it against active plans by **code** first (e.g. `AISA`), then by plan name (e.g. `AI-SA`)
   - If not provided, list all active plans (showing `[CODE] plan-name`) and ask the user to choose

2. **Compute the current ISO week** in `YYYY-WXX` format (e.g. `2026-W10`). Use Monday as the start of the week.

3. **Check if this week's log exists** at `Learning/<CODE>/Weeks/<YYYY-WXX>.md`:
   - If it exists: show its contents and ask if the user wants to update it
   - If not: create it

4. **When creating**, read `Learning/<CODE>/00_plan.md` to extract current phase goals and pre-fill the "本周目标" section.

5. **Use this template**:

   ```markdown
   ---
   date: <today's date>
   week: <YYYY-WXX>
   plan: <plan-name>
   code: <CODE>
   tags: [learning/<plan-name>, weekly]
   ---

   ## 本周目标（来自 plan）

   - [ ] <goals from current phase in 00_plan.md>

   ## 实际完成

   ## 关键洞察

   <!-- 候选 → 用 /zettel 提炼 -->

   ## 阻力 / 未解问题

   ## 下周调整
   ```

## Rules

- Week format is always `YYYY-WXX` with zero-padded week number (W01–W53)
- Never overwrite an existing week log — append or ask
- If `Learning/<CODE>/00_plan.md` doesn't exist, prompt the user to run `/learning-init` first

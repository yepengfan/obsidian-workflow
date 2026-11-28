---
name: sd-blocks
description: >-
  Spaced review of system design building blocks: triage, primers and
  20-minute canvas reviews that rotate through each block's points.
disable-model-invocation: true
---

<!-- module: sd-blocks -->
> [!GUARD] Read `system/modules/sd-blocks/module.md`. If `enabled: false` → reply "⛔ Module **sd-blocks** is disabled. Enable it via `/module-toggle sd-blocks`." and STOP. Do NOT proceed.

> Read `system/modules/practice-review/module.md` before starting. If disabled, explain that SD Blocks requires spaced review, offer `/module-toggle practice-review`, and stop. If its enabled state cannot be verified, report that and stop.

Review a building block: $ARGUMENTS

Read `Learning/Practice/Review/AGENTS.md` and `Learning/Practice/Review/Content/sd-blocks.md`.

## English conversation

Read and apply **English conversation and clarification** in `Learning/Practice/Review/AGENTS.md` for both direct invocations and `/practice` handoffs.

## Start

Call `practice` with `domain: sd-blocks`. It checks the block map and returns `blocks`: every block in `Blocks.md`, in map order, with its title, article `note`, number of points and its review item (`item_id`, `status`, `stage`, `next_review`), or `item: null` when the block has no item yet. It also returns `time_limits`, `pass_criteria` and `placement_intervals` for `sd-blocks`. If SD Blocks is unavailable, report the reason and every listed map error, and stop.

- A block named in `$ARGUMENTS`, by id or title, is reviewed first: a review if it has an active item, otherwise triage.
- Otherwise call `practice_reviews` with `domain: sd-blocks` and review its `overdue` and `today` items in order, as `/practice` does.
- When none are due, suggest the first block in map order that has no item and let the learner choose another. Wait for the choice. Then triage it.

Every attempt has one UUIDv4 attempt ID, kept through retries and saves.

## Triage

Triage a block that has no item. Name the block, without listing its points, and ask how well the learner knows it: not at all, vaguely, or well.

- **Not at all** or **vaguely**: run a **Primer**.
- **Well**: run a **Review** as a placement.

A block whose item is archived follows the archived-item rule in `Learning/Practice/Review/AGENTS.md`: the attempt is judged but not scheduled until the learner reactivates the item.

## Primer

1. Read the block's article (`note`) with `practice_read_note`, or with `read_note` chunks when it is too large. Take the points from the block's entry in `practice`; call `practice_review` once the item exists.
2. Teach the points one at a time: ask what the learner already knows, explain the mechanism and its main tradeoff, and ask them to restate it in their own words. Aim for about 20 minutes.
3. End with a short drawing check on two of the points, following **Review** steps 2 to 4.
4. Judge and save as in **Judge the attempt** and **Save**. The guidance given fails `no_substantive_help`, so the item starts at stage 0 and is reviewed the next day.

## Review

1. For an existing item, call `practice_review` with its `id`. Its `block.points` are already ordered for rotation: points never examined, then points last answered weakly, then the least recently examined. For triage, use the block's points in map order. Pick two or three points from the top that one scenario can examine together; skip a point that does not fit and take the next. Do not show the learner the chosen points.
2. Write a neutral scenario in which those points decide the design: the situation, its scale and what to draw, without naming a mechanism. Use a problem from the `Problems` table of `Blocks.md` that uses the block when one fits. For example: "In the last ten seconds of an auction, thousands of people bid at once. Draw a bid's path from the client to storage, and show how the highest bid is never overwritten."
3. Call `practice_block_template` with the block id, the attempt ID and the scenario. It opens a fresh canvas showing the scenario. Keep earlier review canvases and the article closed until the attempt ends. Start the learner's time limit, `time_limits["sd-blocks"]` minutes, and follow the canvas rules in the MCP entry instructions.
4. When the drawing is done, ask one or two follow-up questions about the examined points the drawing left open. Neutral probes, such as what happens when a component fails or the load grows tenfold, are not help. Naming the technique, correcting the approach or giving the answer is.
5. Debrief. For each examined point, give a result of `mastered`, `partial` or `weak` with its evidence from the canvas or the answers. Then explain what was missed, with the article as reference.

## Judge the attempt

Judge each criterion in `pass_criteria["sd-blocks"]`, once each, with its evidence:

- `no_substantive_help`: the learner proposed every mechanism and answer direction. A primer always fails it.
- `within_time_limit`: the drawing and follow-up questions ended within `time_limits["sd-blocks"]` minutes of active time. Unknown elapsed time is not met.
- `points_answered`: met only when every examined point is `mastered`.

Do not decide pass or fail yourself; the server computes it. Show each judgment and point result in the debrief and in the save preview.

## Save

1. Ask for the learner's own short reflection, then preview the canvas save and the review record together and wait for explicit confirmation.
2. Save the canvas with `practice_save_canvas` at the template's path, using a null revision.
3. Call `practice_finish_round`. Put `id: sdb-<block>`, `domain: sd-blocks`, the block's title and the prompt `Review the <title> building block in a fresh scenario.` in `topic`. Put the attempt ID, the actual local completion date, the reflection, `criteria`, `points` (one `{id, result, evidence}` per examined point) and the scenario as `submission` in `attempt`. Add `placement: true` for a triage review of a familiar block, which is always the item's first attempt.
4. Report the returned stage and next review date. A passed placement starts at the stage that waits `placement_intervals["sd-blocks"]` days. Continue with the next due review, or offer the next block to triage.

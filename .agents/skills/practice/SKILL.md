---
name: practice
description: >-
  Choose a practice module, work through its due reviews, then start a new
  problem in its existing practice workflow.
disable-model-invocation: true
---

<!-- module: practice-review -->
> [!GUARD] Read `system/modules/practice-review/module.md`. If `enabled: false`, tell the user how to enable it with `/module-toggle practice-review`, then stop.

Read `Learning/Practice/Review/AGENTS.md`. Resolve `$ARGUMENTS` and the user's explicit choices in the current exchange. Keep the selected module, review progress and any explicitly supplied new topic through subsequent replies.

## Select module

Use the client's available single-choice input, or numbered choices when that input is unavailable. A bare `/practice` offers `算法` (`algorithm`), `系统设计` (`system-design`) and `行为面试` (`behavioral`). Use a module already supplied in the request or current exchange; otherwise wait for the selection. Do not ask the learner to choose practice or Review.

Resolve the module's authoritative workflow from `practice_flows` in the module configuration. Read that source and execute any module guard it declares before starting a domain action. If it is disabled, explain how to enable it and return to the module choice. Read `Learning/Practice/Review/Content/<domain>.md` for the selected module's review content.

## Complete due reviews

- Run `python3 scripts/practice-review/review.py due`. Filter `overdue` and `today` by the selected `domain`, ordered by `next_review` ascending and then stable ID. Briefly show the counts and review order, then start the first item without another mode or item-selection menu. `upcoming` and `unstarted` items are not due reviews.
- If the learner explicitly selected a review item, use `show <id>` to verify that it is active and belongs to the selected module. Resolve a mismatched or unknown object before starting. Review that item first, then continue with the remaining due items.
- For each item, run the selected-item procedure in `.agents/skills/practice-review-today/SKILL.md`: neutral independent attempt, mapped workflow assessment, the learner's reflection, and confirmed recording. Wait for the learner's submission and reflection before advancing. Keep each item's own stable `attempt_id` through retries and follow-ups.
- After recording an ended round, refresh `due` for this module and start its next due item automatically. An `assisted` or `incomplete` round follows the existing retry schedule; it does not require an immediate same-session repeat. A paused attempt or pending reflection remains on the current item.
- When no due items remain, briefly confirm that the module's due reviews are complete and immediately enter **Start a new problem**. If there were none at the start, go straight there. Do not ask for permission to switch to new practice. Honor an explicit request to pause, stop or change direction.

## Start a new problem

- Enter the mapped workflow for new practice, passing through a new topic supplied for this invocation only after the due reviews are complete. If none was supplied, ask for a new problem or interview question using that workflow's topic-input step and wait. Do not reuse the last reviewed topic or automatically restore an unrelated WIP session. An explicit request to continue a session takes precedence over the default new-problem handoff.
- That workflow owns initialization, guidance, assessment and optional domain-specific saving. Do not add a shared topic menu or infer a topic from earlier conversation. For example, after algorithm reviews, enter `algo-solve` and ask for a new problem number or title when none was supplied.
- Begin one stable `attempt_id` for this attempt and keep it through continuation and retries. When the round ends, register its review object using steps 1-3 in `.agents/skills/practice-review-add/SKILL.md` if it needs an item. Use an existing item's stable ID when available.
- Close the actual practice round using **Review and save** in `.agents/skills/practice-review-today/SKILL.md`, retaining the assessment already produced by the mapped workflow. Collect the learner's own reflection, preserve the observed assistance and submission, and record the round through the shared CLI.

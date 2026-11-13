---
name: practice-review-today
description: >-
  Show today's spaced practice queue, or guide one selected review through
  independent practice, feedback, the learner's reflection, and rescheduling.
disable-model-invocation: true
---

<!-- module: practice-review -->
> [!GUARD] Read `system/modules/practice-review/module.md`. If `enabled: false`, tell the user the module is disabled and how to enable it with `/module-toggle practice-review`, then stop.

Read `Learning/Practice/Review/AGENTS.md`. Use `python3 scripts/practice-review/review.py` for queue and metadata operations.

## List or select

- With no item in `$ARGUMENTS`, run `due`. Show the counts and titles for today, overdue, and waiting for their first recorded round. Include the stable IDs so the learner can choose one.
- With a selected item, run `show <id>`. Check that it is active. Resolve `practice_flows[domain]` from the module configuration, read the mapped source and execute any module guard it declares. Read `Content/<domain>.md` for the review content.
- Present the neutral prompt and a time limit from `review_time_limits[domain]`, adjustable before starting. When `source` is a problem URL, display it as a clickable Markdown link alongside the title; follow `Content/<domain>.md` for domain-specific link and submission requirements. Let the learner make an independent attempt in the format appropriate to the selected workflow and report their actual time. Start a stable unique `attempt_id` and keep it through retries and follow-ups.
- Use only the neutral prompt and problem link before independent practice. Open earlier code, diagrams, answers, notes and the item's `review_focus` after the attempt ends. If the learner asks for help during practice, provide targeted help and retain that assistance in the evaluation.
- After submission, use the mapped workflow's existing assessment section. For system design, enter `sysd-solve` Phase 2 after the independent submission. Its Phase 0 restoration belongs to resumed practice and must not expose an old design before a cold review.

## Review and save

1. Use the mapped workflow's assessment, reusing one already produced when closing a normal practice round. Record `independent` when the learner meets its criteria without substantive help, `assisted` when help was needed to meet them, or `incomplete` when the ended attempt falls short. Honor an agreed time limit when deciding completion. Use the content definition and the item's post-attempt focus to choose a relevant question. Ask for the learner's own short reflection on what happened, why, and what they will try next.
2. When the round has ended and the learner's reflection is available, save it in their words. Keep the observed `outcome`, `submission` or existing submission link, and any `observations` separate from their reflection. Retain the actual day the round ended if saving happens later. A paused attempt can resume with the same ID.
3. Write a temporary attempt JSON file with `attempt_id`, `outcome`, `reflection` and any optional evidence. Run `python3 scripts/practice-review/review.py record <id> --attempt-file <path>`, inserting `--date YYYY-MM-DD` before `record` when needed. Reuse the ID if the save has to be retried. Remove the temporary file after the result is confirmed.
4. Use the returned `recorded` flag and `next_review` to confirm the save and date. If the round was already saved, report its current schedule. Domain-specific Pattern/Log saving follows the mapped workflow's authorization rules.

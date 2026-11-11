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
- With a selected item, run `show <id>`. Check that the returned item is active and read `Flows/<domain>.md` and `Content/<domain>.md`. Present the neutral prompt and the domain's time limit or practice format. Start a new attempt with a stable unique `attempt_id` and keep it through retries and follow-ups.
- Use only the neutral prompt before independent practice. Open earlier code, diagrams, answers, notes and the item's `review_focus` after the attempt ends. If the learner asks for help during practice, provide targeted help and retain that assistance in the evaluation.

## Review and save

1. Apply the selected flow's evaluation criteria to the submitted work and report the evidence. Use the content definition and the item's post-attempt focus to identify the relevant question for this round. Ask for the learner's own short reflection on what happened, why, and what they will try next.
2. When the round has ended and the learner's reflection is available, save it in their words. Keep the observed `outcome`, `submission` or existing submission link, and any `observations` separate from their reflection. Retain the actual day the round ended if saving happens later. A paused attempt can resume with the same ID.
3. Write a temporary attempt JSON file with `attempt_id`, `outcome`, `reflection` and any optional evidence. Run `python3 scripts/practice-review/review.py record <id> --attempt-file <path>`, inserting `--date YYYY-MM-DD` before `record` when needed. Reuse the ID if the save has to be retried. Remove the temporary file after the result is confirmed.
4. Use the returned `recorded` flag and `next_review` to confirm the save and date. If the round was already saved, report its current schedule. The existing algorithm and system design skills can be used separately for their own pattern cards or logs.

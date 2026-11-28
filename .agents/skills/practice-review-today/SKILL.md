---
name: practice-review-today
description: >-
  Show today's spaced practice queue, or guide one selected review through
  independent practice, feedback, the learner's reflection, and rescheduling.
disable-model-invocation: true
---

<!-- module: practice-review -->
> [!GUARD] Read `system/modules/practice-review/module.md`. If `enabled: false`, tell the user the module is disabled and how to enable it with `/module-toggle practice-review`, then stop.

Read `Learning/Practice/Review/AGENTS.md`. Use the practice MCP tools for queue and metadata operations.

## List or select

- With no item in `$ARGUMENTS`, call `practice_reviews` for each enabled module. Show the counts and titles for today, overdue, and waiting for their first recorded attempt. Include the stable IDs so the learner can choose one.
- With a selected item, call `practice_review` with its `id`. Check that it is active. Call `practice` with its `domain` to resolve the module's workflow, time limit and pass criteria, read the mapped source and execute any module guard it declares. Read `Content/<domain>.md` for the review content.
- Present the neutral prompt and the time limit that `practice` returns for the domain, used as a one-time continuation check-in. When `source` is a problem URL, display it as a clickable Markdown link alongside the title; follow `Content/<domain>.md` for domain-specific link and submission requirements. For System Design, start the review using **Attempt type** in the mapped skill and keep its UUID as the attempt ID. For other domains, let the learner make an independent attempt in the format appropriate to the selected workflow and report their actual time. Start a stable unique `attempt_id` and keep it through retries and follow-ups.
- Use only the neutral prompt and problem link before independent practice. Open earlier code, diagrams, answers, notes and the item's `review_focus` after the attempt ends. If the learner asks for help during practice, provide targeted help and judge `no_substantive_help` accordingly.
- After submission, use the mapped workflow's existing assessment section. For system design, enter `sysd-solve` Phase 2 after the independent submission. Record the confirmed attempt once with its UUID. Its Phase 0 restoration belongs to resumed practice and must not expose an old design before a cold review.

## Review and save

1. Use the mapped workflow's assessment, reusing one already produced when closing a normal practice attempt. Judge every criterion in the domain's `pass_criteria`, once each, with its evidence, following **Judging an attempt** in `Learning/Practice/Review/AGENTS.md`. Do not decide pass or fail; the server computes it. Use the content definition, System Design's `practice_design_outline` when applicable, and the item's post-attempt focus to choose a relevant question. Ask for the learner's own short reflection on what happened, why, and what they will try next.
2. When the attempt has ended and the learner's reflection is available, save it in their words. Keep the `criteria` judgment, `submission` or existing submission link, `observations`, and System Design `concept_observations` separate from their reflection. Retain the actual day the attempt ended if saving happens later. A paused attempt can resume with the same ID.
3. For every enrolled module, finish confirmed attempts by calling `practice_finish_round`. Put the selected item's exact `id`, `domain`, `title` and neutral `prompt` in `topic`. Put the original attempt ID as `attempt_id`, the actual local completion date as `completed_on`, the reflection, `criteria` and the observed fields in `attempt`. For a System Design solution folder include `progress_path` as `<session-folder>/progress.md`. Preserve IDs across retries.
4. Report the verified next review date or archive result. Keep an interrupted registration available for retry. Domain-specific artifact saves retain their existing authorization.

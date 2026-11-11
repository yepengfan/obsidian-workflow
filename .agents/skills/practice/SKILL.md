---
name: practice
description: >-
  Open the interactive practice entry. Choose practice or Review, then an
  algorithm, system design, or behavioral interview module and a topic.
disable-model-invocation: true
---

<!-- module: practice-review -->
> [!GUARD] Read `system/modules/practice-review/module.md`. If `enabled: false`, tell the user how to enable it with `/module-toggle practice-review`, then stop.

Read `Learning/Practice/Review/AGENTS.md`. Resolve `$ARGUMENTS` and the user's explicit choices in the current exchange. Keep chosen mode, module and topic through subsequent replies.

## Select mode, module and topic

Use the client's available single-choice input for menus, or numbered choices when that input is unavailable. Ask for one unresolved selection at a time and wait for the answer. Use selections already supplied in the request or current exchange. A bare `/practice` opens the mode menu.

1. **Mode** offers `练习` and `Review（复习）`.
2. **Module** offers `算法` (`algorithm`), `系统设计` (`system-design`) and `行为面试` (`behavioral`). Resolve its authoritative workflow from `practice_flows` in the module configuration. Read that source and execute any module guard it declares before starting a domain action. If it is disabled, explain how to enable it and return to the module choice.
3. **Topic** follows the chosen mode below. Read `Learning/Practice/Review/Content/<domain>.md` for the selected module's review content.

## 练习

- Offer a new topic and any verified ongoing work from the current conversation or the domain's own WIP records. Use the mapped workflow's discovery and restoration procedure when resuming a session.
- The CLI `due` result's `unstarted` entries can also be offered for the selected module as pending items. This label describes their lack of a recorded round. Claim an exercise is already in progress only when the conversation or domain record establishes that fact.
- After the learner chooses a pending item or enters a new topic, execute the mapped workflow's full practice flow. That source owns its initialization, guidance, assessment and optional domain-specific saving.
- Begin one stable `attempt_id` for this attempt and keep it through continuation and retries. When the round ends, register its review object using steps 1-3 in `.agents/skills/practice-review-add/SKILL.md` if it needs an item. Use an existing item's stable ID when available.
- Close the actual practice round using **Review and save** in `.agents/skills/practice-review-today/SKILL.md`, retaining the assessment already produced by the mapped workflow. Collect the learner's own reflection, preserve the observed assistance and submission, and record the round through the shared CLI.

## Review

- Run `python3 scripts/practice-review/review.py due`. Filter `overdue`, `today` and `upcoming` by the selected `domain`. Show the overdue and today counts, then the due titles, dates and stable IDs. Let the learner choose one item.
- With an explicit review item already selected, use `show <id>` to verify that it is active and belongs to the chosen module. Resolve a mismatched or unknown object before starting.
- Start the selected-item procedure in `.agents/skills/practice-review-today/SKILL.md`. Its independent attempt ends before the mapped workflow's existing assessment is applied.
- If the selected module has no due items, show its nearest `upcoming` date when available and offer `切换模块` or `进入练习`. Keep the learner's next selection pending before starting another activity.

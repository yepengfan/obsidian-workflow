# Practice Review

The module has three parts:

- Shared review and scheduling. `scripts/practice-review/review.py` lists due items, saves ended attempts and the learner's own reflection, and updates review metadata. `00_index.md` shows the queue in Obsidian.
- `practice_flows` in the module configuration selects each domain's authoritative workflow. Algorithm and system design use their existing skills for guidance, assessment and domain-specific saving. The behavioral workflow currently lives in `Flows/behavioral.md`.
- `Content/<domain>.md` defines what belongs in a review item, including its neutral prompt, the material to recall, and questions to revisit after an attempt.

Use `algorithm`, `system-design`, or `behavioral` for the domain. The selected workflow owns practice and assessment. This module connects its results to personal reflection and scheduling.

## English conversation and clarification

- Conduct practice and review conversations entirely in English, including module choices, problem prompts, hints, feedback, and reflection questions. Present non-English source material in English while preserving exact identifiers, links, and code. These rules remain active through domain-workflow handoffs and take precedence over their default language choices.
- The Algorithm, System Design, and Behavioral Interview workflows also apply these rules when entered directly. Write new note content, template-derived text, and diagram labels in English while preserving existing filenames, links, metadata identifiers, and historical user content.
- Ask the learner to use English for explanations, interview answers, and reflections. When they reply in another language, ask them to restate their meaning in English before using that explanation or saving the reflection. Keep their own English wording in new records; preserve historical records as written.
- When a reply is unclear, identify the ambiguous phrase and ask a focused question about what they mean. For example, if "calculate directly in the array" could mean building a result list or modifying the input, ask which they intend. Wait for clarification before assessing that claim or recording that reflection; do not infer their intent or silently replace it with a polished interpretation.
- Accept concise, clear English without requiring extra justification or a grammar exercise. Keep clarification neutral during independent attempts. Language clarification alone is not substantive solution help; record any actual problem-solving assistance separately in the assessment.

## Interactive entry

`/practice` selects a domain, completes its due reviews, then starts a new problem. Use the client's choices when available and honor a domain already supplied in the request or current conversation. The entry has no practice/Review mode menu.

Filter `due` to the selected domain's `overdue` and `today` items, ordered by next review date and stable ID. Show the review order and start the first item directly. Each review uses an independent attempt followed by assessment, the learner's reflection and confirmed saving. After each saved round, refresh the queue and automatically start the next due item. Assisted or incomplete ended rounds follow the retry schedule; pending reflection or a paused attempt stays on the current item. `upcoming` and `unstarted` items are outside this due-review sequence.

Once no due items remain, including when the queue was empty initially, automatically enter the selected domain's workflow for a new problem. Keep any explicitly supplied new topic pending until this handoff. Without a topic, ask for a new problem or interview question through that workflow's topic-input step; do not reuse the last reviewed topic or automatically restore an unrelated WIP session. Honor an explicit request to continue, pause, stop or change direction. The domain workflow owns initialization, guidance, assessment and domain-specific saving. Capture a reflection at the end.

Read the selected `practice_flows` source and execute any module guard it declares before a domain action. Practice uses the source's full workflow. Review uses a neutral independent attempt followed by that source's existing assessment section. `review_time_limits` supplies the adjustable review time limits. When practice has already produced an assessment, the shared closing procedure reuses that result.

Direct `/practice-review-today [id]` retains its queue listing or selected-item behavior; the automatic review sequence and transition to a new problem belong to `/practice`.

## Entries and records

- `Items/<id>.md` is the private source of truth for a review object. Keep its `id` stable across attempts. The note stores its prompt, post-attempt focus, and the history of attempts and reflections. When the original submission already has a vault note, link to it instead of copying it.
- Date fields use the vault machine's local calendar. `review_count` counts ended rounds, including rounds that need more practice. `stage` is the zero-based index into `interval_days`. `last_review` and `next_review` are null until the first round is recorded.
- Use the CLI for writes to `review_count`, `stage`, `last_review`, `next_review`, and `last_outcome`. Listing or opening a prompt leaves the dates alone. Archived items stay in history and are omitted from the queue.
- Keep the approved submission and notes factual. Save the learner's reflection in their own words. A paused or ongoing session can resume in chat. Record the round after the learner provides a reflection.

## Schedule

`system/modules/practice-review/module.md` holds the configurable intervals. The trial defaults are 1, 3, 7, 14 and 30 days, calculated from the actual day each review ends. These intervals are a practical spaced review policy inspired by Ebbinghaus's forgetting curve.

| Round | Next review |
| --- | --- |
| First independent completion | Actual completion date plus the first interval |
| Independent completion on or after the due date | Advance one stage up to the final interval and calculate from the actual completion date |
| Independent extra practice before the due date | Keep the scheduled date and stage |
| Ended with help or incomplete | Actual completion date plus `retry_days`, keeping the current stage |

An active item is overdue when its next date is earlier than today. An item is due today when its next date equals today. Items awaiting their first recorded round have a separate list.

## CLI

Run these from the vault. The script also resolves paths relative to itself.

```sh
python3 scripts/practice-review/review.py due
python3 scripts/practice-review/review.py show lc-1071
python3 scripts/practice-review/review.py add --item-file /path/to/item.json
python3 scripts/practice-review/review.py record lc-1071 --attempt-file /path/to/attempt.json
```

`add` reads `id`, `domain`, `title`, and `prompt`. Optional fields are `source` and `review_focus`. `show` returns the prompt, source and scheduling metadata. Read the note itself after the attempt when comparing past evidence.

`due` returns `overdue`, `today`, `unstarted`, and `upcoming` metadata lists. Filter them by domain for the interactive menu.

`record` reads `attempt_id`, `outcome`, and `reflection`. Optional fields are `submission` and `observations`. Outcomes are `independent`, `assisted`, and `incomplete`. Use the same `attempt_id` when retrying the same save. Keep the actual completion date on delayed saves using `--date YYYY-MM-DD` before the subcommand.

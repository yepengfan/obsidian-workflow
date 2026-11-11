# Practice Review

The module has three parts:

- Shared review and scheduling. `scripts/practice-review/review.py` lists due items, saves ended attempts and the learner's own reflection, and updates review metadata. `00_index.md` shows the queue in Obsidian.
- `practice_flows` in the module configuration selects each domain's authoritative workflow. Algorithm and system design use their existing skills for guidance, assessment and domain-specific saving. The behavioral workflow currently lives in `Flows/behavioral.md`.
- `Content/<domain>.md` defines what belongs in a review item, including its neutral prompt, the material to recall, and questions to revisit after an attempt.

Use `algorithm`, `system-design`, or `behavioral` for the domain. The selected workflow owns practice and assessment. This module connects its results to personal reflection and scheduling.

## Interactive entry

`/practice` selects mode, domain, and topic in that order. Ask one unresolved selection at a time using the client's choices when available. Honor selections already supplied in the request or current conversation.

Practice mode starts or resumes the selected domain's practice and captures a reflection at the end. Review mode selects from that domain's overdue and today queues, then runs independent review. When the domain has no due items, `due` supplies an `upcoming` list for showing its nearest scheduled date. The learner can switch domains or enter practice.

Read the selected `practice_flows` source and execute any module guard it declares before a domain action. Practice uses the source's full workflow. Review uses a neutral independent attempt followed by that source's existing assessment section. `review_time_limits` supplies the adjustable review time limits. When practice has already produced an assessment, the shared closing procedure reuses that result.

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

# Practice Review

The module has three parts:

- Shared review and scheduling. `scripts/practice-review/review.py` lists due items, saves ended attempts and the learner's own reflection, and updates review metadata. `00_index.md` shows the queue in Obsidian.
- `Flows/<domain>.md` defines how the learner attempts and how the coach evaluates an item.
- `Content/<domain>.md` defines what belongs in a review item, including its neutral prompt, the material to recall, and questions to revisit after an attempt.

Use `algorithm`, `system-design`, or `behavioral` for the domain. Practice can run on its own or use this queue. Existing `/algo-solve` and `/sysd-solve` keep their usual guided practice and saving rules.

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

`record` reads `attempt_id`, `outcome`, and `reflection`. Optional fields are `submission` and `observations`. Outcomes are `independent`, `assisted`, and `incomplete`. Use the same `attempt_id` when retrying the same save. Keep the actual completion date on delayed saves using `--date YYYY-MM-DD` before the subcommand.

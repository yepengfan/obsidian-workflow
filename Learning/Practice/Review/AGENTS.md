# Practice Review

The module has three parts:

- Shared review and scheduling. `scripts/practice-review/review.py` lists due items, saves ended attempts and the learner's own reflection, and updates review metadata. `00_index.md` opens `scripts/dashboard/practice-review/view.js`: the read-only dashboard for totals, a seven-day schedule, scheduling stages, and domain/status/search filters. Dashboard interactions never record attempts or change scheduling metadata.
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

Filter `due` to the selected domain's `overdue` and `today` items, ordered by next review date and stable ID. Show the review order and start the first item directly. Each review uses its domain’s attempt format followed by assessment, the learner's reflection and confirmed saving. After each saved round, refresh the queue and automatically start the next due item. Use the returned next review date for each ended round; pending reflection or a paused attempt stays on the current item. `upcoming` and `unstarted` items are outside this due-review sequence.

Once no due items remain, including when the queue was empty initially, automatically enter the selected domain's workflow for a new problem. Keep any explicitly supplied new topic pending until this handoff. Without a topic, ask for a new problem or interview question through that workflow's topic-input step; do not reuse the last reviewed topic or automatically restore an unrelated WIP session. Honor an explicit request to continue, pause, stop or change direction. The domain workflow owns initialization, guidance, assessment and domain-specific saving. Capture a reflection at the end.

Read the selected `practice_flows` source and execute any module guard it declares before a domain action. Practice uses the source's full workflow. Review starts with a neutral prompt and uses the mapped assessment. System Design follows the coaching mode in `.agents/skills/sysd-solve/SKILL.md`; other domains start independently. `review_time_limits` supplies each module’s timing configuration. For System Design the value is the Mock continuation check-in. Guided rounds are self-paced. When practice has already produced an assessment, the shared closing procedure reuses that result.

Direct `/practice-review-today [id]` retains its queue listing or selected-item behavior; the automatic review sequence and transition to a new problem belong to `/practice`.

## Entries and records

- `Items/<id>.md` is the private source of truth for a review object. Keep its `id` stable across attempts. The note stores its prompt, post-attempt focus, and the history of attempts and reflections. When the original submission already has a vault note, link to it instead of copying it.
- Date fields use the vault machine's local calendar. `review_count` counts ended rounds, including rounds that need more practice. `stage` is the zero-based index into `interval_days`. `last_review` and `next_review` are null until the first round is recorded.
- Use the CLI for writes to `review_count`, `stage`, `last_review`, `next_review`, `last_outcome`, `status`, and `archived_on`. Listing or opening a prompt leaves the dates alone. Archived items stay in history and are omitted from the queue.
- For Algorithm and Behavioral Interview, practice an archived item again by setting `status: active` and `next_review` to the desired due date in its note. It keeps its stage, so passing that review archives it again. System Design history determines completion and archive status; changing those two fields does not restart its six-round sequence.
- Keep the approved submission and notes factual. Save the learner's reflection in their own words. A paused or ongoing session can resume in chat. Record the round after the learner provides a reflection.

## Schedule

`system/modules/practice-review/module.md` holds the configurable intervals. The defaults are 1, 3, 7, 14 and 60 days, calculated from the actual day each review ends. These intervals are a practical spaced review policy inspired by Ebbinghaus's forgetting curve.

Each System Design topic advances one completed round from the actual completion date, using `interval_days` in order: 1, 3, 7, 14, then 60 days. Rounds 1 and 2 are guided. Rounds 3 through 6 are mock interviews. Round 6 is the final mock and writes a summary that cites existing observations, then archives the topic. Assisted, independent, and omitted outcomes all count as a completed round. An incomplete attempt keeps the same round and uses `retry_days`. A pause is not recorded and leaves the schedule unchanged. Repeating an `attempt_id` does not add another round or another observation. Early and late completions both move one round forward from the day the round actually ended. Other modules keep the outcome schedule below.

In the dashboard show the System Design topic, upcoming round, mode and date. A pause is a checkpoint. Resume the same session and attempt ID.

| Round | Next review |
| --- | --- |
| First independent completion | Actual completion date plus the first interval |
| Independent completion on or after the due date | Advance one stage and calculate from the actual completion date |
| Independent completion on or after the due date at the final stage | With `archive_after_final: true`, set `status: archived`, `archived_on` to the actual completion date and `next_review` to null. With `false`, repeat the final interval |
| Independent extra practice before the due date | Keep the scheduled date and stage |
| Ended with help or incomplete | Actual completion date plus `retry_days`, keeping the current stage |

An active item is overdue when its next date is earlier than today. An item is due today when its next date equals today. Items awaiting their first recorded round have a separate list.

## CLI

Run these from the vault. The script also resolves paths relative to itself.

```sh
python3 scripts/practice-review/review.py due
python3 scripts/practice-review/review.py show lc-1071
python3 scripts/practice-review/review.py add --item-file /path/to/item.json
python3 scripts/practice-review/review.py finish --item-file /path/to/item.json --attempt-file /path/to/attempt.json
```

For confirmed completion in every enrolled module, `finish` ensures the item exists, records the attempt and verifies its schedule. Pass the existing System Design `--progress-path` to close its session after verification. Reuse the original ID and date when retrying.

`add` reads `id`, `domain`, `title`, and `prompt`. Optional fields are `source`, `review_focus`, and `concept_ids`. `show` returns the prompt, source and scheduling metadata. Read the note itself after the attempt when comparing past evidence.

`due` returns `overdue`, `today`, `unstarted`, and `upcoming` metadata lists. Filter them by domain for the interactive menu. For System Design, a parsable history corrects the in-memory due date from completed rounds. `recalculate` writes that date back. Before switching a live vault, prove `migrate` on a temporary vault copy, then run it in the live vault to apply the recalculation immediately. Migration preserves historical event dates, backfills only approved observations with matching locator text, fills the approved URL Shortener concept list only when absent, and rebuilds the profile. Inspect its `skipped` results; insufficient evidence waits for a later session.

`record` reads `attempt_id` and `reflection`. `outcome` is required for every module except System Design, where it may be omitted. Optional fields are `submission` and `observations`. Outcomes are `independent`, `assisted`, and `incomplete`. Use the same `attempt_id` when retrying the same save. Keep the actual completion date on delayed saves using `--date YYYY-MM-DD` before the subcommand.

`finish` with a System Design `--progress-path` accepts optional `concept_observations` on the attempt and stores them in a `practice-observations` YAML fence under the session's Assessment. Without that path, `finish` only registers the attempt and schedule.

Each observation has `observation_id`, `concept_id`, `performance` (`mastered`, `partial`, `weak`, or `uncovered`), `summary`, and `anchor`. Its `attempt_id` defaults to the enclosing attempt and must match it; `date` defaults to the completion date. `learner` defaults to true; interviewer-supplied answers must not be credited as learner evidence. Use the same optional `error_id` for the same error across attempts so it can be identified as repeated. Use `date` for the answer date and `evidence_order` for its known chronological position among that day's answers, including across sessions. Do not invent historical timestamps or ordering. Legacy observations without ordering use stable session-path order and their saved order within each note to break same-day ties.

Observations are deduplicated by `observation_id`; conflicting copies fail instead of overwriting evidence. The latest dated, ordered learner answer determines the current conclusion; `uncovered` does not replace an evidenced answer. Earlier observations and contrary evidence remain available. An error is repeated only when it occurs in two distinct attempts. `profile` atomically rebuilds `Learning/Practice/System-Design/Profile.md`. A failed rebuild preserves the existing profile; retry `finish` with the same attempt ID and confirmed payload without advancing another round.

`outline --concept-ids <concept-id> ...` accepts the topic concept list before registration; save the same list on the question during registration. `outline <id>` returns this problem's concepts first, then in-scope weak or uncovered follow-ups and mastered-concept spot-checks. Follow-ups cite saved evidence when available; a concept without learner evidence receives a first diagnostic question. `backfill` applies only the approved observation backfill described above.

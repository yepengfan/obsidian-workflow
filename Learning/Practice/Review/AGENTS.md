# Practice Review

The module has three parts:

- Shared review and scheduling. The Obsidian workspace MCP server lists due items, saves ended attempts and the learner's own reflection, and updates review metadata (see **MCP tools**). `00_index.md` opens `scripts/dashboard/practice-review/view.js`: the read-only dashboard for totals, a seven-day schedule, scheduling stages, and domain/status/search filters. Dashboard interactions never record attempts or change scheduling metadata.
- `consumers` in the module configuration registers each module that uses spaced review: whether it is enabled, its own module, its authoritative workflow and its review time limit. Algorithm and system design use their existing skills for guidance, assessment and domain-specific saving.
- `Content/<domain>.md` defines what belongs in a review item, including its neutral prompt, the material to recall, and questions to revisit after an attempt.

Use `algorithm` or `system-design` for the domain. The selected workflow owns practice and assessment. This module connects its results to personal reflection and scheduling.

## English conversation and clarification

- Conduct practice and review conversations entirely in English, including module choices, problem prompts, hints, feedback, and reflection questions. Present non-English source material in English while preserving exact identifiers, links, and code. These rules remain active through domain-workflow handoffs and take precedence over their default language choices.
- The Algorithm and System Design workflows also apply these rules when entered directly. Write new note content, template-derived text, and diagram labels in English while preserving existing filenames, links, metadata identifiers, and historical user content.
- Ask the learner to use English for explanations, interview answers, and reflections. When they reply in another language, ask them to restate their meaning in English before using that explanation or saving the reflection. Keep their own English wording in new records; preserve historical records as written.
- When a reply is unclear, identify the ambiguous phrase and ask a focused question about what they mean. For example, if "calculate directly in the array" could mean building a result list or modifying the input, ask which they intend. Wait for clarification before assessing that claim or recording that reflection; do not infer their intent or silently replace it with a polished interpretation.
- Accept concise, clear English without requiring extra justification or a grammar exercise. Keep clarification neutral during independent attempts. Language clarification alone is not substantive solution help; record any actual problem-solving assistance separately in the assessment.

## Interactive entry

`/practice` selects a domain, completes its due reviews, then starts a new problem. Use the client's choices when available and honor a domain already supplied in the request or current conversation. The entry has no practice/Review mode menu.

Call `practice_reviews` for the selected domain and use its `overdue` and `today` items, ordered by next review date and stable ID. Show the review order and start the first item directly. Each review uses its domain’s attempt format followed by assessment, the learner's reflection and confirmed saving. After each saved attempt, refresh the queue and automatically start the next due item. Use the returned next review date for each ended attempt; pending reflection or a paused attempt stays on the current item. `upcoming` and `unstarted` items are outside this due-review sequence.

Once no due items remain, including when the queue was empty initially, automatically enter the selected domain's workflow for a new problem. Keep any explicitly supplied new topic pending until this handoff. Without a topic, ask for a new problem or interview question through that workflow's topic-input step; do not reuse the last reviewed topic or automatically restore an unrelated WIP session. Honor an explicit request to continue, pause, stop or change direction. The domain workflow owns initialization, guidance, assessment and domain-specific saving. Capture a reflection at the end.

Read the workflow that `practice` returns for the selected domain and execute any module guard it declares before a domain action. Practice uses the source's full workflow. Review starts with a neutral prompt and is an independent attempt in every module. `consumers.<domain>.time_limit` supplies each module’s time limit, used as a one-time continuation check-in. When practice has already produced an assessment, the shared closing procedure reuses that result.

Direct `/practice-review-today [id]` retains its queue listing or selected-item behavior; the automatic review sequence and transition to a new problem belong to `/practice`.

## Entries and records

- `Items/<id>.md` is the private source of truth for a review object. Keep its `id` stable across attempts. The note stores its prompt, post-attempt focus, and the history of attempts and reflections. When the original submission already has a vault note, link to it instead of copying it.
- Date fields use the vault machine's local calendar. `review_count` counts ended attempts, passed or failed. `stage` runs from 0, never passed, to the number of `schedule.intervals`. `last_review` and `next_review` are null until the first attempt is recorded. `last_result` (`passed` or `failed`) and `unmet_criteria` describe the latest attempt.
- Use the MCP tools for writes to `review_count`, `stage`, `last_review`, `next_review`, `last_result`, `unmet_criteria`, `status`, and `archived_on`. Listing or opening a prompt leaves the dates alone. Archived items stay in history and are omitted from the queue.
- Practice an archived item again by setting `status: active` and `next_review` to the desired due date in its note. It keeps its stage, so passing that review archives it again.
- Keep the approved submission and notes factual. Save the learner's reflection in their own words. A paused or ongoing session can resume in chat. Record the attempt after the learner provides a reflection.

## Schedule

`schedule` in `system/modules/practice-review/module.md` is the one rule every module follows; modules cannot change it. Intervals count from the actual day each attempt ends. They are a practical spaced review policy inspired by Ebbinghaus's forgetting curve.

| Result | Next review |
| --- | --- |
| Pass | Move up one stage and wait that stage's interval: 1, 3, 7, 14, 30, then 60 days |
| Pass at the top stage | With `archive_after_final: true`, set `status: archived`, `archived_on` to the completion date and `next_review` to null |
| Fail | Step back `on_fail.step_back` stage (never below 0) and retry after `on_fail.retry_days` |

Early attempts count like on-time ones. A pause is not recorded and leaves the schedule unchanged; resume the same session and attempt ID. Repeating an `attempt_id` does not record it again.

## Judging an attempt

Every ended attempt is judged, including the first attempt at a new problem. Each module declares `pass_criteria` in its own `module.md`, referring to `shared_criteria` here by id or adding its own with a rule. Judge every criterion of the module, once each, with the evidence for the judgment. Do not decide pass or fail: the MCP server checks that every criterion was judged and passes the attempt only when all are met. Show the learner each judgment with its evidence before the confirmed save.

- `no_substantive_help` means the same in every module: the learner proposed every mechanism, approach and answer direction. Neutral interviewer probes are not help; a hint, a named technique, a corrected approach or a revealed answer is.
- `within_time_limit` uses the module's `time_limit`. Work may continue past it to finish, but the attempt does not pass.

An active item is overdue when its next date is earlier than today. An item is due today when its next date equals today. Items awaiting their first recorded attempt have a separate list.

## MCP tools

The Obsidian workspace MCP server is the only implementation of scheduling, both in local sessions and in other clients. Local practice calls the same tools.

| Tool | Use |
| --- | --- |
| `practice` | Check that a module can be reviewed and return the schedule rule, its workflow, time limit, pass criteria and entry instructions. `time_limits` and `pass_criteria` are keyed by domain, also for a single-domain call: `time_limits["system-design"]`, `pass_criteria.algorithm`. Without a domain it lists every module with the reason any is unavailable. |
| `practice_reviews` | One domain's `overdue`, `today`, `unstarted`, and `upcoming` lists, already ordered by date and stable ID. |
| `practice_review` | One item's prompt, source and scheduling metadata, without its history. Read the note after the attempt when comparing past evidence. |
| `practice_add_review` | Register `id`, `domain`, `title`, and `prompt`, with optional `source`, `review_focus`, and `concept_ids`. An existing item is returned unchanged with `created: false`. |
| `practice_finish_round` | Confirmed completion in every enrolled module: ensure the item exists, record the attempt and verify its schedule. Pass the System Design `progress_path` to close its session. |
| `practice_record_review` | Record one ended attempt on an existing item. |
| `practice_design_outline` | System Design follow-ups for an item `id`, or for `concept_ids` before registration. |
| `practice_rebuild_design_profile` | Rebuild `Learning/Practice/System-Design/Profile.md` from session assessments. |

An attempt has `attempt_id`, `reflection`, `completed_on`, the actual local day the attempt ended, and `criteria`: one `{id, met, evidence}` per criterion the module declares. Optional fields are `submission`, `observations`, and System Design `concept_observations`. Reuse the same `attempt_id` and `completed_on` when retrying a save; a repeated `attempt_id` is recorded only once.

`practice_finish_round` with a System Design `progress_path` stores `concept_observations` in a `practice-observations` YAML fence under the session's Assessment. Without that path it only registers the attempt and schedule.

Each observation has `observation_id`, `concept_id`, `performance` (`mastered`, `partial`, `weak`, or `uncovered`), `summary`, and `anchor`. Its `attempt_id` defaults to the enclosing attempt and must match it; `date` defaults to the completion date. `learner` defaults to true; interviewer-supplied answers must not be credited as learner evidence. Use the same optional `error_id` for the same error across attempts so it can be identified as repeated. Use `date` for the answer date and `evidence_order` for its known chronological position among that day's answers, including across sessions. Do not invent historical timestamps or ordering. Legacy observations without ordering use stable session-path order and their saved order within each note to break same-day ties.

Observations are deduplicated by `observation_id`; conflicting copies fail instead of overwriting evidence. The latest dated, ordered learner answer determines the current conclusion; `uncovered` does not replace an evidenced answer. Earlier observations and contrary evidence remain available. An error is repeated only when it occurs in two distinct attempts. A failed profile rebuild preserves the existing profile; retry `practice_finish_round` with the same attempt ID and confirmed payload without advancing another round.

`practice_design_outline` returns this problem's concepts first, then in-scope weak or uncovered follow-ups and mastered-concept spot-checks. Follow-ups cite saved evidence when available; a concept without learner evidence receives a first diagnostic question. Save the same `concept_ids` on the item during registration.

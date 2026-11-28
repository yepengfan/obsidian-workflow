---
name: sysd-solve
description: >-
  System design practice workflow - Delivery Framework guidance, review, pattern card logging. Use for /sysd-solve or system design interviews.
disable-model-invocation: true
---

<!-- module: system-design -->
> [!GUARD] Read `system/modules/system-design/module.md`. If `enabled: false` → reply "⛔ Module **system-design** is disabled. Enable it via `/module-toggle system-design`." and STOP. Do NOT proceed.

> Read `system/modules/practice-review/module.md` before starting or resuming. If disabled, explain that System Design requires spaced review, offer `/module-toggle practice-review`, and stop. If its enabled state cannot be verified, report that and stop.

Solve System Design problem: $ARGUMENTS

Read `Learning/Practice/System-Design/AGENTS.md` for module instructions.

## English conversation

Read and apply **English conversation and clarification** in `Learning/Practice/Review/AGENTS.md` for both direct invocations and `/practice` handoffs. Coach messages, learner explanations and reflections, and newly authored notes and diagram labels use English. Clarify unclear replies before assessing their meaning or recording them.

## Attempt type

Use the stable review item ID for this design problem across chats and sessions.
Check the review queue for that ID. For an existing item, read its summary with
`practice_review`. If lookup fails, retry the lookup before continuing.

- **New practice.** The topic has no review item yet. Coaching is allowed: let the learner draw first, ask them to trace one request, then give one targeted question or hint at a time. Leave the next edit to them. Register the item during the confirmed completion save.
- **Archived.** The topic's item is archived: `practice_review` fails with `review_archived`, or returns an item whose `status` is not `active`. Practice it like new practice, but it cannot be recorded until reactivated: follow the archived-item rule in `Learning/Practice/Review/AGENTS.md` and do not call `practice_finish_round` for it, because finishing would bind the session to a registration that cannot complete.
- **Review.** The topic has an active item. Start from the neutral prompt and keep prior solutions and canvases closed until the attempt ends. Let the learner drive. Clarify the current functional flow during High-Level Design. In Deep Dives, probe a tradeoff or failure scenario tied to an agreed non-functional requirement. Hold design feedback until the debrief.

Both are judged the same way (see **Judge the attempt**). There are no guided rounds or fixed round counts: the item's stage and the global schedule rule decide when it is reviewed next. Interviewer probes that ask the learner to explain or extend their own choices are not help. If the learner asks for guidance at any time, give it, keep the drawing, current step and UUID, and track it: substantive help fails `no_substantive_help`.

Announce the topic, whether this is new practice or a review, and the item's stage. Assign a UUIDv4 to a new attempt and use it as its attempt ID; progress.md saves it as `round_id`. Call `practice_design_outline` with `id`
for a registered item. Before registration, call it with `concept_ids` using the topic's concept list and retain that list as `concept_ids` for completion registration. Run the outline before choosing deep-dive follow-ups. Ask this problem's concepts first, then
the returned in-scope weak or uncovered concepts. Do not reveal the answer in
the question, and do not ask about a concept that is outside this problem.

After completion, reflection and confirmation, use the shared review recording procedure once, with the same UUID. Checkpoints, resumes and retries keep that ID.

## Judge the attempt

Every ended attempt is judged, including new practice. Judge each criterion in `pass_criteria["system-design"]` from `practice`, once each, with the evidence for your judgment:

- `no_substantive_help`: the learner proposed every mechanism, approach and answer direction. A hint, a named technique, a corrected approach or a revealed answer is help.
- `within_time_limit`: the attempt reached the end of Deep Dives within the System Design time limit (`time_limits["system-design"]`) of verified active time. Continuing past the check-in is allowed, but this criterion is then not met. Unknown elapsed time is not met.
- `all_steps_done`: all six steps were completed.
- `core_blocks_partial`: use the Problems row found while discovering the objectives, and submit its id as `problem`. Met when every block in its `core` column has at least one learner observation tagged with that `block` in this attempt, and all of them are `mastered` or `partial`. The server checks this judgment. For a problem without a row, judge it on the item's `concept_ids` instead and leave out `problem`.

Do not decide pass or fail yourself: the MCP server checks that every criterion was judged and computes the result. Show the learner each judgment with its evidence in the debrief and include it in the confirmed save preview.

## Phase 0 - Initialize the Solution folder

> [!WARNING] `Solutions/` content is excluded by `.gitignore`, except for `AGENTS.md` and `00_index.md`. To find WIP sessions, use shell `ls` to enumerate folders and read each `progress.md` frontmatter. Do not use `Glob` or `Grep`: they respect `.gitignore` and can silently return no results, causing a false conclusion that no session is in progress.

For all resume decisions, a WIP folder qualifies only while its attempt has no recorded `round_completed_on` date. Offer Finish registration for an ended WIP attempt. Reuse its saved topic ID, attempt ID (`round_id`) and completion date. A scheduled review starts a fresh attempt even if an earlier folder for that topic still has pending saves.

### Automatic resumption with no arguments

When `$ARGUMENTS` is empty for a direct `/sysd-solve` invocation:

1. Run shell `ls Learning/Practice/System-Design/Solutions/` to enumerate subfolders. Read each `progress.md` and check for the `system-design/wip` tag. Follow the warning above rather than using Glob/Grep.
2. **One WIP session** → restore it using **Resume a session** below, checking both progress.md and Excalidraw, and continue from the interrupted step.
3. **Multiple WIP sessions** → list the topic, start date, and current progress of each, then ask which one to continue.
4. **No WIP sessions** → reply that no practice session is in progress, and suggest a problem as described in **Choose a new problem**.

When `/practice` hands off to a new problem without a topic, suggest one as described in **Choose a new problem** and wait, instead of automatically restoring an unrelated WIP session. An independent review starts from its neutral prompt and uses Phase 2 after submission; do not restore old designs before that attempt.

### Choose a new problem

`practice` with domain `system-design` returns `roadmap`, the learning plan's progress. When its `status` is `ready` and it has a `next` problem, suggest that problem by default: its title, phase and focus, and its gap count from `next.preflight` (see **Pre-problem check**). Say when the check is unavailable, with its `error`. Let the learner choose another problem instead. When the roadmap is complete (`next` is null), say so. When it is null or `unavailable`, give the returned `reason` if any. In those cases ask for a problem, for example `/sysd-solve Design YouTube`.

### With arguments

1. Extract the short topic name from `$ARGUMENTS`, such as "Design YouTube" → "YouTube" or "Bitly" → "Bitly".
2. Use shell `ls Learning/Practice/System-Design/Solutions/` to enumerate matching `<topic>-*` folders. Do not use Glob/Grep.
   - **A progress.md qualifies for WIP resumption** → use **Resume a session** to check progress.md and Excalidraw, then continue from the interrupted step.
   - **A progress.md has `system-design/planned`** → replace that tag with `system-design/wip`, check both files using **Resume a session**, and continue from the recorded next step. Start at Step 1 if the session is empty.
   - **Matching folders exist, but none are resumable or planned** → tell the learner how many times they have practiced the topic and ask whether to start another attempt.
   - **No matching folder exists** → create a Solution folder and files as described below.

3. **Create a Solution folder**:
   - Name it `<topic>-<today>`, such as `Dropbox-2026-06-24`.
   - Create `Learning/Practice/System-Design/Solutions/<topic>-<today>/`.
   - Run `node scripts/sd-excalidraw-template.js "<topic>"` and save the output to `<topic>.excalidraw.md` in that folder.
   - Create progress.md with this frontmatter:
     ```yaml
     topic: <full problem description>
     started: <today>
     source: Hello Interview
     excalidraw: "[[Learning/Practice/System-Design/Solutions/<topic>-<today>/<topic>.excalidraw]]"
     tags: [system-design/wip]
     ```
     Include an empty Progress table with all six steps marked ⬜, empty Pending Questions and Key Learnings sections, and an empty Next Session section.

4. Tell the learner: "The Solution folder is ready. Open Excalidraw to start drawing." Include its wikilink.

For new practice, run the **Pre-problem check** before step 3 creates the folder or a planned skeleton's canvas is opened.

### Discover the assessment objectives

Once the topic is known, prepare privately before the first interview question in either mode, including scheduled reviews. Resolve the topic through the Question Breakdowns index described in the module guide. Read the matching breakdown, then look up relevant notes in `Learning/Practice/System-Design/Core Concepts/`, `Key Technologies/` and `Design Patterns/` (all under the same System-Design folder). Read only notes relevant to this problem. If a reference is missing, use the available sources and the agreed scope; identify any unsupported assessment as such in the debrief.

Find the problem's row in the Problems table of `Learning/Practice/System-Design/Blocks.md` by its breakdown note now, and keep the row's id for `problem`. Every block in its `core` column is an essential objective, judged by `core_blocks_partial`: plan where in the attempt the learner can show it, and do not apply the completion rule while a core block has no learner answer. A problem without a row has no core blocks beyond its `concept_ids`.

Choose essential objectives and distinguish supporting knowledge. For each essential objective, specify its stage, knowledge category, and what the learner could demonstrate to satisfy it. Refine the selection once requirements are agreed. Keep reference solutions, pattern names and expected mechanisms out of the neutral prompt and public checkpoint summary before the independent attempt. The learner may demonstrate the same understanding through a different sound design.

### Pre-problem check

New practice only: a scheduled review stays neutral, so it never names the problem's blocks before the attempt ends. Once the breakdown is resolved, call `practice_design_preflight` with its note title as `breakdown`, or with the row's id as `problem`. The result lists the problem's `core` and `uses` blocks, each with its SD Blocks `review` and `gap`:

- `not_enrolled`: the block has no review yet.
- `last_failed`: its latest review failed.
- `null`: no gap. An archived block has finished its schedule.

`core_gaps` counts the core blocks with a gap.

- **Two or more core gaps.** Before the problem, triage each core block whose gap is `not_enrolled`, one at a time, following **Triage** in `.agents/skills/sd-blocks/SKILL.md`, after loading SD Blocks with `practice` and domain `sd-blocks` for its points and pass criteria. That gives a primer for a block the learner does not know, or a placement review for one they know well. Then return to this problem. A core block that `last_failed`, and any supporting block with a gap, is not a prerequisite: plan a Deep Dives question on it. The learner may skip the triage and start the problem now.
- **Fewer than two core gaps.** Start the problem. Name each gap and plan a Deep Dives question on it.
- **`sd_blocks` is `unavailable`.** The blocks have no reviews. Say that the check could not see them, and start the problem.
- **`problem` is null.** Blocks.md has no row for this breakdown. Draft one for the learner to confirm: an id from the breakdown's title in kebab-case, `[[Question Breakdowns/<title>]]`, and `core` and `uses` taken from the patterns and technologies the breakdown relies on, using only block ids from Blocks.md. A block may not be in both columns. The learner maintains Blocks.md, and the MCP server only reads it. In a session with file access, add the confirmed row to the Problems table. Otherwise, give it to the learner to add. The server sees the row once the vault syncs. Until then, the attempt has no `problem`, and `core_blocks_partial` is judged on `concept_ids`.

Keep the result for the debrief. A weak answer about a tagged block brings its review forward (see **Phase 3**).

### Pre-created roadmap problems

A learning plan may create Solution skeletons before practice begins. Their progress.md uses `tags: [system-design/planned]`, with all six steps marked ⬜.

- A planned problem is not a WIP session. A direct `/sysd-solve` without arguments must not list or automatically resume it.
- When the learner specifies that problem, first switch its tag to `system-design/wip` as described above, then begin guidance.
- The dashboard shows planned problems as unstarted, with links to their existing progress files.

### Resume a session

> [!WARNING] For every resumed session, including automatic WIP resumption and explicitly selected wip/planned sessions, read both progress.md and Excalidraw. The learner may have drafted FR/NFR, estimates, entities, or APIs on the canvas without updating progress.md. Reading only progress.md can repeat questions they have already answered.

1. Read the session's progress.md for the Progress table, Pending Questions, Key Learnings, and next-step section. Preserve legacy section names in existing files.
2. Use shell `ls` on the session folder to find its `*.excalidraw.md` file. The filename uses the original short topic name and may differ from progress.md's full `topic` or the current `$ARGUMENTS`; use the actual listing. Read the text between `## Text Elements` and `%%`. This is uncompressed canvas text; there is no need to decompress the Drawing section's compressed-json.
3. **Compare both sources**, ignoring the template placeholders listed below:
   - If Excalidraw contains drafts missing from or inconsistent with progress.md, first synchronize progress.md:
     - Add the drafts to the relevant step's Notes and Key Learnings.
     - Update that step's Progress marker (⬜/🔄/✅) to reflect actual completion.
     - Update the next-step section to the current next action so resumption does not use a stale pointer.
   - If both agree, or Excalidraw contains only template placeholders, resume from progress.md's next step.
4. Restore the assessment state described below. For older checkpoints, reconstruct it once from the reference, saved progress and canvas. Apply the completion check before continuing. Continue from the recorded next step without asking again about content already clear on the canvas. Focus on missing or empty parts. If the next-step section is empty and the canvas contains only placeholders, begin at Step 1.

> [!NOTE] Template placeholders are not learner content. `node scripts/sd-excalidraw-template.js` pre-fills the following fixed skeleton, which does not establish that a step is complete:
> - Headings such as `Design: <topic>`, `1. Requirements`, `Functional Requirements`, `Non-Functional Requirements`, `Below the line (out of scope)`, `Back-of-Envelope`, `2. Core Entities`, `3. API / Interface`, `4. Data Flow`, `Write Flow:`, `Read Flow:`, `5. High-Level Design`, and `6. Deep Dives`.
> - Empty numbered placeholders, such as a list of numbers 1 through 5 or 1 through 2 with no actual text.
> - Empty estimate prompts: `- read/write ratio:`, `- QPS:`, and `- storage:` with no value after the colon.
> Count these as draft content only after the learner adds or replaces them with actual text.

## Automatic checkpoints during Phases 1 and 2

Before advancing to the next numbered step, checkpoint the current session's exact Excalidraw drawing and progress.md in Obsidian. This includes leaving Deep Dives for the Final Design canvas section or debrief. Save the latest learner edits first and verify the drawing, then record the completed step and next step in progress.md. Treat this transition as a checkpoint even when fewer than three exchanges have passed. Step-transition autosave is enabled for these two session files. Announce it when starting or resuming and checkpoint without a separate prompt at each step. If the learner opts out, skip both checkpoint writes and advance in chat. Set the session checkpoint’s **Saved** field to “Unsaved” and retain the active drawing and draft progress.

If either write fails, keep the drawing open and the transition pending. Report which file was verified and retry the outstanding write using the same session. Preserve concurrent edits. A checkpoint does not complete the attempt or advance spaced repetition. Honor an explicit finish request with the debrief even if a save is pending.

During guidance, read and update progress.md when any of these conditions applies:

1. **A step changes status**: ⬜ becomes 🔄 (in progress) or ✅ (complete). Update its Progress row and Notes.
2. **A key design decision occurs**: the learner makes an important choice or learns a key concept, such as "302 vs 301" or "a cache is needed for 100K QPS". Append it to Key Learnings.
3. **A pending question emerges**: append an issue requiring later resolution to Pending Questions.
4. **At every checkpoint**: update the next-step section to the current next action.

Write only when state actually changes. An ordinary question such as "What is QPS?" does not require a checkpoint after the explanation.

When a canvas client supplies review timing, retain it as optional session
metadata. On the next approved progress.md save, append the submitted timing
objects to the `canvas_reviews` frontmatter list. Preserve each review's UTC timestamp and sequence, the stopwatch state, total elapsed seconds at the click, and the timed interval since the last
successful review. When the learner starts a timer, retain its start timestamp.
Untimed reviews have an idle timer and zero elapsed time. Paused time is excluded.
Deduplicate by review timestamp and sequence. Only record supplied measurements, and assess the
design independently of elapsed time.

Track the reference-derived objectives privately throughout the attempt. For each one, keep its knowledge category, primary or supporting role, completion criterion, status (open, demonstrated, or assessed with a gap) and evidence.

Before the debrief, keep every learner-visible checkpoint, save preview and progress.md neutral. Record the current step, the learner's stated choices and open questions, the time-limit check-in threshold and decision, verified elapsed time and source (or unknown), any help given, and whether the attempt continues or pauses. Keep reference-derived targets, pattern names, criteria and gap assessments private. On resume, rebuild the private assessment from the matching references and reconcile it with the learner's recorded evidence and canvas before asking another question. At the debrief, present the objectives, evidence, remaining essential gaps, optional future learning and stopping reason. Include them in progress.md on the existing confirmed save.

Checkpoint roughly every 3-5 exchanges rather than on every reply.

## Session status in chat

Show the learner where the session stands with a **Session checkpoint** list followed by a **Delivery Framework** table:

- when a session starts or resumes, before the first question;
- whenever a step starts, completes, or is reopened;
- when the learner pauses or ends the sitting;
- whenever the learner asks where they are.

Do not repeat it on ordinary turns within a step.

```markdown
**Session checkpoint**
- **Problem:** <topic from progress.md>
- **Source:** <source>
- **Started:** <started date>
- **Attempt:** <new practice, or review at stage N>
- **Current step:** Step <n> - <step name>
- **Previous focus:** <last completed step or key decision, or "None yet">
- **Next:** <next action>
- **Saved:** <"Up to date" or what is not yet saved to progress.md>

**Delivery Framework**
| Step | Status |
|------|--------|
| 1. Requirements | ✅ Done |
| 2. Core Entities | 🔄 In progress |
| 3. API / Interface | ⬜ Pending |
| 4. Data Flow | ⬜ Pending |
| 5. High-Level Design | ⬜ Pending |
| 6. Deep Dives | ⬜ Pending |
```

Derive statuses from progress.md, the canvas reconciliation in **Resume a session**, and progress made in this conversation. Use the same ⬜/🔄/✅ meaning as the Progress table. Showing the status is not a save; report unsaved progress in **Saved** instead of implying it was written.

## Phase 1 - Guide the design

1. Receive the problem name or description.
2. Confirm scope and key constraints.
3. Guide the learner through the six-step framework without directly giving a complete design.
4. Use targeted questions to support their thinking at each step.

**New-practice prompts** (in a review, use the review pacing in **Attempt type**):

- Start with Requirements: "What are the three core functions of this system? What are its non-functional requirements?"
- Guide estimates during Step 1: "What is the expected DAU? Read/write ratio? Storage scale?"
- Progress through Core Entities → API → Data Flow → High-Level Design → Deep Dives.
- If the learner remains stuck for more than two exchanges, offer a more direct hint, still short of a complete design.
- Give a complete design only when explicitly requested, for example "show me the design" or "I give up".
- Use the module's **Core principles** in `Learning/Practice/System-Design/AGENTS.md`: derive architecture from requirements, make tradeoffs explicit, estimate scale, and design incrementally.

**Hello Interview Delivery Framework**:

1. Requirements: functional requirements, non-functional requirements, and back-of-envelope estimates.
2. Core Entities: entities and relationships, focused on business concepts.
3. API or Interface: core interfaces and their inputs and outputs.
4. Data Flow: the complete path from a request to storage or a response.
5. High-Level Design: let the learner sketch the minimum components and trace each agreed functional requirement from its trigger to its outcome, including user requests, scheduled jobs and event-driven work where applicable. Assess the essential Core Concepts and Key Technologies through those flows: what each component does and why its technology or architectural tradeoff fits. While they are explaining, give them room to finish. If a functional path is missing, ask one question about that path. Advance once every agreed functional requirement has a working path and those choices have been assessed.
6. Deep Dives: ask the concepts and patterns in this problem's `concept_ids` before using profile follow-ups. Then use `outline` to revisit an in-scope weak point in a new scenario and to give an uncovered concept its first question. A mastered concept can take one variant. Select up to three primary Design Patterns supported by the breakdown and agreed requirements. For each, assess the mechanism, a relevant failure scenario and the essential tradeoff. Supporting concepts and technologies can clarify that mechanism. For Dropbox, when Handling Large Blobs is primary, assess how the design handles an interrupted large upload. Once sufficient evidence exists, record unrelated database concurrency questions as future learning.

**When to end the interview**

Before every follow-up or canvas-review request, update objective statuses from the conversation, canvas and saved progress. Apply these rules in order:

1. On a finish request, start Phase 2 immediately. On a pause request, save the open attempt for resumption.
2. Once all essential objectives have been assessed, deliver the final review in the same turn. An evidenced gap can be a final finding. Advance past a sufficiently assessed stage. Ask a follow-up only when it could materially change the assessment of an essential objective in the current stage. Otherwise proceed to the debrief and capture optional improvements there.
3. Before the next substantive question, compare verified active minutes with the System Design time limit that `practice` returns (`consumers.system-design.time_limit` in the practice-review module). When the threshold is reached or passed and objectives remain, ask “Would you like to continue until we finish, or move to the final review now?” Wait for the answer. If the learner continues, finish the remaining steps; `within_time_limit` is then not met. If they finish, start Phase 2.
4. Use stopwatch intervals or learner-confirmed active time. Exclude pauses, and count each interval once across resets and resumed sittings. Unknown elapsed time cannot trigger the check-in. Preserve verified active time and the check-in decision in the checkpoint; restore them on resume. A new attempt starts with a fresh check-in.

**Step 5 diagram guidance**:

- Use Mermaid `graph LR` for the architecture.
- Group components with `subgraph`, such as Client, Server, and Data Layer.
- Label data flows with protocols such as HTTP, gRPC, and Pub/Sub.
- Iterate with the learner and save the confirmed diagram to the Pattern card.

## Phase 2 - Review the design

1. Receive the learner's design as text or a diagram.
2. Assess the agreed objectives using the available evidence. Apply these lenses where relevant:
   - **Requirements coverage**: are all functional requirements met?
   - **Scalability**: can it support the target scale?
   - **Tradeoffs**: are the benefits and drawbacks of key decisions explicit?
   - **Consistency and availability**: are the CAP considerations appropriate?
   - **Single points of failure**: are any present?
   - **Cost**: is the design overengineered?
3. Compare it with an appropriate reference design and identify gaps and improvements.
4. Summarize strengths, evidenced gaps, objectives left unassessed and future learning. Record the stopping reason. Offer Phase 3 and follow its reflection and save-confirmation rules.

## Phase 3 - Save learning evidence

1. **Classify the patterns**:
   - Read the frontmatter of existing files under `Learning/Practice/System-Design/Patterns/`.
   - Identify relevant existing patterns; one problem may involve several.
   - Determine whether a new pattern is needed.
   - Present the classification and continue after the learner confirms it.

2. **Update existing patterns**:
   - Append the problem name to frontmatter `problems`.
   - Add a Problems table row with the name, difficulty, and today's date.
   - Set frontmatter `updated` to today.
   - Append any newly observed common mistake to Common Mistakes.

3. **Create new patterns**:
   - Use `Templates/SD Pattern.md`.
   - Set `id` to the highest existing card ID plus one.
   - Fill title, category, tags, problems, Key Insight, When to Use, Design Framework, Trade-offs, and Common Mistakes.
   - Assess `difficulty` from the pattern's complexity.

4. **Write the Log**:
   - Check for `Learning/Practice/System-Design/Log/YYYY-MM-DD.md`.
   - If absent, create it from `Templates/SD Log.md` and fill the first entry.
   - Otherwise append a new `##` section and update frontmatter `problems_solved`.
   - Include the pattern wikilink, difficulty, result emoji, notes, requirements summary, and key decisions.

5. **Reference Design Patterns and Key Technologies building blocks**, when the problem is a main practice item in a learning roadmap:
   - Check its Design Pattern / Key Technology entries in `Learning/Plans/<CODE>/00_map.md`, if present.
   - Add wikilinks to the relevant `Design Patterns/<pattern>.md` and `Key Technologies/<tech>.md` documents in the Log entry.
   - The learner maintains those documents. Do not write or expand their content here; they should be prepared before the problem begins.
   - If a referenced document is missing or an empty shell, tell the learner without automatically filling it in.

6. **Mark complete**:
   - One attempt uses the same Solution folder across steps, checkpoints and chats. On final completion, use the shared practice review registration and recording workflows: select or register the topic's review item, collect the learner's reflection, and save one `concept_observations` entry per located answer. `performance` is `mastered`, `partial`, `weak`, or `uncovered`. Tag an answer about a building block of `Blocks.md` with that block's id as `block`, using the block whose article covers it; leave other answers untagged. A tagged block answered `partial` or `weak` brings its SD Blocks review forward to the next day, reactivating an archived one; tell the learner which blocks the result's `block_signals` moved. Interviewer explanations are not learner evidence. Submit the judgment of every criterion from **Judge the attempt**; the server computes pass or fail and the next date. Use this attempt's stable ID and actual completion date to record its spaced-repetition schedule once. If recording or the profile rebuild fails, keep the session resumable and retry the same attempt. A retry must not record the attempt twice or save a second copy of an observation.
   - When saving an ended attempt, record its actual local completion date as `round_completed_on` in progress.md even if the canvas save is pending. Pausing leaves this field unset.
   - Use the shared finish command with the progress path. It verifies the registration before marking the session done. Track outstanding artifact saves separately.
   - Retain progress.md, Excalidraw, Pattern cards, Logs, and Design Pattern / Key Technology documents as the complete practice record.

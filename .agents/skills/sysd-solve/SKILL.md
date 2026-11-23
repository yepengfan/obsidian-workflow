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

## Coaching mode for this round

Use the stable review item ID for this design problem across chats and sessions.
Check the review queue for that ID. For an existing item, read its summary with
`review.py show <id>`. If the topic has no item yet, start guided round 1
and register it during the confirmed completion save. If lookup fails, retry
the lookup before choosing the round.
Use `completed_design_rounds + 1` as the upcoming round. Each topic gets two
full guided learning rounds, then full mock interviews. Announce the topic,
round and mode. Assign a UUIDv4 to a new round and use it as its attempt ID.
- **Guided.** Let the learner draw first. Ask them to trace one request, then
  give one targeted question or hint at a time. Leave the next edit to them.
- **Mock interview.** Let the learner drive. Clarify the current functional flow during High-Level Design. In Deep Dives,
  probe a tradeoff or failure scenario tied to an agreed non-functional requirement. Hold design feedback until the debrief.
  If the learner asks for a hint, track the substantive help in the assessment.
- “Guide me” and “Switch to mock interview” change the active mode immediately.
  Keep the drawing, current step and UUID. At a checkpoint save `round_id` and
  `coaching_mode` in progress.md. Resume both on the same round. For a legacy
  checkpoint missing these fields, initialize them once. A new round starts
  with its topic default. A review always starts with the neutral prompt and
  keeps prior solutions closed until the attempt ends.
- After completion, reflection and confirmation, use the shared review recording
  procedure once, with the same UUID. Checkpoints, resumes and retries keep that
  ID. Record actual help during learning. Normal interviewer questions asking
  the learner to explain their choices are compatible with independent work.

## Phase 0 - Initialize the Solution folder

> [!WARNING] `Solutions/` content is excluded by `.gitignore`, except for `AGENTS.md` and `00_index.md`. To find WIP sessions, use shell `ls` to enumerate folders and read each `progress.md` frontmatter. Do not use `Glob` or `Grep`: they respect `.gitignore` and can silently return no results, causing a false conclusion that no session is in progress.

For all resume decisions, a WIP folder qualifies only while its round has no recorded `round_completed_on` date. An ended round can have pending artifact saves. A scheduled review starts a fresh attempt even if an earlier folder for that topic still has pending saves.

### Automatic resumption with no arguments

When `$ARGUMENTS` is empty for a direct `/sysd-solve` invocation:

1. Run shell `ls Learning/Practice/System-Design/Solutions/` to enumerate subfolders. Read each `progress.md` and check for the `system-design/wip` tag. Follow the warning above rather than using Glob/Grep.
2. **One WIP session** → restore it using **Resume a session** below, checking both progress.md and Excalidraw, and continue from the interrupted step.
3. **Multiple WIP sessions** → list the topic, start date, and current progress of each, then ask which one to continue.
4. **No WIP sessions** → reply: "No practice session is in progress. Please specify a problem, for example `/sysd-solve Design YouTube`."

When `/practice` hands off to a new problem without a topic, ask for a new problem and wait instead of automatically restoring an unrelated WIP session. An independent review starts from its neutral prompt and uses Phase 2 after submission; do not restore old designs before that attempt.

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

### Discover the assessment objectives

Once the topic is known, prepare privately before the first interview question in either mode, including scheduled reviews. Resolve the topic through the Question Breakdowns index described in the module guide. Read the matching breakdown, then look up relevant notes in `Learning/Practice/System-Design/Core Concepts/`, `Key Technologies/` and `Design Patterns/` (all under the same System-Design folder). Read only notes relevant to this problem. If a reference is missing, use the available sources and the agreed scope; identify any unsupported assessment as such in the debrief.

Choose essential objectives and distinguish supporting knowledge. For each essential objective, specify its stage, knowledge category, and what the learner could demonstrate to satisfy it. Refine the selection once requirements are agreed. Keep reference solutions, pattern names and expected mechanisms out of the neutral prompt and public checkpoint summary before the independent attempt. The learner may demonstrate the same understanding through a different sound design.

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

Before advancing to the next numbered step, checkpoint the current session's exact Excalidraw drawing and progress.md in Obsidian. This includes leaving Deep Dives for the Final Design canvas section or debrief. Save the latest learner edits first and verify the drawing, then record the completed step and next step in progress.md. Treat this transition as a checkpoint even when fewer than three exchanges have passed. Step-transition autosave is enabled for these two session files. Announce it when starting or resuming and checkpoint without a separate prompt at each step. Respect an explicit request to keep work unsaved.

If either write fails, keep the drawing open and the transition pending. Report which file was verified and retry the outstanding write using the same session. Preserve concurrent edits. A checkpoint does not complete the round or advance spaced repetition. Honor an explicit finish request with the debrief even if a save is pending.

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

Before the debrief, keep every learner-visible checkpoint, save preview and progress.md neutral in both modes. Record the current stage, the learner's stated choices and open questions, the active-time budget, verified elapsed time and source (or unknown), and whether the round continues or pauses. Keep reference-derived targets, pattern names, criteria and gap assessments private. On resume, rebuild the private assessment from the matching references and reconcile it with the learner's recorded evidence and canvas before asking another question. At the debrief, present the objectives, evidence, remaining essential gaps, optional future learning and stopping reason. Include them in progress.md on the existing confirmed save.

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
- **Coaching mode:** <guided or mock interview>
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

**Guided-mode prompts** (use mock-interview pacing when that mode is active):

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
5. High-Level Design: let the learner finish tracing each agreed functional flow through the baseline architecture. Assess the essential Core Concepts and Key Technologies through those flows: what each component does and why its technology or architectural tradeoff fits. Advance once the flow and those choices have been assessed.
6. Deep Dives: select up to three primary Design Patterns supported by the breakdown and agreed requirements. For each, assess the mechanism, a relevant failure scenario and the essential tradeoff. Supporting concepts and technologies can clarify that mechanism. For Dropbox, when Handling Large Blobs is primary, assess how the design handles an interrupted large upload. Once sufficient evidence exists, record unrelated database concurrency questions as future learning.

**When to end the interview**

Before every follow-up or canvas-review request, update objective statuses from the conversation, canvas and saved progress. Apply these rules in order:

1. An explicit finish request or verified active time at the limit triggers Phase 2 immediately, including with open objectives. Across sittings, use the shortest of the configured System Design limit (review_time_limits.system-design in the practice-review module), 45 minutes, and any shorter agreed budget. Use trustworthy timer measurements or learner-confirmed active time. Count each measured interval once across stopwatch pauses, resets and resumes. An idle timer, an unknown interval or the calendar age of a checkpoint cannot establish elapsed practice time. A request to pause keeps an unfinished round resumable.
2. If the current stage is sufficiently assessed, advance without another question. Once all essential objectives have been assessed, deliver the final review in the same turn. An evidenced gap can be a final finding.
3. Otherwise ask one question only if its answer could materially change the assessment of an essential objective. If none could, proceed to the final review. Capture secondary gaps and optional improvements for future learning.

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
   - One attempt uses the same Solution folder across steps, checkpoints and chats. On final completion, use the shared practice review registration and recording workflows: select or register the topic's review item, collect the learner's reflection and confirm the outcome. Use this round's stable attempt ID and actual completion date to record its spaced-repetition schedule once. If recording fails, keep the session resumable and retry the unfinished save.
   - When saving an ended round, record its actual local completion date as `round_completed_on` in progress.md even if the canvas save is pending. Pausing leaves this field unset.
   - After the review record succeeds and agreed artifact saves are verified, replace `system-design/wip` with `system-design/done` in the Solution progress.md.
   - Retain progress.md, Excalidraw, Pattern cards, Logs, and Design Pattern / Key Technology documents as the complete practice record.

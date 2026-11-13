---
name: sysd-solve
description: >-
  System design practice workflow - Delivery Framework guidance, review, pattern card logging. Use for /sysd-solve or system design interviews.
disable-model-invocation: true
---

<!-- module: system-design -->
> [!GUARD] Read `system/modules/system-design/module.md`. If `enabled: false` → reply "⛔ Module **system-design** is disabled. Enable it via `/module-toggle system-design`." and STOP. Do NOT proceed.

Solve System Design problem: $ARGUMENTS

Read `Learning/Practice/System-Design/AGENTS.md` for module instructions.

## English conversation

Read and apply **English conversation and clarification** in `Learning/Practice/Review/AGENTS.md` for both direct invocations and `/practice` handoffs. Coach messages, learner explanations and reflections, and newly authored notes and diagram labels use English. Clarify unclear replies before assessing their meaning or recording them.

## Phase 0 - Initialize the Solution folder

> [!WARNING] `Solutions/` content is excluded by `.gitignore`, except for `AGENTS.md` and `00_index.md`. To find WIP sessions, use shell `ls` to enumerate folders and read each `progress.md` frontmatter. Do not use `Glob` or `Grep`: they respect `.gitignore` and can silently return no results, causing a false conclusion that no session is in progress.

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
   - **A progress.md has `system-design/wip`** → use **Resume a session** to check progress.md and Excalidraw, then continue from the interrupted step.
   - **A progress.md has `system-design/planned`** → replace that tag with `system-design/wip`, check both files using **Resume a session**, and continue from the recorded next step. Start at Step 1 if the session is empty.
   - **Matching folders exist, but none have wip/planned tags** → tell the learner how many times they have practiced the topic and ask whether to start another attempt.
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
4. Continue from the recorded next step without asking again about content already clear on the canvas. Focus on missing or empty parts. If the next-step section is empty and the canvas contains only placeholders, begin at Step 1.

> [!NOTE] Template placeholders are not learner content. `node scripts/sd-excalidraw-template.js` pre-fills the following fixed skeleton, which does not establish that a step is complete:
> - Headings such as `Design: <topic>`, `1. Requirements`, `Functional Requirements`, `Non-Functional Requirements`, `Below the line (out of scope)`, `Back-of-Envelope`, `2. Core Entities`, `3. API / Interface`, `4. Data Flow`, `Write Flow:`, `Read Flow:`, `5. High-Level Design`, and `6. Deep Dives`.
> - Empty numbered placeholders, such as a list of numbers 1 through 5 or 1 through 2 with no actual text.
> - Empty estimate prompts: `- read/write ratio:`, `- QPS:`, and `- storage:` with no value after the colon.
> Count these as draft content only after the learner adds or replaces them with actual text.

## Automatic checkpoints during Phases 1 and 2

During guidance, read and update progress.md when any of these conditions applies:

1. **A step changes status**: ⬜ becomes 🔄 (in progress) or ✅ (complete). Update its Progress row and Notes.
2. **A key design decision occurs**: the learner makes an important choice or learns a key concept, such as "302 vs 301" or "a cache is needed for 100K QPS". Append it to Key Learnings.
3. **A pending question emerges**: append an issue requiring later resolution to Pending Questions.
4. **At every checkpoint**: update the next-step section to the current next action.

Write only when state actually changes. An ordinary question such as "What is QPS?" does not require a checkpoint after the explanation.

Checkpoint roughly every 3-5 exchanges rather than on every reply.

## Phase 1 - Guide the design

1. Receive the problem name or description.
2. Confirm scope and key constraints.
3. Guide the learner through the six-step framework without directly giving a complete design.
4. Use targeted questions to support their thinking at each step.

**Guidance principles**:

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
5. High-Level Design: core components and their connections; generate a Mermaid architecture diagram.
6. Deep Dives: examine 2-3 components to address non-functional requirements.

**Step 5 diagram guidance**:

- Use Mermaid `graph LR` for the architecture.
- Group components with `subgraph`, such as Client, Server, and Data Layer.
- Label data flows with protocols such as HTTP, gRPC, and Pub/Sub.
- Iterate with the learner and save the confirmed diagram to the Pattern card.

## Phase 2 - Review the design

1. Receive the learner's design as text or a diagram.
2. Review:
   - **Requirements coverage**: are all functional requirements met?
   - **Scalability**: can it support the target scale?
   - **Tradeoffs**: are the benefits and drawbacks of key decisions explicit?
   - **Consistency and availability**: are the CAP considerations appropriate?
   - **Single points of failure**: are any present?
   - **Cost**: is the design overengineered?
3. Compare it with an appropriate reference design and identify gaps and improvements.
4. Once the design passes review, enter Phase 3.

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
   - Replace `system-design/wip` with `system-design/done` in the Solution progress.md.
   - Retain progress.md, Excalidraw, Pattern cards, Logs, and Design Pattern / Key Technology documents as the complete practice record.

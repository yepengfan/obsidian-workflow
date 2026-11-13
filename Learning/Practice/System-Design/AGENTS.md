# System Design Module - Agent Instructions

> Inherit the general conventions from the vault root AGENTS.md.

## Language

Use English for coaching, learner explanations and reflections, and newly authored notes and diagram labels. Apply **English conversation and clarification** in `Learning/Practice/Review/AGENTS.md`, including direct `/sysd-solve` sessions. Preserve existing filenames, links, metadata identifiers, and historical user content when updating notes.

## Directory Configuration

| Path | Purpose |
|------|---------|
| `Learning/Practice/System-Design/Solutions/<topic>/` | One Solution folder per session, containing progress.md and Excalidraw |
| `Learning/Practice/System-Design/Patterns/` | One Markdown file per pattern card |
| `Learning/Practice/System-Design/Core Concepts/` | Core concept references, such as Caching, Sharding, and CAP Theorem |
| `Learning/Practice/System-Design/Key Technologies/` | Technology building-block articles, such as Redis and Kafka |
| `Learning/Practice/System-Design/Design Patterns/` | Design building-block articles, such as Scaling Reads and Real-time Updates |
| `Learning/Practice/System-Design/Insights/` | Specific knowledge and lessons captured during practice |
| `Learning/Practice/System-Design/Log/` | Practice session logs |
| `Learning/Practice/System-Design/Courses/` | Course notes, such as Hello Interview |
| `Learning/Practice/System-Design/Attachments/` | Shared media, including diagrams and screenshots not specific to one problem |
| `Learning/Practice/System-Design/00_index.md` | Dataview dashboard |
| `Templates/SD Pattern.md` | Template for new pattern cards |
| `Templates/SD Log.md` | Template for new logs |

## Solving Flow

1. Receive a problem, such as "Design YouTube", and guide requirements analysis without directly giving the architecture.
2. Follow the six-step Delivery Framework: Requirements → Core Entities → API → Data Flow → High-Level Design → Deep Dives.
3. Generate a Mermaid architecture diagram at Step 5 and iterate with the learner.
4. Give the complete design only when explicitly requested, for example "show me the design" or "I give up".
5. Review the learner's design for soundness, tradeoffs, and possible improvements.
6. After review passes, save pattern cards with architecture diagrams and write the Log according to the skill's confirmation rules.

## Pattern Card Rules

- **Existing pattern**: add the problem name to frontmatter `problems[]`, append a Problems table row, and update `updated`.
- **New pattern**: create a file from `Templates/SD Pattern.md`, assign the highest existing ID plus one, and fill all fields.
- `difficulty` describes the pattern's complexity, not a particular problem's difficulty.
- Use the pattern title as the filename, removing filesystem-invalid characters: `/ \ : * ? " < > |`.
- Use tags in the form `[system-design/pattern, system-design/{category-slug}]`.

## Log Rules

- Use one `##` section per problem.
- Include the pattern wikilink `[[pattern name]]`, difficulty, result emoji, notes, and time.
- Include Requirements (functional and non-functional) and Key Decisions subsections.
- Keep frontmatter `problems_solved` consistent with the body sections.
- Name the file `YYYY-MM-DD.md`.
- Append to an existing daily Log rather than overwriting it.

## Category Values

Use these category values to match the Dataview grouping keys:

- Storage & Database
- Caching
- Message Queue & Streaming
- Load Balancing & Networking
- API Design
- Consistency & Consensus
- Scaling & Partitioning
- Real-time & Push
- Search & Indexing
- Security & Auth
- Observability
- Microservices

## Hello Interview Delivery Framework

The first five steps establish functional requirements coverage; the full six-step process addresses non-functional requirements.

1. **Requirements**: functional requirements, non-functional requirements (QPS, latency, availability, and consistency), and back-of-envelope estimates.
2. **Core Entities**: core entities and their relationships, focused on business concepts rather than full schemas.
3. **API or Interface**: core interfaces (REST, gRPC, or WebSocket), focused on inputs and outputs.
4. **Data Flow**: the complete path from a user request to final storage or a response.
5. **High-Level Design**: core components and their connections, shown in a Mermaid architecture diagram.
6. **Deep Dives**: examine 2-3 components to address scaling, consistency, and availability.

Let the learner think at each step. Offer hints when they are stuck rather than directly supplying answers.

> See `[[Frameworks/Delivery Framework]]` for detailed framework notes.

## Guiding Heuristics

Use these principles during Phase 1 guidance.

### Core principles

- **Derive architecture from requirements**: help the learner reason toward a design rather than memorize it.
- **Make tradeoffs explicit**: every decision has costs; describe them clearly.
- **Estimate scale**: reason about QPS, latency, and storage orders of magnitude.
- **Design incrementally**: start simple, then explain how to scale.

## Solution Folder Convention

Each system design session has a folder containing all its artifacts:

```text
Learning/Practice/System-Design/
├── Solutions/
│   ├── Bitly-2026-06-14/
│   │   ├── progress.md          # Progress file; tags: [system-design/wip]
│   │   └── Bitly.excalidraw.md  # Excalidraw canvas
│   ├── Bitly-2026-08-15/        # A second session on the same topic
│   │   ├── progress.md
│   │   └── Bitly.excalidraw.md
│   ├── YouTube-2026-07-01/
│   │   ├── progress.md
│   │   └── YouTube.excalidraw.md
```

### Folders

- Use `Learning/Practice/System-Design/Solutions/<short-topic>-<started-date>/`, such as `Dropbox-2026-06-24`.
- Distinguish repeated sessions on the same topic by date.
- Do not create session artifacts in the vault-root `Excalidraw/` or `Attachments/` folders.
- Keep the folder after Phase 3 as a learning record.

### progress.md

- Frontmatter must include `topic`, `started`, and one lifecycle status tag below.
- Include a Progress table for each Delivery Framework step, Pending Questions, Key Learnings, and the next step for resuming. New files use a Next Session section; preserve the legacy heading in existing files.
- The Home.md SD tab detects `system-design/wip` and `system-design/planned`: WIP entries show "Continue →", and planned entries appear in the upcoming practice queue.
- After Phase 3, replace the status tag with `system-design/done` and retain the files.

#### Status lifecycle

```text
system-design/planned → system-design/wip → system-design/done
```

- `planned`: a learning plan has pre-created a Solution skeleton, but practice has not started; all six steps remain ⬜.
- `wip`: practice is in progress. New sessions created by `/sysd-solve <topic>` start here.
- `done`: design, review, and Phase 3 saving are complete.
- A direct `/sysd-solve` without arguments automatically resumes only actual WIP sessions and does not list planned ones. A `/practice` handoff to a new problem asks for a topic instead of restoring unrelated WIP.
- When a planned topic is selected, replace its status with WIP and continue from progress.md's recorded next step.

### Excalidraw

- Name the canvas `<short-topic>.excalidraw.md`, such as `Bitly.excalidraw.md`.
- Create it when `/sysd-solve` starts a new session, pre-filled with all six Delivery Framework headings.
- Embed it from progress.md using `![[...]]`.
- Use uncompressed JSON in a `json` code block. The Excalidraw plugin compresses it when opened.

### Generate the Excalidraw template

Run `node scripts/sd-excalidraw-template.js "<topic>"`.

- The script pre-fills all six Delivery Framework headings and the FR/NFR, Back-of-Envelope, Write Flow, and Read Flow subheadings.
- It outputs uncompressed JSON, which the Excalidraw plugin compresses when opened.
- Edit `scripts/sd-excalidraw-template.js` to change the template layout.

## Diagram Conventions

- Use Mermaid as the primary diagram tool, embedded directly in Markdown for native Obsidian rendering.
- Use `graph LR` for architecture diagrams flowing left to right.
- Group components with `subgraph`, such as Client, Server, and Data Layer.
- Label data flows with protocols and directions, such as HTTP, gRPC, Pub/Sub, or CDC.
- For detailed hand-drawn diagrams, use Excalidraw and save shared files in `Learning/Practice/System-Design/Attachments/`.
- Store reference architectures in each Pattern card's Architecture Diagram section as Mermaid.
- Store the session's architecture snapshot in the Log's Architecture section as Mermaid.

## Related Plans and Modules

- **[[../../Plans/AISA/00_plan|AISA]]**: AI Solutions Architect, focused on cloud architecture.
- **Algorithm**: LeetCode practice for coding skills.
- **Frontend**: React and Next.js practice.

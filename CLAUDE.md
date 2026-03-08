# Obsidian Vault: Workspace

## Vault Overview

This is Ted's personal Obsidian vault for knowledge management, reading notes, work documentation, and personal thoughts. Content is in both English and Chinese.

## Folder Structure

- **Attachments/** — Media files (images, etc.) for general vault notes. Each Learning plan manages its own attachments under `Learning/<CODE>/Attachments/`
- **Entertainment/** — Hobbies (e.g., Mahjong reference notes)
- **Excalidraw/** — Drawings and diagrams
- **Instapaper Notes/** — Saved article highlights from Instapaper
- **Kanban/** — Kanban boards (uses obsidian-kanban plugin)
- **Matter/** — Article notes from Matter app
- **Inbox/** — Fleeting notes capture. Quick thoughts from any source (reading, work, life). Processed weekly into Zettelkasten or deleted.
- **Zettelkasten/** — Permanent notes. Each note is one atomic idea in your own words, linked to other zettel via `Related::` field. Frontmatter includes `topics` (list of keywords for filtering).
- **Thoughts/** — Personal reflections and ideas
- **Learning/** — Structured learning plans. Each plan lives in a subfolder named by its code (e.g. `Learning/AISA/`). Contains `00_plan.md` (goals, phases, timeline), `00_map.md` (concept map), `Weeks/` (weekly logs), `Courses/`, `Projects/`, and `Attachments/` (plan-specific media). The folder name is the plan identifier — used as shorthand in all commands (`/learning-log AISA`). Managed via `/learning-init`, `/learning-log`, `/learning-review`.
- **Training/** — Legacy learning resources (being migrated to `Learning/`)
- **WeRead/** — Book highlights synced from WeRead (微信读书). **DO NOT MODIFY** — this folder is auto-synced and must remain untouched.
- **Work/** — Work documentation, organized by year and project
  - `archive/` — Past years and completed projects
  - `2026/` — Current year daily notes (`YYYY-MM-DD.md`)
  - `Projects/` — Project pages (one per project, created from template)
  - `Brownbag Sessions/` — Brownbag session plans. Each session has a unique `id` (BB-1, BB-2, ...), `created` date, and acceptance criteria checklist (`## 验收标准`). Status is auto-inferred from the checklist: all unchecked → planning, partially checked → in-progress, all checked → done. Created via `/brownbag <topic>`. Index at `Brownbag Sessions/Brownbag Sessions.md`.

## Key Files

- **Home.md** — Dashboard using Dataview queries. Avoid modifying unless asked.
- **sortspec.md** — Custom file explorer sort order (Custom File Explorer Sorting plugin). Do not delete.
- **Work/Work Dashboard.md** — Work dashboard with task views and project summary.
- **Templates/Work Daily.md** — Template for daily work notes.
- **Templates/Work Project.md** — Template for project pages.
- **Templates/Learning Plan.md** — Template for `00_plan.md` (learning plan goals and phases).
- **Templates/Learning Week.md** — Template for weekly learning logs (`Weeks/YYYY-WXX.md`).
- **Templates/Brownbag Session.md** — Template for brownbag session plans (used by `/brownbag` command).

## Conventions

- **Frontmatter**: Notes use YAML frontmatter for metadata (author, tags, dates, status, etc.)
- **Links**: Use `[[wikilinks]]` for internal linking
- **Language**: Mix of English and Chinese — match the language of the content being worked on
- **Formatting**: Use headers (##), callouts (`> [!tip]`), blockquotes, and lists. Follow existing patterns in the vault.
- **Attachments**: Place images/media in `Attachments/`. Exception: Learning plan assets (screenshots, diagrams, etc.) go in `Learning/<CODE>/Attachments/`
- **New notes**: Place in the appropriate existing folder. If unsure, use `Thoughts/`
- **Zettel notes**: One idea per note, written in your own words (not copy-paste). Use `[[wikilinks]]` in the `Related::` field to connect to other zettel. Title should be a descriptive statement (e.g., "Distributed systems trade consistency for availability").
- **Inbox notes**: No format required. Just capture the thought. Run `/inbox-review` weekly to process: convert to zettel or archive to `Inbox/archive/YYYY-MM/`.
- **Project tasks**: Group tasks under `### ProjectName` headings in daily notes (e.g., `### IS2`, `### IFM`). The heading name must match the filename in `Work/Projects/`. Dataview queries use `t.section.subpath` to filter tasks by project.
- **Dataview tag filtering**: Use `p.file.tags.includes("#tag")` (not `p.tags`) in dataviewjs queries for reliable tag matching.

## Installed Plugins

Dataview, Kanban, Calendar, Excalidraw, Tag Wrangler, Table Editor, Footnotes, Mind Map, Homepage, Hider, Style Settings, URL into Selection, WeRead, Plugin Update Tracker, Custom File Explorer Sorting, Spaced Repetition

## Rules

1. **NEVER modify anything in the `WeRead/` folder** — it is synced externally
2. Preserve existing frontmatter when editing notes
3. When adding wikilinks, only link to notes that exist or that you are creating
4. Keep the vault organized — use existing folders before creating new ones
5. Match the language of the source content (English or Chinese)

## Book Learning System

See `Books/CLAUDE.md` for the full reading workflow.
When working inside the `Books/` folder, that file takes precedence for all book-related tasks.

# Obsidian Vault: General Notes

## Vault Overview

This is Ted's personal Obsidian vault for knowledge management, reading notes, work documentation, and personal thoughts. Content is in both English and Chinese.

## Folder Structure

- **Attachments/** — Media files (images, etc.)
- **Entertainment/** — Hobbies (e.g., Mahjong reference notes)
- **Excalidraw/** — Drawings and diagrams
- **Instapaper Notes/** — Saved article highlights from Instapaper
- **Kanban/** — Kanban boards (uses obsidian-kanban plugin)
- **Matter/** — Article notes from Matter app
- **Thoughts/** — Personal reflections and ideas
- **Training/** — Learning resources and course notes
- **Book Summaries/** — AI-generated thematic summaries of WeRead books (in English). Each summary links back to its WeRead source.
- **WeRead/** — Book highlights synced from WeRead (微信读书). **DO NOT MODIFY** — this folder is auto-synced and must remain untouched.
- **Work/** — Work documentation, organized by year and project
  - `archive/` — Past years and completed projects
  - `2026/` — Current year daily notes (`YYYY-MM-DD.md`)
  - `Projects/` — Project pages (one per project, created from template)

## Key Files

- **Home.md** — Dashboard using Dataview queries. Avoid modifying unless asked.
- **Work/Work Dashboard.md** — Work dashboard with task views and project summary.
- **Templates/Work Daily.md** — Template for daily work notes.
- **Templates/Work Project.md** — Template for project pages.

## Conventions

- **Frontmatter**: Notes use YAML frontmatter for metadata (author, tags, dates, status, etc.)
- **Links**: Use `[[wikilinks]]` for internal linking
- **Language**: Mix of English and Chinese — match the language of the content being worked on
- **Formatting**: Use headers (##), callouts (`> [!tip]`), blockquotes, and lists. Follow existing patterns in the vault.
- **Attachments**: Place images/media in `Attachments/`
- **New notes**: Place in the appropriate existing folder. If unsure, use `Thoughts/`
- **Project tasks**: Group tasks under `### ProjectName` headings in daily notes (e.g., `### IS2`, `### IFM`). The heading name must match the filename in `Work/Projects/`. Dataview queries use `t.section.subpath` to filter tasks by project.
- **Dataview tag filtering**: Use `p.file.tags.includes("#tag")` (not `p.tags`) in dataviewjs queries for reliable tag matching.

## Installed Plugins

Dataview, Kanban, Calendar, Excalidraw, Tag Wrangler, Table Editor, Footnotes, Mind Map, Homepage, Hider, Style Settings, URL into Selection, WeRead, Plugin Update Tracker

## Rules

1. **NEVER modify anything in the `WeRead/` folder** — it is synced externally
2. Preserve existing frontmatter when editing notes
3. When adding wikilinks, only link to notes that exist or that you are creating
4. Keep the vault organized — use existing folders before creating new ones
5. Match the language of the source content (English or Chinese)

## Book Learning System

See `Books/CLAUDE.md` for the full reading workflow.
When working inside the `Books/` folder, that file takes precedence for all book-related tasks.

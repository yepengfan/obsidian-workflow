---
name: zettelkasten-inbox-review
description: >-
  Weekly inbox processing — convert to zettel or archive. Use for /zettelkasten-inbox-review.
disable-model-invocation: true
---

<!-- module: zettelkasten -->
> [!GUARD] Read `system/modules/zettelkasten/module.md`. If `enabled: false` → reply "⛔ Module **zettelkasten** is disabled. Enable it via `/module-toggle zettelkasten`." and STOP. Do NOT proceed.

---

Review all notes in the Inbox/ folder and process them into zettel or archive them.

Workflow:
1. Read all `.md` files in `Inbox/` (skip `.gitkeep`)
2. For each note, display its content and ask the user: **[z] convert to zettel / [a] archive / [s] skip**
3. If **convert to zettel**:
   - Draft a zettel following the same process as `/zettel`:
     - **Title**: a descriptive statement
     - **Content**: 3-8 sentences in the user's own words
     - **topics**: 2-5 relevant keywords
     - **Related**: search `Zettelkasten/` for thematic connections, add wikilinks
     - **source**: leave as `""` (inbox notes are original thoughts, not from a book)
   - Present the draft to the user for review/edit
   - On confirmation, create the file in `Zettelkasten/` using the `Templates/Zettel.md` format
   - Move the original inbox note to `Inbox/archive/YYYY-MM/` (create folder if needed)
4. If **archive**: move the note to `Inbox/archive/YYYY-MM/` without creating a zettel
5. If **skip**: leave the note untouched, move on to the next one
6. After processing all notes, show a summary: X converted, Y archived, Z skipped

Rules:
- Never create zettel without user confirmation
- Never delete inbox notes — always archive them to `Inbox/archive/YYYY-MM/`
- Process notes one at a time — do not batch-convert without review
- Write zettel in the same language as the inbox note
- Filename for zettel: title in lowercase with spaces replaced by hyphens

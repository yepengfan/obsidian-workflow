---
name: book-read
description: >-
  Resume a reading session — pick an in-progress book, choose a chapter, and enter
  the Feynman/review workflow. Use when the user wants to study a book they're
  reading, do a Feynman check, or says /book/read or /book-read.
disable-model-invocation: true
---

<!-- module: book-learning -->
> [!GUARD] Read `system/modules/book-learning/module.md`. If `enabled: false` → reply "⛔ Module **book-learning** is disabled. Enable it via `/module-toggle book-learning`." and STOP. Do NOT proceed.

Resume a reading session: $ARGUMENTS

This command is a **router**, not the workflow itself. Its only job is to pick the right
**book + chapter + step**, load context, then hand off to the real reading workflow in
`Learning/Books/CLAUDE.md`. Do **not** duplicate Feynman/review rules here — that file is
the single source of truth. Read it before entering any step.

## Step 1 — Pick the book

Scan `Learning/Books/*/meta.md` for entries with `status: reading`. For each, read
`title`, `author`, and `weread_progress`.

- **`$ARGUMENTS` names/fuzzy-matches exactly one reading book** → use it, skip the prompt.
- **Only one reading book exists** → use it, skip the prompt.
- **Otherwise** → use `AskUserQuestion` to let the user pick (reading books are few, ≤4;
  build options dynamically from the scan — never hardcode titles). Show `title · author ·
  WeRead N%` per option.

## Step 2 — Pick the chapter

Read the chosen book's `MOC.md` (chapter list) and `meta.md`'s `progress:` tracker.

**Report a progress table in conversation** (not `AskUserQuestion` — chapters often exceed 4),
then let the user say a chapter number. Format per `Learning/Books/CLAUDE.md` → "Cross-session
progress display":

```
📖 {Book} — 进度

Ch1 {title}:  ✅ feynman   ○ write
Ch2 {title}:  ○ feynman    ○ write
Ch3 {title}:  ○ 未开始
...

读哪章？
```

Derive each chapter's marks from the tracker: `feynman`/`write` absent or `not_started` → ○,
`in_progress` → ⚠️, `done` → ✅. If the tracker is empty (`progress: {}`, a freshly onboarded
book), show all chapters as ○ 未开始.

⚠️ **EPUB metadata noise**: `book_init.py` sometimes emits duplicate/placeholder chapters from
a messy EPUB TOC (e.g. Learning DDD's `Ch17–Ch32` are just "Chapter 1"–"Chapter 16" repeats of
the real titled chapters). Present only the chapters with real titles; skip bare `Chapter N`
placeholders. If you can't reliably tell real from noise, show the full list and flag that it
contains TOC noise so the user isn't misled.

## Step 3 — Pick the step

Use `AskUserQuestion` to choose which part of the reading loop to enter:

- **费曼测试** — Feynman sparring (the most common; `Learning/Books/CLAUDE.md` → Step 2)
- **查 source / 验证** — on-demand research (that file → "Find sources / verify")
- **我写你 review** — structure & accuracy review of what the user wrote (that file → Step 3)
- **只是继续读** — no AI step; just surface context and progress, then stop

## Step 4 — Load context and enter

Follow `Learning/Books/CLAUDE.md` → "Context loading" for the chosen book+chapter:

```
1. Read {Book}/meta.md       → archetype, output target, progress tracker
2. Read {Book}/MOC.md         → progress, available chapters
3. Read {Book}/chapters/{chapter} skeleton (if exists) → chapter scope
4. Read {Book}/notes/{chapter}.md (if exists) → existing sources
5. Read WeRead highlights for the chapter (via weread_source) → what the user focused on
6. Load archetype-specific Feynman question style
```

Then enter the step chosen in Step 3, following that file's rules exactly. For 费曼测试, that
means opening with "用你自己的话解释一下这章的核心内容。" and giving **no** hints — do not let
this router's context-loading leak book content into the opener.

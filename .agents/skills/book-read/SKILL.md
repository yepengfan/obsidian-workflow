---
name: book-read
description: >-
  Resume a reading session — pick an in-progress book, choose a chapter, and enter
  the capture (落盘) workflow. Use when the user wants to study a book they're
  reading, record their understanding of a chapter, or says /book-read.
disable-model-invocation: true
---

<!-- module: book-learning -->
> [!GUARD] Read `system/modules/book-learning/module.md`. If `enabled: false` → reply "⛔ Module **book-learning** is disabled. Enable it via `/module-toggle book-learning`." and STOP. Do NOT proceed.

Resume a reading session: $ARGUMENTS

This command is a **router**, not the workflow itself. Its only job is to pick the right
**book + chapter + step**, load context, then hand off to the real reading workflow in
`Learning/Books/CLAUDE.md`. Do **not** duplicate the capture-loop rules here — that file is
the single source of truth. Read it before entering any step.

## Step 1 — Pick the book

Scan `Learning/Books/*/meta.md` for entries with `status: reading`. For each, read
`title` and `author`. For the progress badge, resolve WeRead progress **live** — do
**not** read the static `weread_progress` field directly (it is a hand-copied snapshot
that goes stale; PR #156 demoted it to fallback-only). Instead:

1. Read `weread_source` from meta.md → open that plugin-synced WeRead note → use its
   frontmatter `progress`. This is the single source of truth (same as Home.md and Step 4).
2. Only if `weread_source` is missing or the note can't be found → fall back to the
   static `weread_progress`.

- **`$ARGUMENTS` names/fuzzy-matches exactly one reading book** → use it, skip the prompt.
- **Only one reading book exists** → use it, skip the prompt.
- **Otherwise** → use `AskUserQuestion` to let the user pick (build options dynamically from
  the scan — never hardcode titles). Show `title · author · WeRead N%` (live) per option.

## Step 2 — Pick the chapter

Read the chosen book's `MOC.md` (chapter list) and `meta.md`'s `progress:` tracker.

**First, run progress-driven pre-fill** (see `Learning/Books/CLAUDE.md` →
"Progress-driven pre-fill (batch)"): check the full-text cache per that file's
"Session-start check" — **build if missing** (no confirmation needed); **if stale**
(source hash changed), ask before rebuilding and skip pre-fill until confirmed.
Then detect read chapters (WeRead sections with ≥1 highlight) and for any read chapter
without a map yet, generate + append its map to `understanding.md` and set
`progress.chNN.map = done`. Skip silently for iBooks-only / PDF / no-cache books
(note why). Then build the table from the now-current tracker.

**Report a progress table in conversation** (not `AskUserQuestion` — chapters often exceed 4),
then let the user say a chapter number. Use the exact table format from
`Learning/Books/CLAUDE.md` → "Cross-session progress display" (single source of truth — follow
it rather than re-inventing a layout here).

Derive each chapter's marks from meta.md's `progress:` tracker: the `map` and `understanding`
fields — absent or `not_started` → ○, `done` → ✅. If the tracker is empty (`progress: {}`, a
freshly onboarded book), show all chapters as ○ 未开始. (Older books may still carry legacy
`feynman`/`write` fields — ignore them for display.)

⚠️ **EPUB metadata noise**: `book_init.py` sometimes emits duplicate/placeholder chapters from
a messy EPUB TOC (e.g. Learning DDD's `Ch17–Ch32` are just "Chapter 1"–"Chapter 16" repeats of
the real titled chapters). Present only the chapters with real titles; skip bare `Chapter N`
placeholders. If you can't reliably tell real from noise, show the full list and flag that it
contains TOC noise so the user isn't misled.

## Step 3 — Pick the step

Use `AskUserQuestion` to choose which part of the reading loop to enter:

- **落盘理解** — the capture loop: AI generates the chapter's 思维导图 + 核心概念, you add your
  understanding in your own words, AI verifies and stores both (`Learning/Books/CLAUDE.md` →
  "The capture loop"). The most common step.
- **查 source / 验证** — on-demand research (that file → "Find sources / verify")
- **只是继续读** — no AI step; just surface context and progress, then stop

## Step 4 — Load context and enter

Load context per `Learning/Books/CLAUDE.md` → "Context loading" (that section is the single
source of truth for the sequence — do not restate it here). For the full-text cache, follow
that file's "Session-start check": build if missing; ask before rebuilding if stale.

Then enter the step chosen in Step 3, following that file's rules exactly. For 落盘理解:
- If Step 2's pre-fill already set `progress.chNN.map = done` for this chapter, **skip map
  generation** — show the existing map from `understanding.md` and go straight to prompting
  for the user's own understanding (per `Learning/Books/CLAUDE.md` → "The capture loop").
- Otherwise, generate the 思维导图 + 核心概念 first (from the full-text cache + capture-layer
  highlights), show it, then prompt for the user's understanding.

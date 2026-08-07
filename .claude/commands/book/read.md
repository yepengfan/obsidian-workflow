<!-- module: book-learning -->
> [!GUARD] Read `system/modules/book-learning/module.md`. If `enabled: false` → reply "⛔ Module **book-learning** is disabled. Enable it via `/module-toggle book-learning`." and STOP. Do NOT proceed.

Resume a reading session: $ARGUMENTS

This command is a **router**, not the workflow itself. Its only job is to pick the right
**book + chapter + step**, load context, then hand off to the real reading workflow in
`Learning/Books/CLAUDE.md`. Do **not** duplicate Feynman/review rules here — that file is
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
- **Otherwise** → use `AskUserQuestion` to let the user pick (reading books are few, ≤4;
  build options dynamically from the scan — never hardcode titles). Show `title · author ·
  WeRead N%` (live) per option.

## Step 2 — Pick the chapter

Read the chosen book's `MOC.md` (chapter list) and `meta.md`'s `progress:` tracker.

**Report a progress table in conversation** (not `AskUserQuestion` — chapters often exceed 4),
then let the user say a chapter number. Use the exact table format from
`Learning/Books/CLAUDE.md` → "Cross-session progress display" (single source of truth — follow
it rather than re-inventing a layout here).

Derive each chapter's marks from meta.md's `progress:` tracker: a `feynman`/`write` field that
is absent or `not_started` → ○, `in_progress` → ⚠️, `done` → ✅. If the tracker is empty
(`progress: {}`, a freshly onboarded book), show all chapters as ○ 未开始.

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

Load context per `Learning/Books/CLAUDE.md` → "Context loading" (that section is the single
source of truth for the sequence — do not restate it here). If the chosen step is 费曼测试,
also do that file's Feynman "Preparation" reads (chapter skeleton + existing notes) before
opening.

Then enter the step chosen in Step 3, following that file's rules exactly. For 费曼测试, that
means opening with "用你自己的话解释一下这章的核心内容。" and giving **no** hints — do not let
this router's context-loading leak book content into the opener.

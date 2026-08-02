---
name: book-init
description: >-
  Onboard a new book into Learning/Books/ — locate EPUB/PDF, run book_init.py, confirm metadata. Use when adding a book or /book/book-init.
disable-model-invocation: true
---

<!-- module: book-learning -->
> [!GUARD] Read `system/modules/book-learning/module.md`. If `enabled: false` → reply "⛔ Module **book-learning** is disabled. Enable it via `/module-toggle book-learning`." and STOP. Do NOT proceed.

New book onboarding: $ARGUMENTS

Read `Learning/Books/CLAUDE.md` for the full reading workflow this book will enter (archetypes, per-unit steps, folder boundaries). This command only handles **onboarding a new book** (the "New book onboarding" section there is the source of truth for that scope) — it does not touch the per-unit Feynman/write/review cycle that follows, which is a separate, ongoing workflow described later in that same file.

## Step 1 — Confirm book identity

Parse `$ARGUMENTS` for a book title (and author, if given). Confirm with the user:
- **Book title** (exact, used for the vault folder name)
- **Author**
- **Archetype**: `technical-reference` or `cognitive-mental-model` (ask if unclear — this drives output target and Feynman question style, see `Learning/Books/CLAUDE.md` → "Book archetypes")
- **Reading channel**: WeRead / EPUB / PDF / EPUB + WeRead

If the user already gave all of these in `$ARGUMENTS`, skip re-asking and confirm briefly instead.

## Step 2 — Locate the source file (EPUB/PDF only)

Skip this step entirely if reading channel is pure WeRead.

Ebooks are synced from S3 to `~/Library/ebooks/` (see `Learning/Books/.bookrc.example`). Search there first instead of asking the user for a path:

```bash
ls ~/Library/ebooks | grep -i "<title fragment>"
```

- **Exactly one match** → confirm it with the user before proceeding ("找到 `{filename}`，用这个吗？").
- **Multiple matches** (e.g. different editions/languages, as happened with DDIA and Thinking Fast and Slow) → list them with file size and ask the user which one they're actually reading. Do not guess.
- **No match** → ask the user for the file path directly, or confirm they only want WeRead-based tracking (no local EPUB/PDF).

## Step 3 — Run book_init.py (EPUB/PDF only)

```bash
"Learning/Books/.venv/bin/python3" "Learning/Books/book_init.py" \
  --file "<resolved path from Step 2>" \
  --output "Learning/Books"
```

This generates `Learning/Books/{Book Title}/` with `meta.md`, `MOC.md`, `chapters/`, `notes/`, `feynman/`. `meta.md`'s frontmatter already contains the resolved absolute path of the source file — keyed as `epub_path` for `.epub` sources, `pdf_path` for `.pdf` sources — **do not ask the user to re-supply it**, and do not manually re-type it elsewhere.

If `--title` produced a folder name the user doesn't like (bad EPUB metadata), rerun with `--title "Correct Title"` — do not manually rename files.

If the reading channel is pure WeRead (no EPUB/PDF), skip this step and create the folder structure manually per `Learning/Books/CLAUDE.md` step 3 (no `epub_path`/`pdf_path` field in that case).

## Step 4 — Fill in fields book_init.py doesn't know

`book_init.py` cannot infer `archetype`, `output_target`, or `reading_channel` (WeRead-only books also need `weread_source`). After generation, edit `meta.md` frontmatter to add:

```yaml
archetype: <technical-reference | cognitive-mental-model>
output_target: <articles/{slug}/ | journal/>
reading_channel: <EPUB | WeRead | EPUB + WeRead>
weread_source: "WeRead/{Folder}/{File}.md"   # only if a WeRead sync exists for this book
```

Check whether a matching `WeRead/` folder exists for this book title; if so, add `weread_source` even when the primary reading channel is EPUB (matches the pattern used by existing books).

## Step 5 — Report

```
✅ {BookTitle} 已加入系统
   archetype: {X} · output: {Y} · channel: {Z}
   epub_path/pdf_path: {path, or "—" if WeRead-only}

开始读书时告诉我你在读哪个 chapter/concept。
```

Do not push further — Books Index.md discovers the new book automatically via Dataview (reads `status: reading` from `meta.md`), no manual index edit needed.

## Retrofit — backfill epub_path/pdf_path on existing books

*Triggered when user says "帮我补一下 epub_path" / "检查一下哪些书缺 epub 路径"*

For books already onboarded before this automation existed (or WeRead-only books that later got an EPUB/PDF), `meta.md` may be missing `epub_path`/`pdf_path` even though a matching file exists in `~/Library/ebooks/`.

1. Scan `Learning/Books/*/meta.md` for entries missing both `epub_path` and `pdf_path`.
2. For each, fuzzy-match the folder/title against `ls ~/Library/ebooks/`.
3. **Exactly one plausible match** → propose adding it, list the exact line you'll insert, and wait for confirmation (per this vault's "before you act" rule — do not write without approval).
4. **Multiple candidates** (editions/translations) → ask the user which one, same as Step 2 above. Never guess between an English original and a translation, or between editions.
5. **No match** → leave as-is, note it in the report (book may genuinely be WeRead-only).

Report format:
```
📚 epub_path 补全检查
✅ {Book} → 已有 epub_path，跳过
❓ {Book} → 找到候选: {file1}, {file2} — 用哪个？
➕ {Book} → 找到唯一匹配 {file} — 要加吗？
⚠️ {Book} → 未找到匹配，跳过（可能是纯 WeRead）
```

---
name: book-init
description: >-
  Onboard a new book into Learning/Books/ — locate EPUB/PDF, run book_init.py, confirm metadata. Use when adding a book or /book-init.
disable-model-invocation: true
---

<!-- module: book-learning -->
> [!GUARD] Read `system/modules/book-learning/module.md`. If `enabled: false` → reply "⛔ Module **book-learning** is disabled. Enable it via `/module-toggle book-learning`." and STOP. Do NOT proceed.

New book onboarding: $ARGUMENTS

Read `Learning/Books/CLAUDE.md` for the full reading workflow this book will enter (capture layers, the capture loop, folder boundaries). This command only handles **onboarding a new book** (the "New book onboarding" section there is the source of truth for that scope) — it does not touch the per-chapter capture cycle that follows, which is a separate, ongoing workflow described later in that same file.

## Step 1 — Confirm book identity

Parse `$ARGUMENTS` for a book title (and author, if given). Confirm with the user:
- **Book title** (exact, used for the vault folder name)
- **Author**
- **Archetype**: `technical-reference` or `cognitive-mental-model` (ask if unclear — a light tag for granularity/reflection style, see `Learning/Books/CLAUDE.md` → "Book archetypes")
- **Reading channel**: WeRead / iBooks / EPUB / PDF / EPUB + WeRead / EPUB + iBooks

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

This generates `Learning/Books/{Book Title}/` with `meta.md`, `MOC.md`, `chapters/`, `notes/`, and `understanding.md` (the per-chapter capture record — the system's terminal output). `meta.md`'s frontmatter already contains the resolved absolute path of the source file — keyed as `epub_path` for `.epub` sources, `pdf_path` for `.pdf` sources — **do not ask the user to re-supply it**, and do not manually re-type it elsewhere.

For `.epub` sources it also auto-fills, when found — **do not ask the user to re-supply these either**:
- `cover:` — the EPUB's embedded cover image, extracted to `<book>/cover.{ext}` (vault-relative path). This is the primary cover source for books with no WeRead sync (e.g. iBooks-only channel); Home.md's card resolves it via `app.vault.getResourcePath()`.
- `ibooks_source:` — vault-relative path to a fuzzy-matched `ibooks-highlights/{title}.md` (Apple Books highlights export), analogous to `weread_source` but for the iBooks reading channel. Unlike WeRead's per-book folder, this is a single flat file with no chapter headings and no reading-progress field — metadata only, no chapter linking.

If `--title` produced a folder name the user doesn't like (bad EPUB metadata), rerun with `--title "Correct Title"` — do not manually rename files.

If the reading channel is pure WeRead (no EPUB/PDF), skip this step and create the folder structure manually: `{BookTitle}/` with `meta.md`, `MOC.md`, `understanding.md`, `chapters/`, and `notes/` — see `Learning/Books/CLAUDE.md` → "Per-book folder structure" (no `epub_path`/`pdf_path` field in that case).

## Step 4 — Fill in fields book_init.py doesn't know

`book_init.py` cannot infer `archetype` or `reading_channel` (WeRead-only books also need `weread_source`). After generation, edit `meta.md` frontmatter to add:

```yaml
archetype: <technical-reference | cognitive-mental-model>
reading_channel: <EPUB | WeRead | iBooks | EPUB + WeRead | EPUB + iBooks>
weread_source: "WeRead/{Folder}/{File}.md"   # only if a WeRead sync exists for this book
# output_target is optional — the per-chapter understanding.md record is the default output;
# only add it if this book has a dedicated downstream (rare).
```

Check whether a matching `WeRead/` folder exists for this book title; if so, add `weread_source` even when the primary reading channel is EPUB (matches the pattern used by existing books).

`ibooks_source` and `cover` (when a matching `ibooks-highlights/*.md` file or an embedded EPUB cover was found) are already auto-filled by Step 3 — don't add them manually or ask the user for them. If the reading channel is iBooks but no `ibooks-highlights/{title}.md` file exists yet (user hasn't synced highlights), leave `ibooks_source` unset — do not fabricate a path.

## Step 5 — Build the full-text cache (EPUB only)

The per-chapter map is generated from the book's actual text, so building the full-text cache is a **standard onboarding step** for EPUB books:

```bash
"Learning/Books/.venv/bin/python3" Learning/Books/extract_fulltext.py \
  --book "Learning/Books/{Book Title}"
```

- Skip for pure-WeRead or PDF-only books (extractor is EPUB-only). Note it in the report so the user knows chapter maps won't be auto-generated for that book.
- If it errors on a **chapter-count mismatch** (`chapters/` disagrees with the EPUB TOC — TOC-noise duplicates), don't guess: report it and leave the cache unbuilt; the book still works with a highlights-only record.

## Step 6 — Report

```
✅ {BookTitle} 已加入系统
   archetype: {X} · channel: {Z}
   epub_path/pdf_path: {path, or "—" if WeRead-only}
   full-text cache: {✅ N 章, or "— (WeRead/PDF only)", or "⚠️ 章节不匹配，未建"}

开始读书时告诉我你在读哪一章。
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

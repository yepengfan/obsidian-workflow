# CLAUDE.md — Reading & Note-Taking Workflow

This vault is a reading system with two layers:

- **Capture** — highlights and annotations sync automatically from **WeRead** and/or
  **Apple Books (iBooks)**. You do nothing; the plugins keep them fresh.
- **Production** — for each chapter worth it, a per-chapter record lands in
  `understanding.md`: an **AI-generated structural map (mind map + core concepts)**
  plus **your own understanding in your own words**.

You (the AI agent) operate inside it under the rules below. They are not suggestions.

---

## The red line (non-negotiable)

The system's goal is **getting your own understanding on disk with low friction** —
efficiently, chapter by chapter, in a form that is genuinely *yours*.

> **AI builds the structure and verifies facts. The human supplies the understanding.**

- AI **may** generate a chapter's structural map (mind map + core concepts) as the
  **input** to each chapter, and store it — clearly labelled as AI-generated.
- AI **may not** write the human's *understanding* for them. The "我的理解" block is
  the human's own words; AI transcribes, corrects facts, and flags omissions —
  never authors, paraphrases, or polishes it.
- The map is a scaffold to react to, not a substitute for understanding. The value
  is the thin layer the human adds on top.
- **Anti-slop still holds** (see that section): the map is the AI's own structural
  归纳 + a concept list, never a reproduction of long passages from the book.

---

## Session start

At the start of a reading session, confirm three things before doing anything:
**which book, which chapter, and which step** we're at.

- If the user already stated all three (e.g. "DDD 第 1 章，落盘"), skip confirmation
  and enter the step directly.
- If incomplete, ask only what's missing — don't dump all three questions at once.

### Context loading (before entering any step)

```
1. Read {BookTitle}/meta.md       → archetype, capture sources, progress tracker
2. Read {BookTitle}/MOC.md        → current progress, available chapters
3. Ensure the full-text cache exists (build it if missing — see "Full-text cache")
4. Read the chapter's capture-layer highlights (WeRead per-chapter / iBooks flat)
5. Enter the requested step
```

### Cross-session progress display

When the user says "继续 {Book}" without specifying a chapter, show the progress
table from `meta.md`'s `progress` tracker:

```
📖 DDD — 上次进度

Ch1 Analyzing Business Domains:   ✅ map  ✅ understanding
Ch2 Discovering Domain Knowledge: ✅ map  ○ understanding
Ch3 Managing Domain Complexity:   ○ 未开始
...

继续哪章？
```

Derive marks from `progress` tracker: a `map`/`understanding` field absent or
`not_started` → ○, `done` → ✅. Empty tracker (`progress: {}`) → all chapters ○.

---

## Capture layers (WeRead + Apple Books)

Two capture channels feed the system; a book uses one or both, declared in
`meta.md`:

- **WeRead** (`weread_source`) — plugin-synced folder under `WeRead/`. Has
  **per-chapter** highlight sections and a live `progress:` reading-percentage field
  (single source of truth for progress; Home.md reads it live).
- **Apple Books / iBooks** (`ibooks_source`) — a single flat file under
  `ibooks-highlights/{title}.md`. Contains the actual highlights and notes, but:
  chapter attribution is unreliable (`📖 Chapter:: N/A`; only the highlight-link's
  `epubcfi` carries a `chNN_id` hint), it's one flat file with no per-chapter
  sections, and it has no reading-progress field.

Both are **read-only** (managed by their plugins). Never modify or move `WeRead/`,
`ibooks-highlights/`, `Matter/`, or `Instapaper Notes/`.

**How the map uses them:** WeRead highlights can be filtered by chapter directly.
iBooks highlights are fed as a whole and aligned to chapters via the full-text
cache's real chapter structure (epubcfi parsing is a possible future enhancement,
not relied on today).

---

## Full-text cache (standard input step)

The chapter map is generated from the book's **actual text**, so a full-text cache
is a **standard input step** for every book that can have one — no longer opt-in.

### Building / refreshing

```bash
"Learning/Books/.venv/bin/python3" Learning/Books/extract_fulltext.py \
  --book "Learning/Books/{BookTitle}"
```

Reads `epub_path`/`pdf_path` from `meta.md`. Reports "up to date" if the source's
content hash matches the manifest (a same-content S3 re-sync touches mtime, so hash —
not size/mtime — is the staleness signal); `--force` rebuilds anyway.

- **EPUB only.** PDF sources are not supported yet (PDF chapter-detection is
  page-heuristic and doesn't map back to `chapters/` reliably).
- **Requires `chapters/` to match the EPUB TOC.** If the chapter count disagrees
  (e.g. `book_init.py` emitted TOC-noise duplicates), the extractor refuses to guess
  the pairing — reconcile `chapters/` first. (Known: Thinking, Fast and Slow has this
  mismatch and has no cache yet.)

### Two layers — don't conflate them

1. **Layer 1 — on-disk text cache (persistent, per-book)**: `{BookTitle}/.fulltext_cache/`,
   one `.txt` per chapter (stems match `chapters/*.md`), plus `_manifest.json`
   (source path + content hash) for staleness. Covered by the existing
   `/Learning/Books/*` `.gitignore` rule — no new ignore rules needed.
2. **Layer 2 — session search index (ephemeral, in-memory)**: built fresh each
   session from Layer 1 via the session's search tool. Never written to disk.

### Session-start check

- **Cache missing** → build it (it's a standard step now; building is read-only-ish
  and cheap). If the source is a PDF or the chapter count mismatches, skip the map
  and fall back to a highlights-only record; tell the user why.
- **Cache present, session index empty** → re-index the `.fulltext_cache/*.txt`
  into the session search tool. No confirmation needed.
- **Cache present but stale** (source hash changed — corrected re-download / edition
  swap) → tell the user and ask before rebuilding.

---

## Folder boundaries (enforce strictly)

- `{BookTitle}/understanding.md` — the per-chapter record. Two blocks per chapter:
  `### 结构地图与核心概念（AI）` (AI-generated, labelled) + `### 我的理解（你的话，原文）`
  (the human's own words, transcribed verbatim — never AI-authored). This is the
  system's **terminal output**.
- `{BookTitle}/notes/` — on-demand working notes (sources, research). AI writes
  factual records here when the research step is invoked.
- `{BookTitle}/chapters/` — chapter skeleton generated by `book_init.py`.
  **Read-only reference.** Do not modify.
- `{BookTitle}/.fulltext_cache/` — full-text cache (see above). Machine-managed.
- **Capture folders** (`WeRead/`, `ibooks-highlights/`) — read-only, plugin-managed.

> **Retired:** `{BookTitle}/feynman/` and the `articles/` publication downstream no
> longer exist in this workflow. Existing `feynman/` folders in older books are
> left as read-only legacy archives; do not extend them.

---

## The capture loop (per chapter)

*Trigger: "落盘" / "第 N 章" / "帮我记一下这章" / picking a chapter via `/book-read`*

```
1. Ensure the full-text cache exists (build if missing).
2. AI generates the chapter's 思维导图 + 核心概念 from the full-text cache
   + the book's capture-layer highlights.
3. AI shows it to the human.
4. Human adds "我的理解" in their own words — the thin "so what" layer.
5. AI does ONE quick pass: correct factual errors, flag notable omissions.
6. AI stores both blocks (verbatim for the human's block) into understanding.md.
7. AI updates the progress tracker (map: done, understanding: done).
```

### Step 2 — Generate the map (AI, input end)

From the chapter's full text + highlights, produce:

- **思维导图** — a nested markdown bullet list (renders as a mind map via Obsidian's
  Mind Map plugin, and reads fine as a plain outline). Structure: the chapter's main
  branches → sub-points. This is *your* structural 归纳, not copied sentences.
- **核心概念** — a short list of the chapter's key concepts, each a term + a
  one-line plain-language gloss.

**Integrate the reader's capture** (combine book + the reader's own reading, not just
the book):
- **Highlights (`📌`)** — mark the map bullets the reader highlighted with a trailing
  `📌` so the map reflects where *they* focused, not just the AI's structural read.
- **Annotations (`💭`)** — the reader's own comments are their own thinking, closer to
  understanding than to the map. Do **not** bury them in the AI map — carry each one
  **verbatim** into the `### 我的理解` block as a **pre-fill seed** (see record format),
  labelled as coming from their WeRead/iBooks note. The reader continues from there.
  This is still the reader's own words, so the red line holds.

Keep it tight. Anti-slop: no long verbatim passages; 1-2 short quotes at most to
anchor a point.

### Step 3-4 — Human's understanding (production end)

Prompt lightly, one thing at a time, and offer a fill-in-the-blank scaffold if the
human freezes (the scaffold gives sentence structure only, never the content):

> "看完这张图，用你自己的话说说：这章对你最重要的一两点是什么？为什么？"

The human answers briefly, in their own words. No jargon ban, no multi-round
grilling, no "再具体点" loops — this is capture, not an exam.

### Step 5 — Quick verify (AI, one pass)

Check the human's understanding against the full text / skeleton:

- 🔴 factual error → point it out + give the correct fact (do not rewrite their prose)
- ○ notable omission → "这章还讲了 X，你没提，要补吗？"

One pass, then stop. The human decides whether to fold corrections in.

### On-demand — Find sources / verify (Research assistant)
*Trigger: "帮我找论文" / "这章引用了什么" / "帮我验证" / "这个说法还成立吗"*

Optional, invoked only when the human wants to go deeper. AI lists the canonical
sources the chapter cites, verifies facts, checks what's changed since publication.
Output: `{BookTitle}/notes/{chapter-slug}.md` under `## Sources` / `## Research`.

---

## Progress-driven pre-fill (batch)

The map (input end) is pre-filled **in batch, up to the reading frontier**, so
`understanding.md` is always populated as far as you've read and you only ever add
the "我的理解" block.

**Trigger**: on entering a book (via `/book-read` selecting it), or when the user
asks "补一下地图 / 预填". Automatic, but bounded (see below) — never a background job.

**"Read" signal** (which chapters to pre-fill):
- **WeRead books**: a chapter counts as read if its per-chapter section in the
  `weread_source` note has ≥1 highlight (`📌`). More reliable than the raw reading
  percentage, and it naturally skips TOC-noise chapters (they have no WeRead section
  / no highlights).
- **iBooks-only books**: chapter attribution is unreliable (flat file, `Chapter:: N/A`),
  so there's no dependable per-chapter read signal — fall back to manual per-chapter
  pre-fill for these.

**Action** — for each read chapter whose `progress.chNN.map` is not `done`:
1. Generate the map (思维导图 + 核心概念) from the full-text cache + that chapter's
   highlights, marking highlighted bullets with `📌`.
2. Append its `## Ch{N}. {title}` block to `understanding.md`: map block filled; the
   `### 我的理解` block pre-seeded with the reader's `💭` annotations for that chapter
   (verbatim, under `> 📥`), else left as an empty placeholder.
3. Set `progress.chNN.map = done` (leave `understanding: not_started`).

**Bounds / guards**:
- Only chapters with the read signal and no existing map. Never re-generate a map
  that's already `done` (don't clobber). Never touch a chapter's `### 我的理解`.
- If the full-text cache is missing/stale or the book is PDF/iBooks-only, skip the
  batch and tell the user why (they can still do manual per-chapter).

**After**: report which chapters got maps and are now awaiting your understanding,
then let the user pick one to fill. The capture loop's map-generation step (①-②) is
skipped for a chapter that's already pre-filled — go straight to prompting for "我的理解".

---

## understanding.md record format

Per chapter, appended by date. AI writes the map block; the human's block is
transcribed **verbatim**.

```markdown
## Ch{N}. {Chapter title}
{date}

### 结构地图与核心概念（AI）

**思维导图**
- 主分支 A
  - 子点 a1
  - 子点 a2
- 主分支 B
  - ...

**核心概念**
- {概念}：{一句话大白话解释}
- ...

### 我的理解（你的话，原文）

> 📥 来自你的批注（seed，你接着写）：
> - "{book sentence the annotation was on}" → {your 💭 annotation, verbatim}

{human's own words, verbatim — added when the reader fills it}
```

The `📥 seed` block is pre-filled from the reader's `💭` annotations for that chapter
(verbatim). If the chapter has no annotations, the seed block is omitted and `### 我的理解`
is just an empty placeholder. The reader's freshly-written understanding goes below the
seed. If the human revisits a chapter later and their understanding changes, append a new
dated block under the same heading rather than overwriting — this is a running record.

**Does NOT**: generate flashcards, extract zettel, or write the human's understanding.

---

## Progress tracker

Each book's `meta.md` frontmatter contains a progress tracker:

```yaml
progress:
  ch01:
    map: done            # 2026-08-16, AI 思维导图 + 核心概念 已生成
    understanding: done  # 2026-08-16, 你的话已落盘
  ch02:
    map: not_started
    understanding: not_started
```

Two fields per chapter: `map` and `understanding`. AI updates it at the end of the
capture loop; session start reads it to reconstruct progress. Home.md's book card
reads `understanding` from this tracker for its `落盘 X/Y` badge and chapter dots.

> **Legacy:** older books may still carry `feynman`/`write` fields — treat them as
> read-only history; don't write them going forward.

---

## Finishing a book (lightweight)

*Triggered when user says "我读完了这本书" / "{Book} 读完了"*

No AI-driven interview. Just:

1. Show the progress table (which chapters have `understanding: done`, which don't).
   Inform, don't block.
2. Update `meta.md`: `status: finished`, `finished: {date}`.
3. The meta.md reflection sections (`## 跨章回顾` / `## 全局连接` / `## 读后感`) stay
   for the human to fill **if they want** — AI may ask a prompting question, never
   fills them.

**Does NOT**: generate a book summary, extract zettel, or write synthesis.

---

## New book onboarding

*Triggered when user says "我要开始读 XXX", or explicitly via `/book-init <书名>`*

Run via **`/book-init`** (see `.agents/skills/book-init/SKILL.md` for the full
step-by-step). In brief:

```
1. Confirm: title, author, archetype, reading channel (WeRead / iBooks / EPUB / mix).
2. If EPUB/PDF available: locate it under ~/Library/ebooks/ (fuzzy match; ask when
   multiple candidates), run book_init.py to generate the chapter skeleton +
   meta.md/MOC.md/chapters//notes/ + understanding.md placeholder.
3. Fill meta.md fields book_init.py can't infer (archetype, capture sources).
4. Build the full-text cache (extract_fulltext.py) so the chapter map can be
   generated — standard step for EPUB books.
5. Books Index.md auto-discovers via Dataview; no manual edit.
```

**Retrofitting older books**: missing `epub_path`/`pdf_path` can be backfilled via
`/book-init` "帮我补一下 epub_path" — confirm before writing, never guess between
editions/translations.

---

## Anti-slop / copyright (same act, two reasons)

- Never reproduce the book's figures or large passages. The AI map is a structural
  归纳 in its own words + a concept list; the human's block is the human's own words.
- 1-2 short quotes at most, to anchor or verify a point — never long passages.
- This is both copyright-safe and the thing that keeps the record genuinely yours:
  **a note you can't put in your own words is a note you haven't understood yet.**

---

## Variable investment

Most books stay in WeRead/iBooks only — read, enjoyed, a few highlights, done. A book
gets upgraded to the production layer (chapter maps + understanding) **only when it
proves itself worth it during capture.** Don't pre-decide a book deserves it.

---

## Book archetypes

Archetype is a light tag in `meta.md` (`technical-reference` / `cognitive-mental-model`).
It no longer drives a question style (the Feynman flow is retired). It mainly signals
granularity and whether a book leans toward a private reflection style:

- **technical-reference** (e.g. DDIA, Learning DDD, Hard Parts) — chapter by chapter;
  the map + understanding record is the output.
- **cognitive / mental-model** (e.g. Thinking, Fast and Slow) — per concept rather than
  strictly per chapter; the "我的理解" block leans toward "where does this show up in a
  real decision of mine?" The default output is still the understanding record, not a
  public article.

---

## Per-book folder structure

```
Learning/Books/{BookTitle}/
├── MOC.md            ← pure index: links to all content
├── meta.md           ← archetype, capture sources, progress tracker, reading meta
├── chapters/         ← book_init.py skeleton (read-only)
├── notes/            ← on-demand working notes (sources, research)
├── understanding.md  ← per-chapter record: AI map + your understanding (terminal output)
└── .fulltext_cache/  ← full-text cache (machine-managed, gitignored)
```

---

## This file is alive

This workflow is being rebuilt around low-friction capture, with Learning DDD as the
first iteration. Expect it to keep changing as the loop is used and refined.

---
name: book-write
description: >-
  Produce a WRITING SKELETON (骨架 + 重点) for a book's 读后文章 — chapter-level or
  book-level — into {BookTitle}/article.md, so the human can write the article by
  following it. AI builds the skeleton; the human writes the prose. Use when the user
  finished a chapter/book and wants an outline to write a post from, or says /book-write.
disable-model-invocation: true
---

<!-- module: book-learning -->
> [!GUARD] Read `system/modules/book-learning/module.md`. If `enabled: false` → reply "⛔ Module **book-learning** is disabled. Enable it via `/module-toggle book-learning`." and STOP. Do NOT proceed.

Produce a writing skeleton: $ARGUMENTS

This command is the **publication layer** of the reading system (the third layer, after
capture and production). Its job is to distill a **writing skeleton** — the article's
骨架 + 重点 — that the human then writes the actual 读后文章 from, by hand. Read
`Learning/Books/CLAUDE.md` → "Publication layer — 写作骨架 (article.md)" first; that file
is the single source of truth for the rules and format. Do **not** duplicate them here.

## The red line still holds

**AI builds the skeleton and marks the key points. The human writes the prose.**

- AI **may** generate section headings, per-section bullet points (要点), and pull the
  reader's own highlights/理解 forward as *seeds*.
- AI **may not** write the article's prose, the reader's takeaways, or fabricate a
  personal experience. Sections that draw on "我的理解" use the reader's own words
  (verbatim seed); if a chapter has no 我的理解 yet, leave that seed empty and say so —
  never fill it with book text dressed up as a reaction.
- Anti-slop / copyright: same rules as the map — no long verbatim passages; 1–2 short
  quotes at most.

## Step 1 — Pick the book + granularity

Parse `$ARGUMENTS` for a book name and (optionally) a chapter number / "整本".

- Scan `Learning/Books/*/meta.md`. Fuzzy-match `$ARGUMENTS` to a book; if exactly one
  book matches (or only one has `status: reading`/`finished`), use it. Otherwise use
  `AskQuestion` to pick (build options from the scan — never hardcode titles).
- **Granularity**:
  - `$ARGUMENTS` names a chapter (e.g. "DDD 第 2 章") → **chapter-level** skeleton for that chapter.
  - `$ARGUMENTS` says "整本" / "全书" / the book is `status: finished` → **book-level** skeleton.
  - Ambiguous → ask: 章级（这章）还是 书级（跨章汇总）？

## Step 2 — Load the source (understanding.md, not full text)

The writing skeleton is distilled from the **production layer**, not re-parsed from the
book — this reuses the work already on disk and keeps the red line:

1. Read `{BookTitle}/meta.md` → `archetype`, progress tracker, and the reader's own
   `## 这本书要解决什么问题？` / `## 作者的核心主张` / `## 我读这本书想得到什么？` /
   (book-level) `## 跨章回顾` / `## 全局连接` / `## 读后感` if filled.
2. Read `{BookTitle}/understanding.md` → the target chapter(s)' `结构地图与核心概念（AI）`
   block **and** the `我的理解（你的话，原文）` block.

**Precondition guard**:
- Chapter-level: if that chapter has no `## Ch{N}.` block in understanding.md yet, tell
  the user to run `/book-read` (落盘) for it first — there's nothing to distill. Stop.
- Book-level: it works even if some chapters lack 我的理解 — but list which chapters are
  still empty so the article outline flags where the reader's own voice is missing.

## Step 3 — Generate the skeleton (AI, into article.md)

Write to `{BookTitle}/article.md` (create it if missing, with the header block — see the
format in `Learning/Books/CLAUDE.md`). Never overwrite the reader's own prose in
article.md; append/update only the AI skeleton blocks.

### Chapter-level skeleton
Append a `## Ch{N}. {title}` section under `## 章级骨架（写作素材）` containing:
- **骨架** — 3–6 candidate section headings you could build a post-section around, drawn
  from the chapter's mind-map branches (writing-oriented, not a mind map).
- **重点** — the chapter's must-include points (concept + one-line why-it-matters).
- **可用 seed** — the reader's highlights (`📌`) and 我的理解 for this chapter, verbatim,
  under `> 📥` — the raw material the reader writes the section from. Empty if none.

### Book-level skeleton
Generate/refresh the `## 文章大纲（书级）` block at the top of article.md:
- **切入角度** — 1–2 candidate angles for the whole post (a question the book answers, a
  before/after in the reader's own thinking) — offered as options, the reader picks.
- **分节大纲** — the article's section headings in order, each with: 1-line 要点 + which
  chapter(s)' skeleton/seed to draw from. For `technical-reference` books, bias toward a
  **reference-friendly** shape (问题 → 可复用模型/概念 → 适用条件与取舍 → 我会怎么用 →
  存疑/不同意). For `cognitive-mental-model` books, bias toward 决策/场景 shape.
- **待补** — chapters with no 我的理解 yet (the reader's voice is missing there).

Keep it tight and scannable — this is scaffolding to write against, not the article.

## Step 4 — Hand off

Report what got written and point the reader at the next move:

```
✅ {Book} 写作骨架已更新 → Learning/Books/{Book}/article.md
   {章级 Ch{N} · N 个候选小节 / 书级大纲 · N 节}
   待补理解: {chapters missing 我的理解, or "—"}

照骨架写正文就行。正文你自己写，我不代笔——需要我核对事实或补 source 再叫我。
```

Do **not** write the article body. If the user later asks you to "verify" or "find
sources" for a claim, that's the research step in `Learning/Books/CLAUDE.md`.

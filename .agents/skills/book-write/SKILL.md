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
  - `$ARGUMENTS` names a chapter (e.g. "DDD 第 2 章") → chapter skeleton for **that** chapter.
  - `$ARGUMENTS` names no chapter (e.g. just "DDD") → **all read chapters**: add/refresh a
    per-chapter 骨架 for every chapter that has a `## Ch{N}.` block in understanding.md but
    no 骨架 in article.md yet (batch — this is the "每章都有骨架" default).
  - `$ARGUMENTS` says "全书总结" / "整本" / the book is `status: finished` → **book-level**
    全书总结 skeleton (still safe to run alongside the per-chapter ones).
  - Ambiguous → ask: 补某一章 / 补所有已读章 / 写全书总结？

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
format in `Learning/Books/CLAUDE.md`). The file has two writing surfaces: a **per-chapter
summary** for every chapter (each = an AI 骨架 + the reader's 我的总结) and a single
**全书总结** at the end. Never overwrite the reader's own prose; write/refresh only the AI
`**骨架（AI）**` blocks and add empty `**我的总结（你写）**` slots.

### Chapter-level (读完一章 → 每章一个骨架 + 你写这章总结)
Under `## 分章总结`, add/refresh a `### Ch{N}. {title}` section containing:
- **骨架（AI）— 这章在讲什么** — a tight 3–6 bullet outline of the chapter's spine
  (main branches → key sub-points), distilled from that chapter's `结构地图与核心概念`
  in understanding.md. Mark bullets the reader highlighted with `📌`. This is the "so what
  is this chapter about" scaffold, not the full mind map.
- **我的总结（你写）** — the reader's own chapter summary. Pre-seed with their `💭`
  annotations / `我的理解` for this chapter, verbatim, under `> 📥` if any; otherwise leave
  an empty placeholder. Never write this summary for them.

Refresh rule: if a `### Ch{N}.` section already exists, update only its `**骨架（AI）**`
block; never touch the reader's `**我的总结（你写）**` prose.

### Book-level (读完整本 → 全书总结)
Fill the `## 全书总结` block at the end of article.md:
- **骨架（AI）— 全书脉络** — how the chapters connect into one arc (the book's spine across
  chapters), a few bullets. For `technical-reference` books, also offer a reference-friendly
  frame (问题 → 可复用模型/概念 → 适用条件与取舍 → 我会怎么用 → 存疑/不同意). For
  `cognitive-mental-model` books, offer a 决策/场景 frame.
- **待补** — chapters whose `我的总结` is still empty (the reader's voice is missing there).
- **我的总结（你写）** — empty slot for the reader's whole-book summary. Never write it.

Keep every 骨架 tight and scannable — scaffolding to write against, not the summary itself.

## Step 4 — Hand off

Report what got written and point the reader at the next move:

```
✅ {Book} 骨架已更新 → Learning/Books/{Book}/article.md
   分章骨架: Ch{N}…（新增/刷新 N 章） · 全书总结: {骨架已生成 / —}
   待写总结: {chapters whose 我的总结 is still empty, or "—"}

每章照骨架写「我的总结」，读完整本再写全书总结。总结你自己写，我不代笔——
要我核对事实或补 source 再叫我。
```

Do **not** write the reader's summaries. If the user later asks you to "verify" or "find
sources" for a claim, that's the research step in `Learning/Books/CLAUDE.md`.

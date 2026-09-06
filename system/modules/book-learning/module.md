---
module: book-learning
label: "Book Learning 读书系统"
type: knowledge
status: active
enabled: true
created: 2026-07-15
updated: 2026-09-07
depends_on: []
requires:
  cli: [claude]
  python: ">=3.10"
  pip: [ebooklib, beautifulsoup4, pdfplumber]
  plugins: [dataview]
commands: [book-init, read, write]
templates: []
scripts: [Learning/Books/book_init.py, Learning/Books/extract_fulltext.py, Learning/Books/test_extract_fulltext.py]
hooks: []
folders: [Learning/Books/]
config_files:
  - .claude/skills/book-init/SKILL.md
  - .claude/skills/book-read/SKILL.md
  - .claude/skills/book-write/SKILL.md
  - Learning/Books/CLAUDE.md
  - Learning/Books/book_init.py
  - Learning/Books/extract_fulltext.py
  - Learning/Books/test_extract_fulltext.py
  - Learning/Books/.bookrc.example
tags: [system/module]
---

## Overview

深度读书笔记系统，以**高效落盘**为核心。三层：捕获层（WeRead + Apple Books/iBooks 自动同步划线）+ 生产层（每章一条 `understanding.md` 记录：AI 生成思维导图+核心概念 → 人补自己的理解 → AI 一遍核对）+ 发表层（读完章/书时 AI 从生产层提炼**写作骨架** → `article.md`，人照骨架写读后文章；AI 搭骨架，人写正文）。每本书一个独立文件夹。详细工作流见 `Learning/Books/CLAUDE.md`（本文件不重复，只做治理层描述）。

## 架构

- **`{BookTitle}/meta.md`**: frontmatter 驱动 — archetype、reading_channel、progress tracker（每章 `map`/`understanding` 两字段），以及（EPUB/PDF 书）`epub_path`/`pdf_path`（按来源格式二选一）指向 `~/Library/ebooks/` 下的实体文件；`cover`（`book_init.py` 自动从 EPUB 提取内嵌封面到 `<book>/cover.{ext}`）；`weread_source` / `ibooks_source`（二选一或都有；WeRead 有按章划线+阅读进度，iBooks 是单扁平文件、章节归属不可靠、无进度字段）
- **`{BookTitle}/understanding.md`**: **生产层产物**。按章记录，每章两块——`结构地图与核心概念（AI）` + `我的理解（你的话，原文转录）`。发表层写作骨架的输入源
- **`{BookTitle}/article.md`**（可选，按需）: **发表层产物**。AI 从 `understanding.md` 提炼的写作骨架（书级文章大纲 + 章级骨架/重点/seed）+ 人在其下自己写的读后文章正文。AI 只写标注的骨架块，正文人写，见 `Learning/Books/CLAUDE.md` → "Publication layer — 写作骨架"
- **`{BookTitle}/.fulltext_cache/`**: 全书正文文本缓存，`extract_fulltext.py` 生成。**标准输入步骤**（不再是 opt-in）——章节思维导图基于原文生成。仅 EPUB。详见 `Learning/Books/CLAUDE.md` → "Full-text cache"
- **`{BookTitle}/MOC.md`**: 纯索引，链接到 meta + chapters + notes + understanding
- **`{BookTitle}/chapters/`**: `book_init.py` 生成的章节骨架，只读参考
- **`{BookTitle}/notes/`**: 按需的 sources/research 记录
- **`{BookTitle}/feynman/`**（legacy）: 旧版费曼测试日志，只读存档，新流程不再写入
- **`_archive/`**: 旧版目录结构迁移前的存档（如 `DDIA-old-00_meta.md`）

### Ebook 存储

实体 epub/pdf 文件不在 vault 内，存放在 `~/Library/ebooks/`（从 S3 bucket `obsidian-ebook-library-391824190072` 经 launchd 同步，见 `.bookrc.example`）。`meta.md` 的 `epub_path`（`.epub` 来源）或 `pdf_path`（`.pdf` 来源）字段记录解析后的绝对路径，把笔记和原书文件关联起来。

### 数据流

- **新书 onboarding**: `/book-init <书名>` → 确认 archetype/channel → 在 `~/Library/ebooks/` 模糊匹配 epub/pdf → 跑 `book_init.py` 生成骨架（自动写入 `epub_path`/`pdf_path`）→ 人工补 archetype → 建全文缓存 `extract_fulltext.py`
- **读书循环（落盘）**: 捕获（WeRead/iBooks 划线）→ AI 生成本章思维导图+核心概念（基于全文缓存）→ 人补自己的理解 → AI 一遍核对 → 两块并存落盘 `understanding.md`，见 `Learning/Books/CLAUDE.md` "The capture loop"
- **写读后（发表层）**: `/book-write <书名 [章/整本]>` → 从 `understanding.md` 提炼写作骨架（章级：骨架+重点+seed；书级：文章大纲）→ 写入 `article.md` → 人照骨架写正文。读完整本时 `/book-read` 结束流程也会**可选**提示生成书级骨架。见 `Learning/Books/CLAUDE.md` → "Publication layer — 写作骨架"
- **补全遗留书**: `/book-init` 的 Retrofit 流程 → 扫描缺 `epub_path`/`pdf_path` 的 `meta.md` → 模糊匹配补全（多候选时必须询问，不猜）

## 已知遗留问题

- 部分早期书（如 `Fundamentals of Software Architecture`）仍是旧版扁平结构（`00_meta.md`/`00_map.md`），尚未迁移到 `meta.md`/`MOC.md` 新规范。迁移时注意先核对新旧内容一致再删除旧目录（`Designing Data-Intensive Applications` 已完成此迁移并清理，2026-07-15）。

## Quick Start

1. **首次安装** → `cd Learning/Books && python3 -m venv .venv && .venv/bin/pip install ebooklib beautifulsoup4 pdfplumber`（仅在 `.venv/` 不存在时需要，`book_init.py` 依赖这三个包）
2. `/book-init "书名"` — 新书 onboarding（含 epub 定位 + book_init.py + 元数据确认）
3. `/book-read` — 恢复读书 → 选书选章 → 落盘理解到 `understanding.md`
4. `/book-write "书名 [第 N 章 / 整本]"` — 从 `understanding.md` 提炼写作骨架到 `article.md`，照骨架写读后文章
5. `/book-init` 说「帮我补一下 epub_path」— 扫描并补全遗留书的 epub_path/pdf_path

---
module: book-learning
label: "Book Learning 读书系统"
type: knowledge
status: active
enabled: true
created: 2026-07-15
updated: 2026-08-07
depends_on: []
requires:
  cli: [claude]
  python: ">=3.10"
  pip: [ebooklib, beautifulsoup4, pdfplumber]
  plugins: [dataview]
commands: [book-init, read]
templates: []
scripts: [Learning/Books/book_init.py, Learning/Books/extract_fulltext.py, Learning/Books/test_extract_fulltext.py]
hooks: []
folders: [Learning/Books/]
config_files:
  - .claude/commands/book/book-init.md
  - .claude/commands/book/read.md
  - .claude/skills/book-init/SKILL.md
  - .claude/skills/book-read/SKILL.md
  - Learning/Books/CLAUDE.md
  - Learning/Books/book_init.py
  - Learning/Books/extract_fulltext.py
  - Learning/Books/test_extract_fulltext.py
  - Learning/Books/.bookrc.example
tags: [system/module]
---

## Overview

深度读书笔记系统。捕获层（WeRead 自动同步划线）+ 生产层（Feynman 费曼测试 → 人写 → AI review），每本书一个独立文件夹。详细工作流见 `Learning/Books/CLAUDE.md`（本文件不重复，只做治理层描述）。

## 架构

- **`{BookTitle}/meta.md`**: frontmatter 驱动 — archetype、output_target、reading_channel、progress tracker，以及（EPUB/PDF 书）`epub_path`/`pdf_path`（按来源格式二选一）指向 `~/Library/ebooks/` 下的实体文件
- **`{BookTitle}/MOC.md`**: 纯索引，链接到 meta + chapters + notes + feynman
- **`{BookTitle}/chapters/`**: `book_init.py` 生成的章节骨架，只读参考
- **`{BookTitle}/notes/`**: 按需的 sources/research 记录
- **`{BookTitle}/feynman/`**: 费曼测试结果日志（✅/⚠️，按日期追加）
- **`{BookTitle}/.fulltext_cache/`**（可选，per-book opt-in）: 全书正文文本缓存，`extract_fulltext.py` 生成，仅用于自由问答/话题讨论，不影响费曼检查的"先讲后审"顺序。详见 `Learning/Books/CLAUDE.md` → "Full-text cache"
- **`_archive/`**: 旧版目录结构迁移前的存档（如 `DDIA-old-00_meta.md`）

### Ebook 存储

实体 epub/pdf 文件不在 vault 内，存放在 `~/Library/ebooks/`（从 S3 bucket `obsidian-ebook-library-391824190072` 经 launchd 同步，见 `.bookrc.example`）。`meta.md` 的 `epub_path`（`.epub` 来源）或 `pdf_path`（`.pdf` 来源）字段记录解析后的绝对路径，把笔记和原书文件关联起来。

### 数据流

- **新书 onboarding**: `/book/book-init <书名>` → 确认 archetype/channel → 在 `~/Library/ebooks/` 模糊匹配 epub/pdf → 跑 `book_init.py` 生成骨架（按来源格式自动写入 `epub_path`/`pdf_path`）→ 人工补 archetype/output_target
- **读书循环**: Naked read（WeRead/EPUB）→ Feynman sparring → 人写 + AI review，见 `Learning/Books/CLAUDE.md` "Per-unit workflow"
- **补全遗留书**: `/book/book-init` 的 Retrofit 流程 → 扫描缺 `epub_path`/`pdf_path` 的 `meta.md` → 模糊匹配补全（多候选时必须询问，不猜）

## 已知遗留问题

- 部分早期书（如 `Fundamentals of Software Architecture`）仍是旧版扁平结构（`00_meta.md`/`00_map.md`），尚未迁移到 `meta.md`/`MOC.md` 新规范。迁移时注意先核对新旧内容一致再删除旧目录（`Designing Data-Intensive Applications` 已完成此迁移并清理，2026-07-15）。

## Quick Start

1. **首次安装** → `cd Learning/Books && python3 -m venv .venv && .venv/bin/pip install ebooklib beautifulsoup4 pdfplumber`（仅在 `.venv/` 不存在时需要，`book_init.py` 依赖这三个包）
2. `/book/book-init "书名"` — 新书 onboarding（含 epub 定位 + book_init.py + 元数据确认）
3. `/book/book-init` 说「帮我补一下 epub_path」— 扫描并补全遗留书的 epub_path/pdf_path

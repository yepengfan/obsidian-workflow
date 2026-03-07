# Obsidian Workflow

System files for my Obsidian knowledge management vault. Content (notes, highlights, attachments) is synced separately — this repo only tracks the **workflow infrastructure**.

## What's in here

```
.claude/
  commands/       # Claude Code slash commands (/backup, /daily, /research, etc.)
  scripts/        # Auto-sync hooks
  skills/         # Claude Code skills (Obsidian markdown, Bases, Canvas, etc.)
  settings.json   # Hook configuration

Books/
  book_init.py    # EPUB/PDF parser → Obsidian note generator
  CLAUDE.md       # Book learning system instructions
  Books Index.md  # Dataview-powered book directory
  .bookrc.example # Config template for local paths

Templates/        # Work daily notes and project page templates
CLAUDE.md         # Vault-level Claude Code instructions
Home.md           # Obsidian dashboard with Dataview queries
```

## Architecture

```mermaid
graph LR
    subgraph Sources
        EPUB[EPUB/PDF]
        WR[WeRead Highlights]
    end

    subgraph GitHub["GitHub (this repo)"]
        SYS[System Files<br/>scripts, templates,<br/>CLAUDE.md, commands]
    end

    subgraph Vault["Obsidian Vault"]
        HOME[Home Dashboard]
        IDX[Books Index]
        BOOKS[Book Notes]
        WORK[Work Notes]
        OTHER[Thoughts, Articles, ...]
    end

    subgraph Sync
        IC[iCloud / S3]
    end

    EPUB -->|book_init.py| BOOKS
    WR -->|auto-sync plugin| Vault
    SYS -->|git clone| Vault
    Vault <-->|content sync| IC
```

## Book Learning System

```mermaid
graph TD
    INIT["<b>INIT</b><br/>初始化 书名"]
    INIT -->|book_init.py| GEN[Generate Structure]
    GEN --> META[00_meta.md<br/>Reading goals]
    GEN --> MAP[00_map.md<br/>Chapter map +<br/>Concept network]
    GEN --> CH[chapters/Ch01..N<br/>Feynman prompts +<br/>Pre-generated flashcards]
    GEN -->|auto-detect| WRLINK[WeRead links<br/>in each chapter]

    READ["<b>READ</b><br/>Read chapter on WeRead"]
    READ --> FILL[Fill 核心概念 +<br/>和已知事物的连接]

    FEYNMAN["<b>FEYNMAN</b><br/>帮我费曼测试第 X 章"]
    FILL --> FEYNMAN
    FEYNMAN -->|Claude interrogates| CARDS[Generate flashcards]

    REVIEW["<b>REVIEW</b><br/>review 第 X 部分"]
    CARDS --> REVIEW
    REVIEW --> SUMMARY[Part summary +<br/>Cross-chapter connections]

    FINAL["<b>FINAL</b><br/>我读完了这本书"]
    SUMMARY --> FINAL
    FINAL --> SYNTH[Book synthesis +<br/>Gap check]

    SR["<b>SPACED REVIEW</b><br/>Obsidian SR plugin"]
    CARDS -.->|#flashcards/BookName| SR
    SR -.->|interval repetition| SR

    style INIT fill:#4a9eff,color:#fff
    style FEYNMAN fill:#ff6b6b,color:#fff
    style REVIEW fill:#ffa94d,color:#fff
    style FINAL fill:#51cf66,color:#fff
    style SR fill:#be4bdb,color:#fff
```

A structured reading workflow: **scaffold first → directed reading → active construction → spaced review**.

```
python3 Books/book_init.py --file "path/to/book.epub" --output "path/to/vault/Books"
```

Generates per-book Obsidian notes:
- `00_meta.md` — reading goals and final evaluation
- `00_map.md` — chapter map + cross-chapter concept network
- `chapters/Ch01_*.md` — per-chapter notes with Feynman test prompts and flashcards

Features:
- EPUB and PDF support (CJK and English)
- Auto-links WeRead (微信读书) highlights to chapter notes
- Spaced repetition flashcards via [obsidian-spaced-repetition](https://github.com/st3v3nmw/obsidian-spaced-repetition)
- Interactive workflows: Feynman testing, Part Review, Final synthesis (via Claude Code)

## Setup

1. Clone into your Obsidian vault root
2. Copy `Books/.bookrc.example` to `.bookrc` in the vault root and edit paths
3. Install dependencies: `pip install ebooklib beautifulsoup4 pdfplumber`
4. Install Obsidian plugins: Dataview, Spaced Repetition

## Dependencies

- [Obsidian](https://obsidian.md) with Dataview plugin
- [Claude Code](https://claude.ai/claude-code) for interactive workflows
- Python 3 with `ebooklib`, `beautifulsoup4`, `pdfplumber`

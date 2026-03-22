# Obsidian Workflow

System files for my Obsidian knowledge management vault. Content (notes, highlights, attachments) is synced separately — this repo only tracks the **workflow infrastructure**.

## Philosophy

This system is built on two complementary frameworks: **Second Brain** and **Zettelkasten**.

**Second Brain** (Tiago Forte) treats external tools as an extension of your mind — offloading capture, organization, and retrieval so that cognitive load is reserved for thinking and creating, not remembering. The Inbox, templates, and automated sync pipelines in this vault reflect that principle: capture should be frictionless, and information should flow toward use.

**Zettelkasten** (Niklas Luhmann) is a method for building a personal knowledge network from atomic, self-contained notes written in your own words. Unlike a filing cabinet organized by topic, a Zettelkasten grows through links — ideas accumulate meaning by connecting to other ideas, not by sitting in folders. Each zettel here is one thought, linked forward and backward, gradually forming a web that surfaces unexpected connections.

The combination produces a two-layer system: a **capture layer** (Inbox) where nothing is precious and everything is temporary, and a **knowledge layer** (Zettelkasten) where only distilled, original insights live permanently. Claude Code bridges the two — automating the extraction and linking work that would otherwise create friction and keep raw notes from ever becoming permanent knowledge.

## What's in here

```
.claude/
  commands/       # Claude Code slash commands (/zettel, /retro, /daily, /research, etc.)
  scripts/        # Auto-sync hooks
  skills/         # Claude Code skills (Obsidian markdown, Bases, Canvas, etc.)
  settings.json   # Hook configuration

Books/
  book_init.py    # EPUB/PDF parser → Obsidian note generator
  CLAUDE.md       # Book learning system instructions
  Books Index.md  # Dataview-powered book directory + WeRead Library card view
  .bookrc.example # Config template for local paths

Inbox/            # Fleeting notes — quick capture, processed weekly
Zettelkasten/     # Permanent notes — one atomic idea per note, interlinked
Learning/         # Structured learning plans (folder name = plan code)
  AISA/           # e.g. AI Solutions Architect
    00_plan.md    # Goals, phases, timeline, completion criteria
    00_map.md     # Concept map + technology radar
    Weeks/        # Weekly logs (YYYY-WXX.md)
    Courses/      # Course notes
    Projects/     # Project notes
Feeds/            # Auto-generated content feeds
  AI-Daily/       # Daily AI news digest (中英文), generated on Obsidian startup
  GitHub-Trending/ # Daily GitHub trending repos digest (中英文)
scripts/
  ai-digest/      # Hybrid Python + Claude Code RSS digest pipeline
    digest/       # Core module (fetch → dedup → score → summarize → report)
    setup.sh      # One-command bootstrap (venv + deps)
  github-trending/ # GitHub trending repos pipeline (stdlib Python + Claude Haiku)
    fetch.py      # Two-query GitHub Search API fetcher + dedup
    enrich.py     # Single Haiku call: categorize, score, bilingual one-liners
    write_reports.py  # Obsidian markdown report assembler
    run.sh        # Idempotent orchestrator with 14-day archive rotation
Templates/        # Inbox, Zettel, Work Daily, Work Project, Learning Plan, Learning Week, Brownbag Session
CLAUDE.md         # Vault-level Claude Code instructions
Home.md           # Obsidian dashboard with Dataview queries
sortspec.md       # Custom file explorer sort order (Custom File Explorer Sorting plugin)
```

## Architecture

```mermaid
graph TD
    EPUB[EPUB/PDF] -->|book_init.py| Vault
    WR[WeRead] -->|auto-sync plugin| Vault
    SYS[GitHub repo<br/>templates, commands] -->|git clone| Vault
    DIGEST[scripts/ai-digest] -->|Shell Commands<br/>on startup| Vault
    GHTREND[scripts/github-trending] -->|Claude Code skill| Vault

    Vault["🗃️ Obsidian Vault<br/>Home · Books · Work<br/>Inbox · Zettelkasten · Feeds"]

    Vault <-->|Remotely Save| S3V[S3: vault-sync]
    EBOOKS[~/Library/ebooks] -->|launchd| S3E[S3: ebook-library]
    S3V --> BACKUP[NAS backup]
    S3E --> BACKUP
```

## Book Learning System

```mermaid
graph TD
    INIT["<b>INIT</b><br/>初始化 书名"]
    INIT -->|book_init.py| GEN[Generate Structure]

    subgraph scaffold [" "]
        direction LR
        META[00_meta.md<br/>Reading goals]
        MAP[00_map.md<br/>Concept network]
        CH[chapters/Ch01..N<br/>Feynman prompts]
    end
    GEN --> scaffold

    READ["<b>READ</b><br/>Read chapter on WeRead"]
    READ --> FILL[Fill 核心概念 +<br/>和已知事物的连接]

    FILL --> FEYNMAN["<b>FEYNMAN</b><br/>帮我费曼测试第 X 章"]
    FEYNMAN --> CARDS[Generate flashcards]
    FEYNMAN -->|extract insights| ZK[Zettelkasten]

    CARDS --> REVIEW["<b>REVIEW</b><br/>review 第 X 部分"]
    REVIEW --> SUMMARY[Part summary]

    SUMMARY --> FINAL["<b>FINAL</b><br/>我读完了这本书"]
    FINAL --> SYNTH[Book synthesis]
    FINAL -->|cross-chapter insights| ZK

    CARDS -.->|#flashcards| SR["<b>SPACED REVIEW</b><br/>Obsidian SR plugin"]
    SR -.->|interval repetition| SR

    style INIT fill:#4a9eff,color:#fff
    style FEYNMAN fill:#ff6b6b,color:#fff
    style REVIEW fill:#ffa94d,color:#fff
    style FINAL fill:#51cf66,color:#fff
    style SR fill:#be4bdb,color:#fff
    style ZK fill:#20c997,color:#fff
    style scaffold fill:none,stroke:#ddd,stroke-dasharray:5
```

A structured reading workflow: **scaffold first → directed reading → active construction → spaced review → permanent knowledge**.

## Knowledge Flow (Zettelkasten)

```mermaid
flowchart TD
    classDef cmd fill:#4a9eff,color:#fff,font-weight:bold
    classDef store fill:#20c997,color:#fff
    classDef inbox fill:#ffd43b,color:#000
    classDef source fill:#f8f9fa,color:#333,stroke:#ccc
    classDef plan fill:#e8d5ff,color:#5f3dc4,stroke:#5f3dc4
    classDef output fill:#ff922b,color:#fff

    subgraph capture ["Capture → Zettel"]
        THOUGHT["💡 Fleeting thought"]:::source
        THOUGHT --> BTN["Zettel capture"]:::cmd
        BTN --> INBOX["Inbox/"]:::inbox
        INBOX --> IR["/inbox-review"]:::cmd
        IR ~~~ BOOK["📚 Book / article"]:::source
        BOOK --> ZT["/zettel"]:::cmd
        ZT ~~~ WORK_EXP["💼 Work experience"]:::source
        WORK_EXP --> RT["/retro"]:::cmd
    end

    subgraph learn ["Learn → Share"]
        COURSE["📖 Structured learning"]:::source --> LI["/learning-init"]:::cmd
        LI --> PLAN["Learning/"]:::plan
        PLAN --> LL["/learning-log"]:::cmd
        LL --> LR["/learning-review"]:::cmd
        LR -.-> BB["/brownbag"]:::cmd
    end

    IR --> ZK["Zettelkasten/"]:::store
    ZT --> ZK
    RT --> ZK
    LR --> ZK
    PLAN -->|share| BB
    BB --> BBS["Brownbag Sessions/"]:::output
```

### Commands

All commands run inside Claude Code (type `/command-name` in the chat).

#### Knowledge Building

| Command | When to use |
|---------|------------|
| `/zettel <source>` | Extract permanent zettel from a book, article, or note |
| `/inbox-review` | Weekly — process all Inbox notes into zettel or archive |
| `/retro <source>` | Extract reusable lessons from work daily notes or project pages |

#### Research & Notes

| Command | When to use |
|---------|------------|
| `/research <topic>` | Web research → structured note saved to `Thoughts/` |
| `/summarize <note>` | Summarize a note or folder into key points |
| `/backlink [note]` | Scan a note and add `[[wikilinks]]` to referenced concepts |

#### Work

| Command | When to use |
|---------|------------|
| `/daily` | Create today's personal daily note in `Thoughts/` (separate from work daily notes in `Work/2026/`) |
| `/meeting <title>` | Create a meeting note |
| `/decision-log <decision>` | Record a decision with context and rationale |
| `/project <name>` | Create a new project page in `Work/Projects/` |
| `/brownbag <topic>` | Create a new brownbag session plan in `Work/Brownbag Sessions/` (auto-assigns BB-N id) |

#### Learning

| Command | When to use |
|---------|------------|
| `/learning-init <plan>` | Create a new learning plan — assigns a short code (e.g. `AISA`) |
| `/learning-log [code\|plan]` | Create or open this week's learning log — accepts code shorthand |
| `/learning-review [code\|plan] [week]` | Review a week's log — produce zettel candidates and plan adjustments |
| `/project-retro [code\|folder]` | Technical project retro — decisions, pitfalls, reusable patterns |

#### Feeds

| Command | When to use |
|---------|------------|
| `ai-digest` | Generate today's AI daily digest from 92 RSS feeds |
| `github-trending` | Generate today's GitHub trending repos report |

#### Vault Maintenance

| Command | When to use |
|---------|------------|
| `/organize [folder]` | Review and sort notes in a folder |
| `/tag-audit` | Audit and clean up tags across the vault |
### Zettelkasten Workflow

**Capture (mobile):** Use the `+ Zettel` button on Home.md to create a timestamped note in `Inbox/` — no format required, just the thought.

**Inbox → Zettel flow** (run `/inbox-review` in Claude Code):
1. Each inbox note is shown one at a time
2. Choose: **convert to zettel** / **archive** / **skip**
3. Converted notes become permanent zettel in `Zettelkasten/`
4. Processed notes are archived to `Inbox/archive/YYYY-MM/` (never deleted)
5. Skipped notes remain in `Inbox/` for the next review

**Zettel status lifecycle:**
- 🌱 `seedling` — newly created, 0–1 Related links
- 🌿 `growing` — 2+ Related links, idea connected to the network
- 🌳 `evergreen` — manually marked; deeply internalized, cross-domain connections

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

## AI Daily Digest

A self-contained pipeline in `scripts/ai-digest/` that generates a bilingual (中/EN) daily AI news digest:

```
92 RSS feeds (Karpathy curated)
  → async fetch + time-window filter
  → title dedup (Jaccard similarity)
  → Haiku batch scoring (relevance × quality × timeliness)
  → Sonnet bilingual summarization (zh + en in parallel)
  → Obsidian markdown reports → Feeds/AI-Daily/
  → CloudWatch cost metrics
```

- **Trigger**: Shell Commands plugin on Obsidian startup, or Home.md ▶ Generate button
- **Output**: `Feeds/AI-Daily/YYYY-MM-DD.md` (中文) + `YYYY-MM-DD-en.md` (English)
- **Cost**: ~$0.13/day (Haiku scoring + Sonnet summarization)
- **Time**: ~90s (zh/en parallelized)

## GitHub Trending

A lightweight pipeline in `scripts/github-trending/` that generates a bilingual (中/EN) daily GitHub trending repos digest:

```
GitHub Search API (2 queries: new hot + active popular)
  → merge + dedup by full_name
  → top 30 by stars
  → single Haiku call (categorize + score + bilingual one-liners)
  → rank by score, select top 15
  → Obsidian markdown reports → Feeds/GitHub-Trending/
```

- **Trigger**: Claude Code skill command (`github-trending`), or `bash scripts/github-trending/run.sh`
- **Output**: `Feeds/GitHub-Trending/YYYY-MM-DD.md` (中文) + `YYYY-MM-DD-en.md` (English)
- **Cost**: ~$0.06/day (single Haiku enrichment call)
- **Time**: ~30-60s
- **Dependencies**: stdlib only (no pip install needed), requires `claude` CLI on PATH

## Setup (new machine)

### Prerequisites

- [Obsidian](https://obsidian.md)
- [Claude Code](https://claude.ai/claude-code)
- Python 3.13+ with `pip install ebooklib beautifulsoup4 pdfplumber`
- AWS CLI (`brew install awscli`) — for vault sync and Bedrock access

### 1. AWS credentials

Configure the `obsidian-sync` IAM user (least-privilege access to S3 only):

```bash
aws configure --profile obsidian-sync
# Access Key ID and Secret Access Key are stored in password manager
# Region: ap-southeast-2
```

### 2. Vault sync (Remotely Save)

1. Open Obsidian → Settings → Community Plugins → Install **Remotely Save**
2. Configure S3 backend:
   - **Endpoint**: `s3.ap-southeast-2.amazonaws.com`
   - **Region**: `ap-southeast-2`
   - **Bucket**: `obsidian-vault-sync-391824190072`
   - **Access Key / Secret**: from `obsidian-sync` IAM user
3. Trigger first sync — this downloads the full vault

### 3. Ebook library

```bash
# Create local ebook directory
mkdir -p ~/Library/ebooks

# Download ebooks from S3
aws s3 sync s3://obsidian-ebook-library-391824190072 ~/Library/ebooks --profile obsidian-sync
```

### 4. Ebook auto-sync (launchd)

Create `~/Library/LaunchAgents/com.tedfan.ebook-s3-sync.plist` (replace `/Users/tedfan` with your home directory):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tedfan.ebook-s3-sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/aws</string>
        <string>s3</string>
        <string>sync</string>
        <string>/Users/tedfan/Library/ebooks</string>
        <string>s3://obsidian-ebook-library-391824190072</string>
        <string>--region</string>
        <string>ap-southeast-2</string>
        <string>--exclude</string>
        <string>.DS_Store</string>
        <string>--profile</string>
        <string>obsidian-sync</string>
    </array>
    <key>WatchPaths</key>
    <array>
        <string>/Users/tedfan/Library/ebooks</string>
    </array>
    <key>StandardOutPath</key>
    <string>/tmp/ebook-s3-sync.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ebook-s3-sync.log</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.tedfan.ebook-s3-sync.plist
```

Any changes to `~/Library/ebooks/` are automatically synced to S3.

### 5. Book system config

```bash
cp Books/.bookrc.example .bookrc
# Edit .bookrc:
#   books_dir = "~/Library/ebooks"
#   vault_dir = "~/Vaults/Workspace"
```

### 6. Obsidian plugins

Install via Community Plugins: Dataview, Spaced Repetition, Kanban, Calendar, Excalidraw, Tag Wrangler, Remotely Save, Custom File Explorer Sorting, Shell Commands

### 7. AI Daily Digest

The digest pipeline lives in `scripts/ai-digest/` and runs on Obsidian startup via the [Shell Commands](https://github.com/Taitava/obsidian-shellcommands) plugin.

#### 7a. Install the pipeline

```bash
cd scripts/ai-digest && bash setup.sh
```

This creates a `.venv` and installs dependencies (`boto3`, `aiohttp`, `trafilatura`).

#### 7b. Configure Shell Commands

1. Settings → Shell Commands → **New shell command**, paste:

   ```bash
   VAULT=~/Vaults/Workspace; [ -f "$VAULT/Feeds/AI-Daily/$(date +%Y-%m-%d).md" ] || { cd "$VAULT/scripts/ai-digest" && .venv/bin/python -m digest & }
   ```

   Logic: check if today's file exists → only run if missing → `&` backgrounds the process so Obsidian isn't blocked.

2. Set **Alias** to `AI Daily Digest`
3. Click the command → **Events** → enable **Obsidian starts**

Output: `Feeds/AI-Daily/YYYY-MM-DD.md` (中文) and `YYYY-MM-DD-en.md` (English) appear ~30 s after Obsidian launches.

### 8. GitHub Trending

The trending pipeline lives in `scripts/github-trending/` and uses only stdlib Python — no setup needed beyond having `claude` CLI on PATH.

Run manually or via the Claude Code skill command:

```bash
bash scripts/github-trending/run.sh
```

Optional: set `GITHUB_TOKEN` for higher API rate limits (30 req/min authenticated vs 10 req/min unauthenticated).

Output: `Feeds/GitHub-Trending/YYYY-MM-DD.md` (中文) and `YYYY-MM-DD-en.md` (English).

### 9. NAS backup (optional)

Synology NAS can pull from S3 as an offline backup via **Cloud Sync**:

1. Open **Package Center** → Install **Cloud Sync**
2. Create a new sync task:
   - **Cloud Provider**: Amazon S3
   - **Access Key / Secret Key**: from `obsidian-sync` IAM user
   - **Bucket**: select the bucket to back up
   - **Local path**: a folder on the NAS (e.g., `/volume1/Backup/obsidian-vault`)
   - **Sync direction**: Download only (NAS as read-only backup)
3. Repeat for the second bucket if desired

This gives you a 3-2-1 backup: local Mac + S3 + NAS.

## AWS resources

| Resource | Value |
|----------|-------|
| IAM user | `obsidian-sync` |
| Vault bucket | `obsidian-vault-sync-391824190072` |
| Ebook bucket | `obsidian-ebook-library-391824190072` |
| Region | `ap-southeast-2` (Sydney) |

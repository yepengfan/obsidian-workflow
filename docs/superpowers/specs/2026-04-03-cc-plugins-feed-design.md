# Claude Code Plugins Feed — Design Spec

**Date:** 2026-04-03
**Status:** Draft
**Author:** Claude (brainstorming session with Ted)

## Overview

A new weekly feed that discovers Claude Code plugins (packages installed to `~/.claude/plugins/`) via GitHub Search + npm Registry, enriches them with Claude Haiku scoring, and generates bilingual Obsidian notes. Tracks both **new plugin discovery** and **version updates** to already-known plugins.

**Scope:** Top-level Claude Code plugin packages — superpowers, oh-my-claudecode, gstack, etc. Not individual MCP servers, skills, or hooks.

**Goal:** Discovery of new plugins + tracking updates to installed/known ones.

**Cadence:** Weekly (manual via `/feeds/cc-plugins`).

## Architecture

```
GitHub Search API ──┐
                    ├──→ fetch.py ──→ enrich.py ──→ write_reports.py
npm Registry API ───┘       │            │               │
                            ▼            ▼               ▼
                      raw plugins    scored +        Obsidian notes
                       (JSON)      classified        (weekly .md)
                            │        (JSON)              │
                            ▼                            ▼
                       state.json              Feeds/CC-Plugins/
                    (track known plugins)     YYYY-WXX.md + -en.md
```

Pipeline follows the established feed pattern: `fetch.py` → `enrich.py` → `write_reports.py`, orchestrated by `run.sh` with module guard, pre-flight checks, logging, and cleanup.

### File Layout

```
scripts/cc-plugins/
├── fetch.py          # GitHub search + npm version lookup
├── enrich.py         # Claude Haiku: classify, score, summarize
├── write_reports.py  # Generate Obsidian weekly notes
├── prompts/
│   └── enrich.md     # Classification + scoring prompt (single Haiku call)
├── state.json        # Persistent plugin tracking
└── run.sh            # Pipeline orchestrator

Feeds/CC-Plugins/
├── 2026-W14.md       # Weekly report (Chinese)
├── 2026-W14-en.md    # Weekly report (English)
├── Dashboard.md      # Index of all weekly reports
└── archive/          # Reports >14 weeks old

system/modules/feeds-cc-plugins/module.md
.claude/commands/feeds/cc-plugins.md
```

## Data Sources

### GitHub Search (primary discovery)

Multiple queries to cast a wide net:

1. `topic:claude-code-plugin` — repos that self-tag
2. `"claude-code" in:name,description` — name/description matches
3. `"claude/plugins" OR ".claude/plugins" in:readme` — README mentions plugin install path
4. `"claude-code" plugin in:readme` — broader README matches

**Filters:**
- Only repos with ≥ 2 stars OR created within last 30 days (avoids abandoned forks)
- Per repo: name, description, stars, forks, last push date, topics, language, README (first 2000 chars)

**Auth:** Uses `GITHUB_TOKEN` environment variable (optional but recommended for rate limits). Same as github-trending feed.

### npm Registry (version tracking)

For each discovered GitHub repo, attempt to find corresponding npm package:

1. Check repo's `package.json` `name` field via GitHub raw content API
2. Fallback: search npm by repo name

For matched packages: latest version, publish date, weekly downloads.

No auth needed — npm registry API is public.

### Deduplication

- By GitHub repo URL (canonical identifier)
- Cross-check: same npm package found via different GitHub repos → merge

## Classification & Scoring

### Classification Gate

Claude Haiku reads the README excerpt + repo metadata and answers: "Is this actually a Claude Code plugin (a package that installs into `~/.claude/plugins/` and provides skills, agents, hooks, or workflows for Claude Code)?"

Repos that are Claude API wrappers, Anthropic SDK examples, or unrelated projects get `is_plugin: false` and are filtered out before scoring.

### Scoring Dimensions

Weighted 1–10 scale, aggregated into composite score:

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Usefulness | 30% | How practical for daily Claude Code workflow? Does it solve a real problem? |
| Maturity | 25% | Stars, downloads, docs quality, version stability, test coverage signals |
| Activity | 25% | Recent commits, release frequency, issue responsiveness, not abandoned |
| Relevance | 20% | Alignment with Ted's workflow — Obsidian, code analysis, productivity, knowledge mgmt |

### Categories

| Category | Emoji | Examples |
|----------|-------|---------|
| `productivity` | ⚡ | Workflow enhancement, task mgmt, automation |
| `code-quality` | 🔍 | Linting, testing, review, TDD tools |
| `integration` | 🔗 | MCP servers, API connectors, platform bridges |
| `knowledge` | 📚 | Documentation, learning, search, memory |
| `devops` | 🚀 | CI/CD, deployment, infrastructure |
| `other` | 📦 | Everything else |

### Enrichment Output Per Plugin

```json
{
  "repo_url": "https://github.com/anthropics/superpowers",
  "name": "superpowers",
  "is_plugin": true,
  "score": 9.2,
  "dimensions": {
    "usefulness": 9,
    "maturity": 10,
    "activity": 9,
    "relevance": 9
  },
  "category": "productivity",
  "summary_zh": "Claude Code 官方增强插件，提供 TDD、调试、计划等高级工作流技能",
  "summary_en": "Official Claude Code enhancement plugin with TDD, debugging, planning, and advanced workflow skills",
  "install_cmd": "claude plugin add superpowers",
  "tags": ["official", "tdd", "debugging", "planning", "skills"]
}
```

## State Management

### State File (`scripts/cc-plugins/state.json`)

```json
{
  "last_run": "2026-W14",
  "plugins": {
    "https://github.com/anthropics/superpowers": {
      "name": "superpowers",
      "npm_package": "claude-code-superpowers",
      "last_version": "5.0.7",
      "first_seen": "2026-W12",
      "last_checked": "2026-W14",
      "stars": 1250
    }
  }
}
```

### Classification Logic

- **New plugin:** repo URL not in `state.plugins` → tagged 🆕
- **Updated plugin:** `last_version` differs from current npm latest → tagged 📦 with `old → new` version display
- **No change:** known plugin, same version → omitted from report (only new/updated make the weekly cut)

State is updated at the end of `write_reports.py` after successful report generation (not during fetch — ensures atomic updates).

## Output Format

### Weekly Report (`Feeds/CC-Plugins/2026-W14.md`)

**Frontmatter:**
```yaml
---
date: 2026-04-03
week: "2026-W14"
tags: [cc-plugins, digest]
lang: zh
plugins_discovered: 12
plugins_new: 3
plugins_updated: 2
generator: claude-code
---
```

**Body:**
```markdown
# Claude Code Plugins · W14

> 本周扫描 12 个插件，发现 3 个新插件，2 个版本更新

## 🆕 新发现

> [!tip] 1️⃣ gstack ⭐ 9.2 · ⚡ productivity
> [GitHub](url) · [npm](url) · ⭐ 340 · 📥 1.2k/wk
> `claude plugin add gstack`
>
> Multi-model orchestration framework for Claude Code...

> [!tip] 2️⃣ claude-test ⭐ 7.8 · 🔍 code-quality
> [GitHub](url) · [npm](url) · ⭐ 89 · 📥 450/wk
> `claude plugin add claude-test`
>
> TDD workflow toolkit with snapshot testing...

## 📦 版本更新

> [!info] superpowers `5.0.7` → `5.1.0` · ⚡ productivity
> [GitHub](url) · [Changelog](url)
>
> New debugging skill, improved plan execution...

> [!info] oh-my-claudecode `2.3.1` → `2.4.0` · ⚡ productivity
> [GitHub](url) · [Changelog](url)
>
> Added ultraqa mode, team pipeline improvements...

## 📊 本周统计
- 扫描插件: 12
- 新发现: 3 (≥6分)
- 版本更新: 2
```

### English Version (`2026-W14-en.md`)

Same structure, English language, `lang: en` in frontmatter.

### Dashboard.md

Dataview query listing all weekly reports sorted by week descending. Shows week, new count, updated count per report.

### Archive

Reports older than 14 weeks moved to `archive/` subdirectory by `run.sh` cleanup step.

## Home.md Integration

CC Plugins gets its own **standalone section** on Home.md, separate from the daily Feeds tab group. Rationale: weekly cadence doesn't belong alongside daily feeds.

### Layout

```
┌─────────────────────────────────────────────┐
│  Feeds   [AI Digest | GitHub | Blogs | Pod] │  ← daily feeds (existing)
├─────────────────────────────────────────────┤
│  CC Plugins                        Weekly 📦 │  ← new standalone section
│                                              │
│  Week 14 · 3 new · 2 updated               │
│                                              │
│  🆕 New Discoveries                         │
│  ⭐ gstack (9.2) — Multi-model orchestr...  │
│  👍 claude-test (7.8) — TDD workflow...     │
│                                              │
│  📦 Version Updates                          │
│  superpowers 5.0.7 → 5.1.0 — New debug...  │
│  oh-my-claudecode 2.3.1 → 2.4.0 — ...      │
│                                              │
│  All reports → Dashboard                     │
└─────────────────────────────────────────────┘
```

### DataviewJS Behavior

- Finds the **latest** `Feeds/CC-Plugins/YYYY-WXX.md` by sorting (not by today's date)
- Reads frontmatter: `plugins_new`, `plugins_updated`, `week`
- Parses content sections: extracts 🆕 and 📦 entries
- Shows top 3–5 entries per subsection
- Score color coding: ≥ 8 accent color, ≥ 6 normal, < 6 muted
- "All reports →" link to `Feeds/CC-Plugins/Dashboard.md`

## Module Definition

### `system/modules/feeds-cc-plugins/module.md`

```yaml
---
name: feeds-cc-plugins
type: feed
enabled: true
version: 1.0.0
description: Weekly Claude Code plugin discovery and version tracking feed
updated: 2026-04-03
commands:
  - /feeds/cc-plugins
output: Feeds/CC-Plugins/
requires:
  cli: [claude, git, python3, curl]
  python: ">=3.13"
  pip: []
  plugins: [dataview]
  env:
    ANTHROPIC_API_KEY: "Required for Claude Haiku enrichment"
dependencies:
  - dashboard
---
```

### `.claude/commands/feeds/cc-plugins.md`

Standard feed command with:
1. Module guard (check `enabled: false` → STOP)
2. Run `bash scripts/cc-plugins/run.sh`
3. Report: files generated, plugins discovered/new/updated
4. Post-success: read latest report, display top new plugins and version updates

## Pipeline Details

### run.sh

Follows established conventions:

1. Environment setup (PATH, logging)
2. Module toggle guard (`system/modules/feeds-cc-plugins/module.md`)
3. Pre-flight checks (claude CLI, Python, GITHUB_TOKEN warning if missing)
4. Idempotency: check if report for current ISO week already exists → exit 2
5. Step 0: `python3 fetch.py` → raw plugins JSON (stdout)
6. Step 1: Pipe to `python3 enrich.py` → enriched JSON (stdout)
7. Step 2: `python3 write_reports.py` with enriched JSON + state.json → Obsidian notes
8. Archive cleanup (>14 weeks)
9. Exit codes: 0 = success, 1 = error, 2 = already exists

### fetch.py

- Input: none (fetches from GitHub + npm APIs)
- Uses stdlib only (`urllib.request`, `json`) — no pip dependencies
- GitHub Search: runs 4 queries, deduplicates by repo URL
- npm lookup: for each repo, tries to resolve npm package name
- Merges state.json to tag each plugin as `new`, `updated`, or `unchanged`
- Output: JSON array to stdout
- Exit code 2 if current week's report already exists

### enrich.py

- Input: JSON from fetch.py (stdin)
- Pipes plugin batch to `claude --model haiku` with `prompts/enrich.md`
- Single Haiku call for entire batch (cost control)
- Filters out `is_plugin: false` results
- Output: enriched JSON to stdout

### write_reports.py

- Input: enriched JSON (via env var pointing to temp file)
- Generates Chinese + English weekly reports
- Updates `state.json` with current versions
- Generates/refreshes `Dashboard.md`
- Creates `Feeds/CC-Plugins/` directory if needed

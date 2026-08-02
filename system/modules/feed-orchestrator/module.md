---
module: feed-orchestrator
label: "Feed Orchestrator"
type: feed
status: active
enabled: true
created: 2026-05-21
updated: 2026-08-03
depends_on: [feeds-ai-digest, feeds-github-trending, feeds-engineering-blogs, dashboard]
requires:
  python: ">=3.13"
  pip: [anthropic, aiohttp]
  cli: [agent]
  plugins: [dataview, obsidian-shellcommands]
  env:
    FEED_LLM_BACKEND: "(optional) cursor (default) or anthropic"
    CURSOR_API_KEY: "(optional) Cursor API key for headless runs; agent login also works"
    ANTHROPIC_API_KEY: "(required when FEED_LLM_BACKEND=anthropic) Anthropic API key for Haiku"
commands: []
templates: []
scripts:
  - scripts/feed-orchestrator/main.py
  - scripts/feed-orchestrator/tools.py
  - scripts/feed-orchestrator/feeds.py
  - scripts/feed-orchestrator/status.py
  - scripts/feed-orchestrator/load-env.sh
  - scripts/shared/llm_runner.py
  - scripts/shared/cursor_runner.py
hooks: []
folders: []
config_files:
  - .claude/skills/feeds-all/SKILL.md
  - .claude/commands/feeds/all.md
  - scripts/feed-orchestrator/requirements.txt
  - .obsidian/plugins/obsidian-shellcommands/data.json
tags: [system/module]
---

# Feed Orchestrator

## Overview
Python 编排器，一键生成全部 3 个 Daily Feed 管线。通过 Home.md「Daily Feeds ▶」按钮或 CLI 触发。

LLM 后端可切换（`FEED_LLM_BACKEND`）：
- **cursor**（默认）— Cursor CLI `agent -p`，走 Cursor subscription
- **anthropic** — Anthropic SDK Haiku，需 `ANTHROPIC_API_KEY`

依赖:
- [[system/modules/feeds-ai-digest/module|AI Daily Digest]]
- [[system/modules/feeds-github-trending/module|GitHub Trending]]
- [[system/modules/feeds-engineering-blogs/module|Engineering Blogs]]

## 架构

```
scripts/feed-orchestrator/
├── main.py              # 编排入口 — fetch → enrich → write → archive
├── feeds.py             # Feed 配置 + enrich 逻辑
├── status.py            # 状态文件（.feed-status.json）
├── load-env.sh          # Shell Commands 入口
└── .venv/

scripts/shared/
├── llm_runner.py        # FEED_LLM_BACKEND 切换层
└── cursor_runner.py     # Cursor CLI agent -p 封装
```

### 工作流程
```
Home.md [Daily Feeds ▶]  →  load-env.sh  →  main.py
  ↓
  1. check module enabled
  2. skip if report exists
  3. fetch.py（子进程）
  4. enrich（cursor 或 anthropic）
  5. write_reports.py（子进程）
  6. archive
  ↓
Feeds/.feed-status.json  ← Home.md 轮询
```

### LLM 后端

| 变量 | 默认 | 说明 |
|------|------|------|
| `FEED_LLM_BACKEND` | `cursor` | `cursor` 或 `anthropic` |
| `FEED_CURSOR_MODEL` | `composer-2.5` | Cursor 模型 |
| `FEED_CURSOR_MODEL_SCORE` | — | ai-digest 打分步骤 override |
| `FEED_CURSOR_MODEL_SUMMARIZE` | — | ai-digest 摘要步骤 override |
| `FEED_HAIKU_MODEL` | auto | anthropic 模式模型 override |

Cursor 模式下 ai-digest 合并为 3 次 LLM 调用（score all → summarize all → trend）。
Anthropic 模式保持 parallel batch（4/5 篇 per call）。

### 触发方式
| 方式 | 说明 |
|------|------|
| Home.md 按钮 | Daily Feeds ▶ |
| 命令面板 | Execute: Generate All Feeds |
| CLI | `bash scripts/feed-orchestrator/load-env.sh` |
| Cursor | `/feeds-all` or `/feeds/all` |

### 输出
- `Feeds/AI-Daily/YYYY-MM-DD.md` + `-en.md`
- `Feeds/GitHub-Trending/YYYY-MM-DD.md` + `-en.md`
- `Feeds/Engineering-Blogs/YYYY-MM-DD.md` + `-en.md`
- `Feeds/.feed-status.json`

## Quick Start

```bash
# Cursor backend（默认）
bash scripts/feed-orchestrator/load-env.sh

# Anthropic backend
FEED_LLM_BACKEND=anthropic bash scripts/feed-orchestrator/load-env.sh

# 单个 feed
bash scripts/feed-orchestrator/load-env.sh --feeds github-trending
```

---
🏠 [[Home]] · 📊 [[system/registry|Registry]] · 🚀 [[GETTING_STARTED|Getting Started]]

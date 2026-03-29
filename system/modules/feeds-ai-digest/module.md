---
module: feeds-ai-digest
label: "AI Daily Digest"
type: feed
status: active
enabled: true
created: 2026-03-29
updated: 2026-03-29
depends_on: [dashboard]
requires:
  cli: [claude]
  python: ">=3.13"
  pip: [aiohttp]
  plugins: [dataview, obsidian-shellcommands]
  env:
    ANTHROPIC_API_KEY: "Claude API key for Haiku scoring/summarization"
commands: [ai-digest]
templates: []
scripts:
  - scripts/ai-digest/run.sh
  - scripts/ai-digest/fetch.py
  - scripts/ai-digest/score.py
  - scripts/ai-digest/summarize.py
  - scripts/ai-digest/write_reports.py
hooks: []
folders: [Feeds/AI-Daily/]
config_files:
  - .claude/commands/feeds/ai-digest.md
  - scripts/ai-digest/prompts/score.md
  - scripts/ai-digest/prompts/summarize.md
  - .obsidian/plugins/obsidian-shellcommands/data.json
tags: [system/module]
---

# AI Daily Digest

## Overview
每日 AI 新闻摘要管线。从 92 个 Karpathy 精选 RSS 源获取文章，Claude Haiku 评分筛选 + 双语摘要，输出中英文 Obsidian 报告。

## 架构

```
scripts/ai-digest/
├── run.sh              # 编排器（4 阶段 + 归档）
├── fetch.py            # Phase 0: RSS 抓取 + 去重
├── score.py            # Phase 1: Haiku 评分筛选 top 15
├── summarize.py        # Phase 2: Haiku 双语摘要
├── write_reports.py    # Phase 3: 组装 Obsidian markdown
├── prompts/
│   ├── score.md        # 评分规则（相关性、质量、时效性）
│   └── summarize.md    # 摘要格式（中英文、阅读理由、趋势）
└── .venv/              # Python 虚拟环境
```

### Pipeline 流程
```
Phase 0: fetch.py (92 RSS feeds → JSON)
  ↓
Phase 1: score.py (Claude Haiku → top 15 articles)
  ↓
Phase 2: summarize.py (Claude Haiku → bilingual summaries)
  ↓
Phase 3: write_reports.py (→ Obsidian markdown)
  ↓
Phase 4: archive (>14 天报告归档)
```

### 触发方式
| 方式 | 说明 |
|------|------|
| Obsidian 启动 | Shell Commands 插件自动运行（后台，幂等） |
| 手动 | `/ai-digest` slash 命令 |

### 输出
- `Feeds/AI-Daily/YYYY-MM-DD.md` — 中文版
- `Feeds/AI-Daily/YYYY-MM-DD-en.md` — 英文版
- `Feeds/AI-Daily/Dashboard.md` — 索引

### 性能
~4-6 分钟，使用 Haiku 模型以控制成本和速度。

## Quick Start

1. **首次安装** → `cd scripts/ai-digest && python -m venv .venv && source .venv/bin/activate && pip install aiohttp`
2. **手动运行** → `/feeds/ai-digest` — 生成今日 AI 摘要（中英文双版）
3. **自动运行** → 配置 Shell Commands 插件，在 Obsidian 启动时执行 `bash scripts/ai-digest/run.sh`
4. **查看结果** → `Feeds/AI-Daily/` 目录下的 `YYYY-MM-DD.md`（中文）和 `YYYY-MM-DD-en.md`（英文）

**日常节奏**: 打开 Obsidian 自动生成 → Home.md Feeds 标签页查看

## 配置位置
| 组件 | 位置 |
|------|------|
| 编排器 | `scripts/ai-digest/run.sh` |
| 评分提示词 | `scripts/ai-digest/prompts/score.md` |
| 摘要提示词 | `scripts/ai-digest/prompts/summarize.md` |
| Shell Command | `.obsidian/plugins/obsidian-shellcommands/data.json` |
| 权限 | `.claude/settings.json` (Bash allow list) |
| slash 命令 | `.claude/commands/feeds/ai-digest.md` |

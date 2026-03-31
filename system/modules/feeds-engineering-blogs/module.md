---
module: feeds-engineering-blogs
label: "Engineering Blogs"
type: feed
status: active
enabled: true
created: 2026-03-31
updated: 2026-04-01
depends_on: [dashboard]
requires:
  cli: [claude]
  python: ">=3.13"
  plugins: [dataview]
  env:
    ANTHROPIC_API_KEY: "(required) Claude API key for Haiku enrichment"
commands: [engineering-blogs]
templates: []
scripts:
  - scripts/engineering-blogs/run.sh
  - scripts/engineering-blogs/fetch.py
  - scripts/engineering-blogs/enrich.py
  - scripts/engineering-blogs/write_reports.py
hooks: []
folders: [Feeds/Engineering-Blogs/]
config_files:
  - .claude/commands/feeds/engineering-blogs.md
  - scripts/engineering-blogs/prompts/enrich.md
tags: [system/module]
---

# Engineering Blogs

## Overview
每日大厂工程博客精选。RSS 抓取 AWS、Netflix、Cloudflare、Meta、OpenAI、DeepMind、GitHub 等工程博客，Claude Haiku 分类评分 + 双语摘要。

依赖: [[system/modules/dashboard/module|dashboard]]

## 架构

```
scripts/engineering-blogs/
├── run.sh              # 编排器（3 步骤 + 归档）
├── feeds.py            # RSS 订阅源定义
├── fetch.py            # Step 0: RSS 抓取 + 去重
├── enrich.py           # Step 1: Haiku 分类 + 评分 + 双语摘要
├── write_reports.py    # Step 2: 组装 Obsidian markdown
└── prompts/
    └── enrich.md       # 分类和评分提示词
```

### Pipeline 流程
```
Step 0: fetch.py (RSS feeds → JSON)
  ↓
Step 1: enrich.py (Claude Haiku → categorize + score + bilingual summaries)
  ↓
Step 2: write_reports.py (→ Obsidian markdown)
  ↓
Step 3: archive (>14 天报告归档)
```

### 触发方式
| 方式 | 说明 |
|------|------|
| 手动 | `/feeds/engineering-blogs` slash 命令 |

### 输出
- `Feeds/Engineering-Blogs/YYYY-MM-DD.md` — 中文版
- `Feeds/Engineering-Blogs/YYYY-MM-DD-en.md` — 英文版
- `Feeds/Engineering-Blogs/Dashboard.md` — 索引

### 博客来源
AWS Architecture · AWS ML · GitHub Engineering · OpenAI · Google DeepMind · Meta Engineering · Cloudflare · Stripe Engineering · Spotify Engineering · Dropbox Tech

### 分类
`ai-ml` · `infrastructure` · `data` · `security` · `devtools` · `platform` · `research` · `other`

### 评分标准
高标准评分：仅深度工程洞察、架构决策、事后分析、开源发布等获得高分（7+）。产品公告、营销内容、浅层教程评分低。

### 性能
~30-60 秒，单次 Haiku 调用。无需额外 Python 依赖（stdlib only）。

## Quick Start

1. **无需额外 pip 包** — Python 标准库即可（但 pipeline 需要 `ANTHROPIC_API_KEY`）
2. **手动运行** → `/feeds/engineering-blogs` — 生成今日工程博客精选（中英文双版）
3. **查看结果** → `Feeds/Engineering-Blogs/` 目录下的 `YYYY-MM-DD.md`（中文）和 `YYYY-MM-DD-en.md`（英文）

**日常节奏**: 需要时手动 `/feeds/engineering-blogs` → Home.md Feeds 标签页查看

## 配置位置
| 组件 | 位置 |
|------|------|
| 编排器 | `scripts/engineering-blogs/run.sh` |
| 博客列表 | `scripts/engineering-blogs/feeds.py` |
| 评分提示词 | `scripts/engineering-blogs/prompts/enrich.md` |
| 权限 | `.claude/settings.json` (Bash allow list) |
| slash 命令 | `.claude/commands/feeds/engineering-blogs.md` |

---
🏠 [[Home]] · 📊 [[system/registry|Registry]] · 🚀 [[GETTING_STARTED|Getting Started]]

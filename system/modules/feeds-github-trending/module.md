---
module: feeds-github-trending
label: "GitHub Trending"
type: feed
status: active
enabled: true
created: 2026-03-29
updated: 2026-03-29
depends_on: [dashboard]
commands: [github-trending]
templates: []
scripts:
  - scripts/github-trending/run.sh
  - scripts/github-trending/fetch.py
  - scripts/github-trending/enrich.py
  - scripts/github-trending/write_reports.py
hooks: []
folders: [Feeds/GitHub-Trending/]
config_files:
  - .claude/commands/feeds/github-trending.md
  - scripts/github-trending/prompts/enrich.md
tags: [system/module]
---

# GitHub Trending

## Overview
每日 GitHub 热门仓库摘要。通过 GitHub Search API 获取新仓库和活跃仓库，Claude Haiku 分类评分 + 双语一句话描述。

## 架构

```
scripts/github-trending/
├── run.sh              # 编排器（3 步骤 + 归档）
├── fetch.py            # Step 0: GitHub Search API 抓取 + 去重
├── enrich.py           # Step 1: Haiku 分类 + 评分 + 双语描述
├── write_reports.py    # Step 2: 组装 Obsidian markdown
└── prompts/
    └── enrich.md       # 分类和评分提示词
```

### Pipeline 流程
```
Step 0: fetch.py (GitHub Search API → JSON)
  ↓
Step 1: enrich.py (Claude Haiku → categorize + score + bilingual one-liners)
  ↓
Step 2: write_reports.py (→ Obsidian markdown)
  ↓
Step 3: archive (>14 天报告归档)
```

### 触发方式
| 方式 | 说明 |
|------|------|
| 手动 | `/github-trending` slash 命令 |

### 输出
- `Feeds/GitHub-Trending/YYYY-MM-DD.md` — 中文版
- `Feeds/GitHub-Trending/YYYY-MM-DD-en.md` — 英文版
- `Feeds/GitHub-Trending/Dashboard.md` — 索引

### 分类
`ai-ml` · `devtools` · `web` · `systems` · `data` · `security` · `other`

### 性能
~30-60 秒，单次 Haiku 调用。可选设置 `GITHUB_TOKEN` 提高 API 速率限制（30 req/min vs 10 req/min）。

## 配置位置
| 组件 | 位置 |
|------|------|
| 编排器 | `scripts/github-trending/run.sh` |
| 分类提示词 | `scripts/github-trending/prompts/enrich.md` |
| 权限 | `.claude/settings.json` (Bash allow list) |
| slash 命令 | `.claude/commands/github-trending.md` |

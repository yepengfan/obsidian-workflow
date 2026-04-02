---
module: feeds-cc-plugins
label: "CC Plugins"
type: feed
status: active
enabled: true
created: 2026-04-03
updated: 2026-04-03
depends_on: [dashboard]
requires:
  cli: [claude, python3, curl]
  python: ">=3.13"
  pip: []
  plugins: [dataview]
  env:
    ANTHROPIC_API_KEY: "(required) Claude API key for Haiku enrichment"
    GITHUB_TOKEN: "(optional) Higher API rate limit — 30 req/min vs 10 req/min"
commands: [cc-plugins]
templates: []
scripts:
  - scripts/cc-plugins/run.sh
  - scripts/cc-plugins/fetch.py
  - scripts/cc-plugins/enrich.py
  - scripts/cc-plugins/write_reports.py
hooks: []
folders: [Feeds/CC-Plugins/]
config_files:
  - .claude/commands/feeds/cc-plugins.md
  - scripts/cc-plugins/prompts/enrich.md
tags: [system/module]
---

# CC Plugins

## Overview
每周 Claude Code 插件发现与版本追踪。通过 GitHub Search API + npm Registry 发现新插件，Claude Haiku 分类评分 + 双语摘要。

依赖: [[system/modules/dashboard/module|dashboard]]

## 架构

```
scripts/cc-plugins/
├── run.sh              # 编排器（3 步骤 + 归档）
├── fetch.py            # Step 0: GitHub Search + npm 版本查询
├── enrich.py           # Step 1: Haiku 分类 + 评分 + 双语描述
├── write_reports.py    # Step 2: 组装 Obsidian 周报 + 更新状态
├── prompts/
│   └── enrich.md       # 分类门控 + 评分提示词
└── state.json          # 持久化插件追踪状态
```

### Pipeline 流程
```
Step 0: fetch.py (GitHub Search + npm Registry → JSON)
  ↓
Step 1: enrich.py (Claude Haiku → classify + score + bilingual summaries)
  ↓
Step 2: write_reports.py (→ Obsidian weekly markdown + state update)
  ↓
Step 3: archive (>14 周报告归档)
```

### 触发方式
| 方式 | 说明 |
|------|------|
| 手动 | `/feeds/cc-plugins` slash 命令 |

### 输出
- `Feeds/CC-Plugins/YYYY-WXX.md` — 中文周报
- `Feeds/CC-Plugins/YYYY-WXX-en.md` — 英文周报
- `Feeds/CC-Plugins/Dashboard.md` — 索引

### 分类
`productivity` · `code-quality` · `integration` · `knowledge` · `devops` · `other`

### 评分维度
| 维度 | 权重 | 说明 |
|------|------|------|
| Usefulness | 30% | 对日常 Claude Code 工作流的实用价值 |
| Maturity | 25% | Star 数、下载量、文档质量、版本稳定性 |
| Activity | 25% | 近期提交、发布频率、是否活跃 |
| Relevance | 20% | 与 Ted 工作流的匹配度（Obsidian、代码分析、知识管理） |

### 状态追踪
`state.json` 跟踪已知插件，每周对比：
- 🆕 新发现 — 首次出现
- 📦 版本更新 — npm 版本变化
- 无变化 — 跳过，不写入报告

### 性能
~60-120 秒（GitHub 搜索 + npm 查询 + 单次 Haiku 调用）。可选设置 `GITHUB_TOKEN` 提高 API 速率限制。

## Quick Start

1. **无需额外 pip 包** — Python 标准库即可（pipeline 需要 `ANTHROPIC_API_KEY`）
2. **手动运行** → `/feeds/cc-plugins` — 生成本周 Claude Code 插件摘要（中英文双版）
3. **(可选)** → 设置 `GITHUB_TOKEN` 环境变量以提高 API 速率限制
4. **查看结果** → `Feeds/CC-Plugins/` 目录下的 `YYYY-WXX.md`（中文）和 `YYYY-WXX-en.md`（英文）

**周期节奏**: 每周手动 `/feeds/cc-plugins` → Home.md CC Plugins 区域查看

## 配置位置
| 组件 | 位置 |
|------|------|
| 编排器 | `scripts/cc-plugins/run.sh` |
| 分类提示词 | `scripts/cc-plugins/prompts/enrich.md` |
| 权限 | `.claude/settings.json` (Bash allow list) |
| slash 命令 | `.claude/commands/feeds/cc-plugins.md` |

---
🏠 [[Home]] · 📊 [[system/registry|Registry]] · 🚀 [[GETTING_STARTED|Getting Started]]

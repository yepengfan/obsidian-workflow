---
module: feed-orchestrator
label: "Feed Orchestrator"
type: feed
status: active
enabled: true
created: 2026-05-21
updated: 2026-05-21
depends_on: [feeds-ai-digest, feeds-github-trending, feeds-engineering-blogs, feeds-cc-plugins, dashboard]
requires:
  python: ">=3.13"
  pip: [claude-agent-sdk, anthropic, aiohttp]
  plugins: [dataview, obsidian-shellcommands]
  env:
    ANTHROPIC_API_KEY: "(required) Anthropic API key for Agent SDK orchestration + Haiku enrichment"
commands: []
templates: []
scripts:
  - scripts/feed-orchestrator/main.py
  - scripts/feed-orchestrator/tools.py
  - scripts/feed-orchestrator/feeds.py
  - scripts/feed-orchestrator/status.py
  - scripts/feed-orchestrator/load-env.sh
hooks: []
folders: []
config_files:
  - scripts/feed-orchestrator/requirements.txt
  - .obsidian/plugins/obsidian-shellcommands/data.json
tags: [system/module]
---

# Feed Orchestrator

## Overview
Claude Agent SDK 驱动的全自动 Feed 生成器。通过 Home.md 上的 "Generate Feeds" 按钮触发，一键生成全部 4 个 Feed 管线（3 个日报 + 1 个周报）。

依赖:
- [[system/modules/feeds-ai-digest/module|AI Daily Digest]]
- [[system/modules/feeds-github-trending/module|GitHub Trending]]
- [[system/modules/feeds-engineering-blogs/module|Engineering Blogs]]
- [[system/modules/feeds-cc-plugins/module|CC Plugins]]

## 架构

```
scripts/feed-orchestrator/
├── main.py              # Agent SDK 入口 — query() 循环
├── tools.py             # 7 个 @tool 定义（check/fetch/enrich/write/archive/status）
├── feeds.py             # Feed 配置 + Anthropic SDK 增强逻辑
├── status.py            # 状态文件管理（原子写入 .feed-status.json）
├── load-env.sh          # Shell Commands 入口（加载环境变量）
├── requirements.txt     # claude-agent-sdk, anthropic, aiohttp
└── .venv/               # Python 虚拟环境
```

### 工作流程
```
Home.md [Generate Feeds ▶] 按钮
  ↓  (Shell Commands 插件)
load-env.sh  →  main.py
  ↓
Agent SDK query() 循环：
  1. check_module_status()  — 检查各模块开关
  2. check_existing_report() — 跳过已存在的报告
  3. fetch_feed()  — 运行现有 fetch.py（子进程）
  4. enrich_feed() — Anthropic SDK + Haiku 评分/增强
  5. write_report() — 运行现有 write_reports.py（子进程）
  6. archive_old_reports() — 归档旧报告
  ↓
Feeds/.feed-status.json  ← 每步更新
  ↓
Home.md 轮询显示实时状态徽章
```

### 关键设计
| 决策 | 说明 |
|------|------|
| Agent SDK 替代 bash | 不再需要 run.sh 脚本，Python 统一编排 |
| Haiku 做批量 LLM 工作 | 评分/增强使用 Haiku（成本 ~$0.01），Agent SDK 仅编排（~$0.05-0.15） |
| 复用现有 Python | fetch.py 和 write_reports.py 以子进程调用，无需重写 |
| 原子状态文件 | tmp + rename 防止读取损坏，Home.md 每 3 秒轮询 |
| 并发锁 | 检查 .feed-status.json 中运行中的 feed（< 15 分钟），防止重复运行 |

### 触发方式
| 方式 | 说明 |
|------|------|
| Home.md 按钮 | "Generate Feeds ▶" 按钮，带实时状态徽章 |
| 命令面板 | "Execute: Generate All Feeds" |
| CLI | `bash scripts/feed-orchestrator/load-env.sh` |

### 输出
生成的报告由各子模块管理:
- `Feeds/AI-Daily/YYYY-MM-DD.md` — AI 日报（中英文）
- `Feeds/GitHub-Trending/YYYY-MM-DD.md` — GitHub 趋势（中英文）
- `Feeds/Engineering-Blogs/YYYY-MM-DD.md` — 工程博客（中英文）
- `Feeds/CC-Plugins/YYYY-Wxx.md` — CC 插件周报（中英文）
- `Feeds/.feed-status.json` — 运行状态（Home.md 轮询用）

### 性能
- AI Digest: ~4-6 分钟（92 RSS + Haiku 批量评分/摘要）
- GitHub Trending: ~30-60 秒
- Engineering Blogs: ~30-60 秒
- CC Plugins: ~60-120 秒
- 编排开销: ~$0.05-0.15 per run（Agent SDK）

## Quick Start

1. **安装** → `cd scripts/feed-orchestrator && python3.13 -m venv .venv && .venv/bin/pip install -r requirements.txt`
2. **手动运行** → `bash scripts/feed-orchestrator/load-env.sh`
3. **按钮运行** → Home.md Feeds 区域点击 "Generate Feeds ▶"
4. **查看结果** → 各 Feeds/ 子目录下的日期文件

## 配置位置
| 组件 | 位置 |
|------|------|
| Agent SDK 入口 | `scripts/feed-orchestrator/main.py` |
| 工具定义 | `scripts/feed-orchestrator/tools.py` |
| Feed 配置 + 增强 | `scripts/feed-orchestrator/feeds.py` |
| 状态管理 | `scripts/feed-orchestrator/status.py` |
| 环境包装 | `scripts/feed-orchestrator/load-env.sh` |
| Shell Command | `.obsidian/plugins/obsidian-shellcommands/data.json` |
| Home.md 按钮 | `Home.md` (Feeds dataviewjs block) |

---
🏠 [[Home]] · 📊 [[system/registry|Registry]] · 🚀 [[GETTING_STARTED|Getting Started]]

---
module: feeds-podcast
label: "Podcast Feed"
type: feed
status: active
enabled: true
created: 2026-04-01
updated: 2026-04-01
depends_on: [dashboard]
requires:
  cli: [claude, ffmpeg]
  python: ">=3.13"
  pip: [mlx-whisper, feedparser]
  plugins: [dataview, media-extended]
  env:
    ANTHROPIC_API_KEY: "(required) Claude API key for scoring/summarization"
commands: [podcast]
templates: []
scripts:
  - scripts/podcast/run.sh
  - scripts/podcast/fetch.py
  - scripts/podcast/transcribe.py
  - scripts/podcast/enrich.py
  - scripts/podcast/write_notes.py
  - scripts/podcast/lifecycle.py
hooks: []
folders: [Podcasts/]
config_files:
  - .claude/commands/feeds/podcast.md
  - Podcasts/Feeds.md
  - scripts/podcast/feeds.txt
  - scripts/podcast/state.json
  - scripts/podcast/prompts/score.md
  - scripts/podcast/prompts/summarize.md
tags: [system/module]
---

# Podcast Feed

## Overview
播客订阅管线。从用户订阅的 RSS 源获取新 episode，本地 Whisper 转写，Claude 评分 + 双语摘要，输出 Obsidian 笔记 + 推荐首页。

依赖: [[system/modules/dashboard/module|dashboard]]

## 架构

```
scripts/podcast/
├── run.sh              # 编排器（5 步骤）
├── fetch.py            # Step 0: RSS 抓取 + 音频下载
├── transcribe.py       # Step 1: mlx-whisper 本地转写
├── enrich.py           # Step 2: Claude 评分 + 双语摘要
├── write_notes.py      # Step 3: 生成 Obsidian 笔记 + 推荐首页
├── lifecycle.py        # Step 4: 音频归档 + 清理
├── feeds.txt           # RSS 订阅列表
├── state.json          # 已处理 episode 记录
├── podcast.log         # 运行日志
└── prompts/
    ├── score.md        # 评分提示词（4 维度加权）
    └── summarize.md    # 摘要提示词（双语 + 要点 + Zettel 候选）
```

### Pipeline 流程
```
Step 0: fetch.py (RSS feeds → JSON + .mp3 下载)
  ↓
Step 1: transcribe.py (mlx-whisper → .srt + transcript JSON)
  ↓
Step 2: enrich.py (Claude → score + 双语摘要 + 要点)
  ↓
Step 3: write_notes.py (→ Episode 笔记 + Podcasts.md 推荐首页)
  ↓
Step 4: lifecycle.py (→ 音频归档 + 清理)
```

### 触发方式
| 方式 | 说明 |
|------|------|
| 手动 | `/feeds/podcast` slash 命令 |

### 输出
- `Podcasts/episodes/{slug}.md` — Episode 笔记（含双语摘要、要点、Zettel 候选、嵌入音频）
- `Podcasts/audio/{slug}.mp3` — 音频文件
- `Podcasts/audio/{slug}.srt` — 字幕文件（供 Media Extended 使用）
- `Podcasts/Podcasts.md` — 推荐首页（按分数分组）

### 评分维度
- 信息密度 (30%): 干货 vs 闲聊比例
- 新颖性 (25%): 是否有新观点/新信息
- 可操作性 (25%): 是否有可执行的 takeaway
- 兴趣匹配 (20%): AI/tech/personal growth 相关度

### 生命周期管理
```
unlistened → listened → archived
                │             │
          +30 天音频        +90 天
          移到 archive/    删除音频
                          (保留 .srt + 笔记)
```

### 性能
- 单个 1h episode: ~5-10 分钟（下载 + 本地 Whisper 转写 + Claude 评分）
- 批量 10 个 episode: ~60 分钟以内
- 转写使用本地 Apple Silicon GPU，不依赖网络

## Quick Start

1. **首次安装** → `bash scripts/podcast/setup.sh`（创建 venv、安装依赖、检查 ffmpeg）
2. **添加订阅** → 编辑 `scripts/podcast/feeds.txt`，每行一个 RSS URL
3. **手动运行** → `/feeds/podcast` — 处理新 episode，生成笔记
4. **查看推荐** → `Podcasts/Podcasts.md` — 按分数分组的推荐首页
5. **桌面收听** → 打开 Episode 笔记，通过 Media Extended 同步音频 + 字幕

**日常节奏**: Apple Podcasts 发现好节目 → 添加 RSS 到 feeds.txt → `/feeds/podcast` → Podcasts.md 查看推荐 → 收听 → `status: listened` 标记已听

## 配置位置
| 组件 | 位置 |
|------|------|
| 编排器 | `scripts/podcast/run.sh` |
| RSS 订阅列表 | `scripts/podcast/feeds.txt` |
| Episode 状态记录 | `scripts/podcast/state.json` |
| 评分提示词 | `scripts/podcast/prompts/score.md` |
| 摘要提示词 | `scripts/podcast/prompts/summarize.md` |
| 权限 | `.claude/settings.json` (Bash allow list) |
| slash 命令 | `.claude/commands/feeds/podcast.md` |

---
🏠 [[Home]] · 📊 [[system/registry|Registry]] · 🚀 [[GETTING_STARTED|Getting Started]]

# Podcast Pipeline — Architecture

> Created: 2026-04-01
> Status: Final

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Podcast Pipeline System                       │
│                                                                  │
│  ┌──────────┐    ┌──────────────────────────────────────────┐   │
│  │  Apple    │    │         scripts/podcast/                 │   │
│  │ Podcasts  │───>│                                          │   │
│  │ (发现)    │    │  feeds.txt ──> run.sh (编排器)            │   │
│  └──────────┘    │                  │                        │   │
│                  │    ┌─────────────┼─────────────┐          │   │
│                  │    ▼             ▼             ▼          │   │
│                  │  Step 0       Step 1        Step 2        │   │
│                  │  fetch.py     transcribe.py  enrich.py    │   │
│                  │  (RSS+下载)   (Whisper)      (Claude)     │   │
│                  │    │             │             │          │   │
│                  │    ▼             ▼             ▼          │   │
│                  │         Step 3: write_notes.py            │   │
│                  │              (生成笔记)                    │   │
│                  │                  │                        │   │
│                  │                  ▼                        │   │
│                  │         Step 4: lifecycle.py              │   │
│                  │           (归档 + 清理)                    │   │
│                  └──────────────────┼───────────────────────┘   │
│                                     │                           │
│  ┌──────────────────────────────────▼──────────────────────┐   │
│  │                   Obsidian Vault                         │   │
│  │                                                          │   │
│  │  Podcasts/                                               │   │
│  │  ├── Podcasts.md          ← 推荐首页                     │   │
│  │  ├── episodes/*.md        ← Episode 笔记                 │   │
│  │  └── audio/*.mp3 + *.srt  ← 音频 + 字幕                  │   │
│  │                                                          │   │
│  │  Media Extended Plugin    ← 桌面端播放 + 字幕同步          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Pipeline Steps

### Step 0: fetch.py — RSS 抓取 + 音频下载

```
Input:  feeds.txt (RSS URLs)
Output: JSON (episode 元数据 + 本地音频路径)

feeds.txt ──> feedparser ──> 过滤新 episode ──> 下载 .mp3
                                   │
                             state.json (已处理 GUID)
```

**职责：**
- 读取 `feeds.txt`，解析每个 RSS feed
- 对比 `state.json` 过滤已处理的 episode
- 提取 episode 元数据：title, podcast_name, date, duration, description, guid
- 下载音频到 `Podcasts/audio/`
- 文件命名规则：`{podcast-slug}-{episode-slug}.mp3`
  - slug 生成：小写 + 特殊字符替换为连字符 + 截断到 60 字符
- 输出 JSON 到 stdout（与 ai-digest 模式一致）

**错误处理：**
- Feed 解析失败 → 记录日志，跳过该 feed，继续处理其他 feed
- 音频下载失败 → 记录日志，跳过该 episode
- 已存在的音频文件 → 跳过下载

### Step 1: transcribe.py — Whisper 本地转写

```
Input:  JSON (含本地音频路径列表)
Output: JSON (追加 transcript 字段)

音频文件 ──> mlx-whisper ──> .srt (字幕) + transcript JSON
                 │
           large-v3-turbo 模型
           word-level timestamps
           自动语言检测
```

**职责：**
- 遍历新 episode 音频文件
- 使用 `mlx_whisper.transcribe()` 转写
- 生成 `.srt` 文件到 `Podcasts/audio/`（与 .mp3 同名配对）
- 将 transcript segments (text + timestamps) 注入 JSON
- 已存在的 .srt → 跳过转写

**配置：**
```python
MODEL = "mlx-community/whisper-large-v3-turbo"
WORD_TIMESTAMPS = True
OUTPUT_FORMAT = "srt"  # for Media Extended
```

**SRT 输出示例：**
```srt
1
00:00:00,000 --> 00:00:04,200
Welcome to the Lex Fridman Podcast.

2
00:00:04,200 --> 00:00:08,100
Today I have the pleasure of speaking
with Yann LeCun.
```

### Step 2: enrich.py — Claude 评分 + 摘要

```
Input:  JSON (含 transcript)
Output: JSON (追加 score, summary, takeaways)

transcript ──> claude -p ──> 评分 + 双语摘要 + 要点
                  │
            prompts/score.md
            prompts/summarize.md
```

**职责：**
- 两阶段处理（与 ai-digest 一致）：
  1. **Score phase**: 传入 transcript → 输出分数 + 分类
  2. **Summarize phase**: 传入 transcript + 分数 → 输出摘要 + 要点 + Zettel 候选
- 使用 `claude -p` CLI 调用（支持并行处理多个 episode）
- 超长 transcript（>100K tokens）→ 截取前 80% + 最后 10%（保留开头和结尾）

**评分 Prompt (prompts/score.md) 核心逻辑：**
```
维度（各 1-10，取加权平均）：
- 信息密度 (30%): 干货 vs 闲聊比例
- 新颖性 (25%): 是否有新观点/新信息
- 可操作性 (25%): 是否有可执行的 takeaway
- 兴趣匹配 (20%): AI/tech/personal growth 相关度
```

**摘要 Prompt (prompts/summarize.md) 输出结构：**
```json
{
  "summary_zh": "中文一句话摘要",
  "summary_en": "English one-line summary",
  "takeaways": ["要点1", "要点2", ...],
  "zettel_candidates": ["可转化为 Zettel 的观点1", ...]
}
```

### Step 3: write_notes.py — 生成 Obsidian 笔记

```
Input:  JSON (完整 enriched 数据)
Output: Markdown 文件

enriched JSON ──> Episode 笔记 (.md)
             ──> 推荐首页 (Podcasts.md)
             ──> state.json 更新
```

**职责：**
- 为每个新 episode 生成 `Podcasts/episodes/{slug}.md`
- 刷新 `Podcasts/Podcasts.md` 推荐首页
- 更新 `state.json` 记录已处理的 episode

**Episode 笔记模板：**
```markdown
---
type: podcast-episode
podcast: "{podcast_name}"
episode: "{episode_number}"
title: "{title}"
date: {publish_date}
duration: "{HH:MM:SS}"
score: {score}
status: unlistened
listened_date:
archived_date:
audio: "[[Podcasts/audio/{slug}.mp3]]"
tags: [podcast, {auto_tags}]
---

# {title}

## Summary
> [!abstract]
> {summary_zh}
>
> {summary_en}

## Key Takeaways
{takeaways as bullet list}

## Zettel Candidates
> [!tip] 可转化为 Zettel 的观点
{zettel_candidates as bullet list}

## Audio
![[Podcasts/audio/{slug}.mp3]]

## Transcript
{timestamped transcript in markdown format}

## My Notes
> ✍️ Write your thoughts here...
```

**推荐首页 (Podcasts.md) 结构：**
```markdown
---
type: dashboard
---
# Podcast Feed

## New Episodes
> [!tip] 上次更新：{date} | 共 {count} 期新内容

### ⭐ Strongly Recommended (9-10)
| Podcast | Episode | Score | Duration | Summary |
|---------|---------|:-----:|----------|---------|
| ... |

### 👍 Worth Listening (7-8)
| ... |

### 📋 Optional (5-6)
| ... |

### ⏭️ Skip (<5)
| ... |

## Recently Listened
{dataview query for status=listened, last 10}

## Stats
{dataview query for counts}
```

### Step 4: lifecycle.py — 归档 + 清理

```
Podcasts/audio/*.mp3 ──> 检查对应笔记 status + 日期
                              │
                    ┌─────────┼──────────┐
                    ▼         ▼          ▼
               保留        归档到       删除音频
            (unlistened)  archive/     (保留笔记)
                         (listened    (.srt 保留)
                          +30 天)     (+90 天)
```

**职责：**
- 扫描 `Podcasts/audio/` 下所有 .mp3 文件
- 读取对应 episode 笔记的 frontmatter（status, listened_date, archived_date）
- 自动补填：若 status=listened 但无 listened_date → 设为今天
- 执行归档/清理规则
- 更新笔记 frontmatter（status + 对应日期字段）
- 记录操作到日志

**规则：**
```python
ARCHIVE_AFTER_DAYS = 30   # listened_date + 30d → archived
DELETE_AFTER_DAYS = 90    # archived_date + 90d → audio deleted
```

## 3. Data Flow

```
feeds.txt
    │
    ▼
┌─────────┐     ┌──────────┐     ┌─────────┐     ┌──────────────┐
│ fetch.py │────>│transcribe│────>│enrich.py│────>│write_notes.py│
│          │     │   .py    │     │         │     │              │
│ RSS解析  │     │ Whisper  │     │ Claude  │     │ Markdown生成  │
│ 音频下载 │     │ 转写     │     │ 评分摘要│     │ 首页刷新      │
└─────────┘     └──────────┘     └─────────┘     └──────────────┘
    │                │                │                │
    ▼                ▼                ▼                ▼
 .mp3 文件       .srt 文件      enriched JSON     .md 笔记
 state.json      transcript                      Podcasts.md

                        ┌────────────┐
                        │lifecycle.py│
                        │  归档/清理  │
                        └────────────┘
```

**数据在步骤间通过 stdout/stdin JSON pipe 传递（与 ai-digest 一致）：**
```bash
EPISODES=$("$PYTHON" fetch.py)
TRANSCRIBED=$(echo "$EPISODES" | "$PYTHON" transcribe.py)
ENRICHED=$(echo "$TRANSCRIBED" | "$PYTHON" enrich.py)
echo "$ENRICHED" > "$TMPDIR/enriched.json"
"$PYTHON" write_notes.py
```

## 4. File Naming Convention

```
Podcast name: "Lex Fridman Podcast"
Episode title: "Episode #401: Yann LeCun on World Models"

Slug: lex-fridman-podcast-episode-401-yann-lecun-on-world-models
  ↓ (truncated to 60 chars)
Slug: lex-fridman-podcast-episode-401-yann-lecun-on-world-mode

Files generated:
  Podcasts/audio/lex-fridman-podcast-episode-401-yann-lecun-on-world-mode.mp3
  Podcasts/audio/lex-fridman-podcast-episode-401-yann-lecun-on-world-mode.srt
  Podcasts/episodes/lex-fridman-podcast-episode-401-yann-lecun-on-world-mode.md
```

## 5. Module Integration

```
system/modules/feeds-podcast/module.md
  ├── module: feeds-podcast
  ├── type: feed
  ├── enabled: true
  ├── depends_on: [dashboard]
  ├── requires:
  │     cli: [claude, ffmpeg]
  │     python: ">=3.13"
  │     pip: [mlx-whisper, feedparser]
  │     plugins: [dataview, media-extended]
  │     env: {ANTHROPIC_API_KEY: "..."}
  ├── commands: [podcast]
  ├── scripts: [run.sh, fetch.py, transcribe.py, enrich.py, write_notes.py, lifecycle.py]
  └── folders: [Podcasts/]

.claude/commands/feeds/podcast.md
  ├── Module guard (check enabled)
  ├── Run pipeline: bash scripts/podcast/run.sh
  └── Report results
```

## 6. Error Handling Strategy

```
run.sh
  │
  ├── Step 0: fetch.py
  │     ├── Feed parse error     → log + skip feed
  │     ├── Download error       → log + skip episode
  │     └── No new episodes      → exit 0 (idempotent)
  │
  ├── Step 1: transcribe.py
  │     ├── Whisper model load   → exit 1 (fatal)
  │     ├── Transcribe error     → log + skip episode
  │     └── No audio to process  → pass through (no-op)
  │
  ├── Step 2: enrich.py
  │     ├── Claude CLI missing   → exit 1 (fatal)
  │     ├── API rate limit       → retry with backoff
  │     └── Single episode fail  → log + skip (use empty summary)
  │
  ├── Step 3: write_notes.py
  │     ├── Write error          → exit 1 (fatal)
  │     └── Partial write        → cleanup + retry
  │
  └── Step 4: lifecycle.py
        ├── Archive error        → log + continue
        └── Delete error         → log + continue
```

# Podcast Pipeline — Feature Research

> Created: 2026-04-01
> Status: Final

## 1. 需求背景

用户当前使用 Apple Podcasts 收听播客，但缺乏系统性的内容管理和知识提取能力。目标是在 Obsidian vault 内构建一个完整的播客消费和学习系统：

- **发现**：Apple Podcasts 作为播客源发现渠道
- **评估**：AI 自动转写 + 打分 + 推荐，帮助筛选值得听的内容
- **消费**：在 Obsidian 桌面端边听音频边看同步字幕（transcript）
- **产出**：从播客内容中提取想法，转化为 Zettelkasten 笔记

## 2. 技术调研

### 2.1 RSS Feed 解析

Apple Podcasts 的每个节目都有对应的 RSS feed。获取方式：
- Apple Podcasts 页面 URL → 通过 iTunes Lookup API 获取 `feedUrl`
- 直接搜索节目名找到 RSS feed URL

**推荐库**：`feedparser`（Python，成熟稳定，支持所有 RSS/Atom 格式）

RSS `<enclosure>` 标签包含音频文件直链（通常是 .mp3），可直接下载。

### 2.2 音频转写（Speech-to-Text）

| 方案 | 速度 (1h 音频) | 质量 | 成本 | 时间戳 | 语言 |
|------|---------------|------|------|--------|------|
| **mlx-whisper** (large-v3-turbo) | ~2-4 min | 优秀 | 免费，本地 | word-level | 多语言自动检测 |
| whisper.cpp (large-v3) | ~5-8 min | 优秀 | 免费，本地 | segment-level | 多语言 |
| OpenAI Whisper API | ~1 min | 优秀 | $0.006/min ≈ $0.36/h | segment-level | 多语言 |
| Deepgram API | ~0.5 min | 很好 | $0.0043/min | word-level | 多语言 |

**选择：mlx-whisper (large-v3-turbo)**
- Apple Silicon 原生优化，M 系列芯片上最快
- 免费，无 API 限制
- 支持 word-level timestamps
- 输出格式灵活（JSON / SRT / VTT / TXT）
- 自动语言检测，中英文播客都能处理

### 2.3 AI 摘要与评分

复用 vault 已有模式：通过 `claude` CLI 调用 Haiku 模型。

输入：完整 transcript 文本
输出：
- 评分（1-10）
- 双语一句话摘要（中文 + English）
- 5-8 个关键要点
- 可转化为 Zettel 的观点候选

**注意**：播客 transcript 通常很长（1h ≈ 8000-12000 words），需要考虑 token 限制。
方案：对超长 transcript 分段处理，或使用 Haiku 的 200K context window。

### 2.4 Obsidian 音频播放 + 字幕同步

#### Media Extended 插件

| 特性 | 支持情况 |
|------|---------|
| 本地音频播放 | ✅ |
| .srt/.vtt 字幕加载 | ✅ 自动检测同名字幕文件 |
| 点击时间戳跳转 | ✅ 核心功能 |
| 全局快捷键控制 | ✅ |
| 移动端 | ❌ 不支持（桌面专属） |
| 维护状态 | ✅ 活跃（v4.1.5, 2025-12, 最新 commit 2026-02） |
| 开源 | ⚠️ v4 闭源，v3 MIT |

GitHub: [PKM-er/media-extended](https://github.com/PKM-er/media-extended) (876⭐)

#### 字幕文件策略

Media Extended 支持自动关联同名字幕：
```
Podcasts/audio/lex-401.mp3
Podcasts/audio/lex-401.srt  ← 自动加载
```

Pipeline 同时生成：
1. `.srt` 文件 → Media Extended 桌面字幕同步
2. Markdown transcript 嵌入笔记 → 手机端 fallback + 永久存档

#### 替代方案（备选）

| 插件 | 功能 | 适用场景 |
|------|------|---------|
| Podcast Note (81⭐) | 从 Apple/Spotify URL 抓元数据 | 快速收集（支持移动端） |
| Timestamp Player (1⭐) | 音频 + 时间戳跳转 | 更轻量但不成熟 |

### 2.5 音频文件管理

用户 vault 通过 S3 同步，音频文件大小不是核心瓶颈。

生命周期策略：
- 音频放在 vault 内 `Podcasts/audio/`
- `listened` 状态 + 30 天 → 归档到 `Podcasts/audio/archive/`
- 归档 + 90 天 → 删除音频文件
- 笔记和 transcript（.md + .srt）永久保留

### 2.6 已有 Pipeline 模式参考

Vault 中已有两个成熟 pipeline：
- `scripts/ai-digest/` — RSS → 评分 → 摘要 → Markdown (Python + Claude CLI)
- `scripts/github-trending/` — API → 分类评分 → Markdown (Python + Claude CLI)

共同模式：
- `run.sh` 编排器（module guard + step-by-step + 归档）
- `state.json` / `history.json` 防重复处理
- `prompts/*.md` 可编辑的 AI 提示词
- `write_reports.py` 生成 Obsidian markdown
- Module manifest in `system/modules/`
- Slash command in `.claude/commands/feeds/`

## 3. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 长播客转写耗时（>2h 节目） | Pipeline 运行时间长 | 支持断点续传，已转写的跳过 |
| Transcript 质量（口音/专业术语） | 影响 AI 摘要准确性 | 使用 large-v3-turbo 模型，质量最好 |
| 音频文件大 | S3 同步流量 | 生命周期管理 + 定期清理 |
| Media Extended v4 闭源 | 长期可维护性 | 字幕也嵌入 markdown，不完全依赖插件 |
| RSS feed 变更/失效 | 获取失败 | 错误处理 + 日志记录，跳过失效 feed |

## 4. 结论

方案可行，技术栈成熟。复用已有 pipeline 架构可以大幅降低开发成本。核心创新点是 Whisper 本地转写 + Media Extended 字幕同步，形成完整的「播客 → 知识」闭环。

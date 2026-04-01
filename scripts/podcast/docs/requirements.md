# Podcast Pipeline — Requirements

> Created: 2026-04-01
> Status: Final

## 1. 功能需求

### FR-01: RSS 订阅管理
- 用户通过 `feeds.txt` 文件管理播客订阅（一行一个 RSS feed URL）
- 支持注释行（`#` 开头）用于分组和说明
- feeds.txt 格式示例：
  ```
  # Tech / AI
  https://lexfridman.com/feed/podcast/
  https://feeds.simplecast.com/54nAGcIl  # Huberman Lab

  # 中文播客
  https://example.com/feed.xml  # 某中文播客
  ```

### FR-02: 批量更新
- 手动触发 `/feeds/podcast` 命令执行批量更新
- 解析所有订阅 feed，检测新 episode
- 下载新 episode 的音频文件（.mp3）
- 使用 `state.json` 记录已处理的 episode GUID，防止重复

### FR-03: 本地转写
- 使用 mlx-whisper (large-v3-turbo) 本地转写
- 输出带时间戳的 `.srt` 字幕文件（供 Media Extended 使用）
- 输出 JSON 格式的 transcript（供后续处理和 markdown 生成）
- 自动检测语言（支持中英文播客）
- 已转写的音频跳过（断点续传）

### FR-04: AI 评分与推荐
- 基于 transcript 全文进行内容评分（1-10 分）
- 评分维度：
  - 信息密度（干货程度）
  - 新颖性（是否有新观点）
  - 可操作性（是否有可执行的 takeaway）
  - 与用户兴趣的匹配度（AI/tech/personal growth）
- 生成双语一句话摘要（中文 + English）
- 提取 5-8 个关键要点（Key Takeaways）
- 标记「Zettel 候选」观点

### FR-05: 推荐首页
- `Podcasts/Podcasts.md` 作为推荐首页
- 按分数分组展示：⭐ 强推 (9-10) / 👍 值得听 (7-8) / 📋 可选 (5-6) / ⏭️ 可跳过 (<5)
- 显示节目名、标题、分数、时长、一句话摘要
- 包含统计信息（本周新增、已听数量等）
- 每次批量更新时刷新

### FR-06: Episode 笔记
- 每个 episode 生成一个 `.md` 笔记到 `Podcasts/episodes/`
- Frontmatter 包含结构化元数据（podcast, episode, date, duration, score, status, tags）
- 包含双语摘要、关键要点、Zettel 候选标记
- 嵌入音频播放器（`![[Podcasts/audio/xxx.mp3]]`）
- 包含 Markdown 格式的时间戳 transcript（手机 fallback）
- 包含「我的笔记」空白区域供用户记录想法

### FR-07: 桌面端音频 + 字幕同步
- 依赖 Media Extended 插件
- 音频文件和 `.srt` 字幕文件同名配对存放在 `Podcasts/audio/`
- 点击时间戳跳转到音频对应位置

### FR-08: 生命周期管理
- Episode status 流转：`unlistened` → `listened` → `archived`
- 用户手动修改 frontmatter `status: listened` 标记已听
- 当 status 变为 `listened` 时，`listened_date` 需要被设置（用户手动设置，或 lifecycle.py 首次发现 status=listened 且无 listened_date 时自动补填当天日期）
- 归档规则：`listened_date` + 30 天 → 音频移到 `Podcasts/audio/archive/`，笔记 status 更新为 `archived`，设置 `archived_date`
- 清理规则：`archived_date` + 90 天 → 删除音频文件（保留 .srt 和笔记）
- 生命周期操作在每次 `run.sh` 执行时自动运行

## 2. 非功能需求

### NFR-01: 性能
- 单个 1h episode 端到端处理时间 < 10 分钟（下载 + 转写 + 评分 + 生成笔记）
- 批量更新 10 个新 episode 总耗时 < 60 分钟
- 转写使用本地 GPU (Apple Silicon)，不依赖网络

### NFR-02: 幂等性
- 重复运行 `run.sh` 不产生重复笔记或重复下载
- 使用 `state.json` 记录已处理的 episode GUID
- 已存在的笔记不覆盖

### NFR-03: 错误容忍
- 单个 feed 获取失败不影响其他 feed
- 单个 episode 转写失败不影响其他 episode
- 所有错误记录到日志文件 `scripts/podcast/podcast.log`

### NFR-04: 一致性
- Pipeline 架构与 `scripts/ai-digest/` 和 `scripts/github-trending/` 保持一致
- Module manifest 格式与其他 feeds module 一致
- Slash command 格式与其他 feeds command 一致

### NFR-05: 可配置
- 所有 AI prompts 存放在 `scripts/podcast/prompts/` 可独立编辑
- 评分阈值、归档天数等通过常量定义在脚本顶部
- Feed 列表通过 `feeds.txt` 管理

## 3. Vault 结构

```
scripts/podcast/
├── run.sh              # 编排器
├── fetch.py            # Step 0: RSS 抓取 + 音频下载
├── transcribe.py       # Step 1: mlx-whisper 转写
├── enrich.py           # Step 2: Claude 评分 + 摘要
├── write_notes.py      # Step 3: 生成 Obsidian 笔记
├── lifecycle.py        # Step 4: 音频归档 + 清理
├── feeds.txt           # RSS 订阅列表
├── state.json          # 已处理 episode 记录
├── podcast.log         # 运行日志
├── prompts/
│   ├── score.md        # 评分 prompt
│   └── summarize.md    # 摘要 prompt
└── docs/               # 设计文档（本文件所在位置）

Podcasts/                   # Vault 中的播客内容
├── Podcasts.md             # 推荐首页
├── episodes/               # Episode 笔记
│   ├── lex-fridman-401-yann-lecun.md
│   └── ...
└── audio/                  # 音频 + 字幕
    ├── lex-fridman-401-yann-lecun.mp3
    ├── lex-fridman-401-yann-lecun.srt
    ├── archive/            # 归档音频
    └── ...

system/modules/feeds-podcast/
└── module.md               # Module manifest

.claude/commands/feeds/
└── podcast.md              # Slash command
```

## 4. 依赖

### 外部工具
| 工具 | 用途 | 安装方式 |
|------|------|---------|
| `mlx-whisper` | 音频转写 | `pip install mlx-whisper` |
| `feedparser` | RSS 解析 | `pip install feedparser` |
| `claude` CLI | AI 评分摘要 | 已安装 |
| `ffmpeg` | 音频格式处理（可选） | `brew install ffmpeg` |

### Obsidian 插件
| 插件 | 用途 | 必需 |
|------|------|------|
| Media Extended | 音频播放 + 字幕同步 + 时间戳跳转 | 是（桌面体验核心） |
| Dataview | 推荐首页查询 | 是（已安装） |

### 环境变量
| 变量 | 用途 |
|------|------|
| `ANTHROPIC_API_KEY` | Claude API（评分 + 摘要） |

## 5. 用户体验流程

```
1. 📱 Apple Podcasts 发现好节目 → 找到 RSS feed URL
2. 📝 添加到 scripts/podcast/feeds.txt
3. 💻 运行 /feeds/podcast → 等待 5-10 分钟
4. 📖 打开 Podcasts/Podcasts.md → 查看 AI 推荐分组
5. 🎧 点进感兴趣的 episode → 桌面端：音频 + 字幕同步播放
6. ✍️ 在笔记「我的笔记」区域记录想法
7. 💡 好观点 → 转化为 Zettel
8. ✅ 听完 → 修改 status: listened
9. 🔄 30 天后音频自动归档，90 天后自动清理
```

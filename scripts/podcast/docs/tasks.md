# Podcast Pipeline — Task Breakdown

> Created: 2026-04-01
> Status: Final

## Implementation Order

任务按依赖关系排序。每个任务标记了预计复杂度和可并行性。

---

## Phase 1: Foundation (基础设施)

### Task 1.1: Module Manifest + Slash Command
**复杂度**: Low
**文件**:
- `system/modules/feeds-podcast/module.md`
- `.claude/commands/feeds/podcast.md`

**内容**:
- 创建 module manifest（参考 feeds-ai-digest 格式）
- 创建 slash command（module guard + run.sh 调用）
- 确保 module-toggle 可以正常启用/禁用

### Task 1.2: Vault Folder Structure
**复杂度**: Low
**文件**:
- `Podcasts/episodes/.gitkeep`
- `Podcasts/audio/.gitkeep`
- `Podcasts/audio/archive/.gitkeep`

**内容**:
- 创建 Podcasts 文件夹结构
- 创建 .gitkeep 保持空目录

### Task 1.3: feeds.txt + state.json
**复杂度**: Low
**文件**:
- `scripts/podcast/feeds.txt`
- `scripts/podcast/state.json`

**内容**:
- 创建 feeds.txt 模板（带注释和示例 URL）
- 创建空 state.json (`{"processed": {}}`)

### Task 1.4: AI Prompts
**复杂度**: Medium
**文件**:
- `scripts/podcast/prompts/score.md`
- `scripts/podcast/prompts/summarize.md`

**内容**:
- 编写评分 prompt（维度、权重、输出格式）
- 编写摘要 prompt（双语摘要、要点提取、Zettel 候选）
- 输出必须是 valid JSON

---

## Phase 2: Core Pipeline (核心管线)

### Task 2.1: fetch.py — RSS 抓取 + 音频下载
**复杂度**: Medium
**依赖**: Task 1.3
**文件**: `scripts/podcast/fetch.py`

**功能**:
- 读取 feeds.txt，跳过注释行和空行
- `feedparser` 解析每个 feed
- 对比 state.json 过滤已处理 episode (by GUID)
- 提取元数据：title, podcast_name, date, duration, description, guid, audio_url
- 下载 .mp3 到 Podcasts/audio/ （使用 urllib 或 aiohttp）
- 生成 slug 文件名（小写 + 连字符 + 截断 60 字符）
- 输出 JSON 到 stdout
- 错误处理：feed 失败跳过，下载失败跳过，已存在跳过

**测试要点**:
- 空 feeds.txt → 正常退出
- 无新 episode → 正常退出 (空 JSON)
- feed URL 失效 → 跳过 + 日志
- 音频 URL 404 → 跳过 + 日志

### Task 2.2: transcribe.py — Whisper 转写
**复杂度**: High
**依赖**: Task 2.1
**文件**: `scripts/podcast/transcribe.py`

**功能**:
- 从 stdin 读取 JSON（含音频路径列表）
- 使用 `mlx_whisper.transcribe()` 转写每个音频
- 生成 .srt 文件（与 .mp3 同名）
- 将 transcript segments 注入 JSON（text + start + end）
- 已存在 .srt → 跳过（从现有文件加载 transcript）
- 输出 enriched JSON 到 stdout

**关键代码**:
```python
import mlx_whisper

result = mlx_whisper.transcribe(
    audio_path,
    path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
    word_timestamps=True
)
```

**SRT 生成**:
- 使用 whisper 的 segment 数据生成标准 SRT 格式
- 每个 segment 一个字幕条目
- 时间格式：HH:MM:SS,mmm

**测试要点**:
- 短音频（<1 min）→ 正常转写
- 长音频（>1h）→ 性能验证
- 中文音频 → 语言自动检测
- 已存在 .srt → 跳过

### Task 2.3: enrich.py — Claude 评分 + 摘要
**复杂度**: Medium
**依赖**: Task 2.2, Task 1.4
**文件**: `scripts/podcast/enrich.py`

**功能**:
- 从 stdin 读取 JSON（含 transcript）
- 两阶段调用 Claude CLI：
  1. Score: transcript → 分数 + 分类
  2. Summarize: transcript + 分数 → 摘要 + 要点 + Zettel 候选
- 超长 transcript 截断策略（前 80% + 后 10%）
- 使用 `claude -p` 并行处理多个 episode（参考 ai-digest/score.py）
- 输出 enriched JSON 到 stdout

**测试要点**:
- 正常 transcript → 有效评分和摘要
- 超长 transcript → 截断后仍能处理
- Claude CLI 失败 → 错误处理

### Task 2.4: write_notes.py — 生成 Obsidian 笔记
**复杂度**: Medium
**依赖**: Task 2.3
**文件**: `scripts/podcast/write_notes.py`

**功能**:
- 从环境变量 TMPDIR_PODCAST 读取 enriched JSON
- 为每个 episode 生成 markdown 笔记
  - YAML frontmatter（所有元数据）
  - 双语摘要区域
  - Key Takeaways 列表
  - Zettel 候选区域
  - 嵌入音频 `![[Podcasts/audio/{slug}.mp3]]`
  - Markdown 格式的时间戳 transcript
  - 空白的 My Notes 区域
- 生成/刷新推荐首页 Podcasts.md
  - 按分数分组
  - 包含 Dataview 统计查询
- 更新 state.json

**测试要点**:
- 单个 episode → 正确生成笔记
- 多个 episode → 批量生成 + 首页更新
- 中文标题 → 正确处理
- 已存在笔记 → 不覆盖

---

## Phase 3: Orchestration (编排层)

### Task 3.1: run.sh — Pipeline 编排器
**复杂度**: Medium
**依赖**: Task 2.1-2.4
**文件**: `scripts/podcast/run.sh`

**功能**:
- Module guard（检查 enabled）
- PATH 设置（兼容 Obsidian Shell Commands）
- 日志记录到 podcast.log
- 5 步顺序执行：fetch → transcribe → enrich → write_notes → lifecycle
- 步骤间 JSON pipe
- 错误处理（每步失败有清晰错误信息）
- 临时目录管理

**参考**: `scripts/ai-digest/run.sh` 的结构

### Task 3.2: lifecycle.py — 归档 + 清理
**复杂度**: Low
**依赖**: Task 2.4
**文件**: `scripts/podcast/lifecycle.py`

**功能**:
- 扫描 Podcasts/audio/ 下所有 .mp3
- 读取对应笔记的 frontmatter
- 规则执行：
  - listened + 30天 → mv to archive/ + 更新 status
  - archived + 90天 → rm 音频（保留 .srt + 笔记）
- 日志记录

---

## Phase 4: Polish (完善)

### Task 4.1: setup.sh — 首次安装脚本
**复杂度**: Low
**文件**: `scripts/podcast/setup.sh`

**内容**:
- 创建 Python venv
- 安装依赖：`mlx-whisper feedparser`
- 检查 ffmpeg 可用性
- 检查 claude CLI 可用性
- 下载 Whisper 模型（首次运行时自动下载，但可以预下载）

### Task 4.2: CLAUDE.md 更新
**复杂度**: Low
**文件**: `CLAUDE.md`

**内容**:
- 在 Folder Structure 中添加 `Podcasts/` 说明
- 在 Feeds/ 说明中添加 Podcast 条目
- 在 Installed Plugins 中添加 Media Extended

---

## Summary

| Phase | Tasks | 预计时间 |
|-------|-------|---------|
| Phase 1: Foundation | 4 tasks | ~15 min |
| Phase 2: Core Pipeline | 4 tasks | ~45 min |
| Phase 3: Orchestration | 2 tasks | ~15 min |
| Phase 4: Polish | 2 tasks | ~10 min |
| **Total** | **12 tasks** | **~85 min** |

## Parallelization Plan (Sub-agents)

```
Agent 1 (sonnet): Phase 1 全部 (Task 1.1-1.4)
    ↓ 完成后
Agent 2 (sonnet): fetch.py + transcribe.py (Task 2.1-2.2)
Agent 3 (sonnet): enrich.py + write_notes.py (Task 2.3-2.4) — 可基于接口约定并行
    ↓ 全部完成后
Agent 4 (sonnet): run.sh + lifecycle.py + setup.sh (Task 3.1-3.2, 4.1)
    ↓ 完成后
Main agent: CLAUDE.md 更新 + 最终 review (Task 4.2)
```

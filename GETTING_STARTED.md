---
tags: [system]
created: 2026-03-29
updated: 2026-03-29
---

# Getting Started 新手上手指南

> [!abstract] 目的
> 从零开始使用这个 Obsidian vault 的完整引导。如果你是第一次打开这个 vault，从这里开始。

## 前置条件

### 必装

| 工具 | 用途 | 安装 |
|------|------|------|
| [Obsidian](https://obsidian.md) | 笔记编辑器 | 官网下载 |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | 所有 slash 命令的运行时 | `npm install -g @anthropic-ai/claude-code` |

> [!warning] 没有 Claude Code = 没有命令
> 这个 vault 的所有自动化（`/work-daily`、`/zettelkasten-zettel` 等）都是 Claude Code slash 命令（Agent Skills）。没装 Claude Code 就只能当普通 Obsidian vault 用。

### Obsidian 插件

打开 vault 后，Obsidian 会提示安装社区插件。按重要性分级：

| 优先级 | 插件 | 用途 |
|--------|------|------|
| **🔴 必装** | Dataview | 所有仪表盘和查询的基础 |
| **🔴 必装** | Homepage | Home.md 作为 Obsidian 落地页 |
| **🟡 推荐** | Shell Commands | AI Digest 自动触发（如果不用 feeds 模块可跳过） |
| **🟡 推荐** | Calendar | 日历视图导航日记 |
| **🟡 推荐** | Spaced Repetition | 间隔重复复习 |
| **🟢 可选** | Kanban | 看板视图 |
| **🟢 可选** | Excalidraw | 手绘图表 |
| **🟢 可选** | Tag Wrangler | 批量管理标签 |
| **🟢 可选** | Table Editor | 表格编辑增强 |
| **🟢 可选** | Mind Map | 思维导图 |
| **🟢 可选** | Hider / Style Settings | UI 美化 |
| **🟢 可选** | URL into Selection | 快速插入链接 |
| **🟢 可选** | Footnotes | 脚注支持 |

### Python（仅 Feeds 模块需要）

如果你要用 AI Digest 或 GitHub Trending：

```bash
# 检查 Python 版本（需要 3.13+）
python3 --version

# AI Digest 还需要 aiohttp
cd scripts/ai-digest
python -m venv .venv
source .venv/bin/activate
pip install aiohttp
```

### 环境变量（仅 Feeds 模块需要）

| 变量 | 用途 | 必需? |
|------|------|-------|
| `ANTHROPIC_API_KEY` | Claude API — Feeds pipeline 用 Haiku 评分和摘要 | Feeds 必需 |
| `GITHUB_TOKEN` | GitHub API — 提高速率限制 | 可选 |

## 第一步：了解 vault 结构

```
.
├── Home.md              ← 主仪表盘（Obsidian 启动时自动打开）
├── system/
│   ├── registry.md      ← 📊 所有模块的状态总览
│   ├── README.md        ← 📖 模块系统文档
│   └── modules/         ← 📦 每个模块的清单
├── Work/                ← 工作日记和项目
├── Zettelkasten/        ← 永久笔记
├── Learning/            ← 学习计划
├── Inbox/               ← 快速捕捉
├── Feeds/               ← AI/GitHub 摘要
├── Templates/           ← 笔记模板
└── .claude/skills/      ← slash 命令定义（Agent Skills）
```

> [!tip] 入口
> 🏠 [[Home]] · 📊 [[system/registry|Registry]] · 📖 [[system/README|Module Docs]]

## 第二步：选择你需要的模块

这个 vault 有 9 个模块，你不需要全部开启。根据你的需求选择：

### 🟢 建议新手先开启

| 模块 | 做什么 | 命令 |
|------|--------|------|
| [[system/modules/dashboard/module\|dashboard]] | Home.md 仪表盘 | （无命令，纯 UI） |
| [[system/modules/work/module\|work]] | 每日工作记录 | `/work-daily`, `/work-project` |
| [[system/modules/zettelkasten/module\|zettelkasten]] | 永久知识库 | `/zettelkasten-zettel`, `/zettelkasten-inbox-review` |

### 🟡 按需开启

| 模块 | 做什么 | 前置条件 |
|------|--------|----------|
| [[system/modules/learning/module\|learning]] | 结构化学习计划 | 依赖 zettelkasten |
| [[system/modules/brownbag/module\|brownbag]] | 技术分享会管理 | 依赖 work |
| [[system/modules/vault-ops/module\|vault-ops]] | 维护工具（整理、备份） | git |

### 🔵 进阶（需要额外配置）

| 模块 | 做什么 | 前置条件 |
|------|--------|----------|
| [[system/modules/feeds-ai-digest/module\|feeds-ai-digest]] | 每日 AI 新闻 | Python 3.13+, aiohttp, ANTHROPIC_API_KEY |
| [[system/modules/feeds-github-trending/module\|feeds-github-trending]] | GitHub 热门仓库 | Python 3.13+, ANTHROPIC_API_KEY |
| [[system/modules/profile/module\|profile]] | 个人 Baseball Card | 依赖 dashboard |

## 第三步：启用模块

在 Claude Code 中运行：

```
/module-toggle <module-name>
```

例如启用工作系统：

```
/module-toggle work
```

`/module-toggle` 会自动检查前置条件（CLI 工具、Python 版本、Obsidian 插件、环境变量、模块依赖），并告诉你缺了什么。

> [!tip] 查看所有模块
> 运行 `/module-toggle`（不带参数）可以查看全部模块状态。

## 第四步：清理个人数据

> [!warning] 这个 vault 包含原作者的个人内容
> 如果你是 fork 来自用的，建议清理以下内容：

| 文件夹 | 操作 |
|--------|------|
| `Work/2026/` | 删除所有日记（保留文件夹结构） |
| `Work/Projects/` | 删除项目页面（保留空文件夹） |
| `Zettelkasten/` | 删除所有 zettel 或保留你感兴趣的 |
| `Inbox/` | 清空 |
| `Learning/AISA/`, `Learning/SYSD/` | 删除（用 `/learning-init` 创建你自己的） |
| `Feeds/AI-Daily/`, `Feeds/GitHub-Trending/` | 删除旧报告（新的会自动生成） |
| `Profile/` | 替换为你自己的 Baseball Card |
| `WeRead/`, `Matter/`, `Instapaper Notes/` | 删除（除非你也用这些 app 并配置了同步） |

保留的结构性文件（不要删）：
- `Home.md`, `Work/Work Dashboard.md`, `Work/Weekly View.md`, `Work/Monthly View.md`
- `Templates/` 下的所有模板
- `system/` 下的所有模块定义
- `.claude/` 下的所有命令定义（skills）
- `sortspec.md`

## 第五步：开始使用

启用模块后，每个模块的 manifest 文件里有 **Quick Start** 部分，告诉你日常怎么用：

```
system/modules/<module-name>/module.md → ## Quick Start
```

或者直接看下面的快速参考：

### 每日工作流（Work + Zettelkasten）

```
早上: /work-daily           → 创建今日笔记，延续昨日未完成任务
工作中: 在 ### 项目名 下写任务
需要时: /work-meeting       → 记录会议
需要时: /work-decision-log  → 记录决策
下班前: /zettelkasten-zettel → 捕捉今天的想法
每周: /zettelkasten-inbox-review → 清理 Inbox
每周: /zettelkasten-retro   → 从工作日记提取经验
```

## 模块依赖关系

```
dashboard ←── work ←── brownbag
    ↑
    ├── feeds-ai-digest
    ├── feeds-github-trending
    └── profile

zettelkasten ←── learning

vault-ops (独立)
```

箭头方向: A ← B 表示 B 依赖 A。启用 B 之前需要先启用 A。

## 常见问题

### Q: Dataview 查询显示报错？
安装并启用 Dataview 插件（Settings → Community Plugins → Browse → Dataview）。

### Q: Home.md 没有自动打开？
安装 Homepage 插件，设置 → Homepage → 选择 `Home.md`。

### Q: `/work-daily` 等命令无法使用？
确保已安装 Claude Code 并在 vault 目录下运行。命令只在 Claude Code 终端里生效。

### Q: AI Digest 运行失败？
检查: (1) Python 3.13+ 已安装 (2) `scripts/ai-digest/.venv/` 存在并已安装 aiohttp (3) `ANTHROPIC_API_KEY` 已设置。

### Q: 如何完全禁用一个模块？
`/module-toggle <name>` — 禁用后该模块的所有命令都会拒绝执行。

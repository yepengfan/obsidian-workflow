---
module: work
label: "Work 工作系统"
type: work
status: active
created: 2026-03-29
updated: 2026-03-29
depends_on: [dashboard]
commands: [daily, project, decision-log, meeting]
templates: [Templates/Work Daily.md, Templates/Work Project.md]
scripts: []
hooks: []
folders: [Work/]
config_files:
  - .claude/commands/daily.md
  - .claude/commands/project.md
  - .claude/commands/decision-log.md
  - .claude/commands/meeting.md
tags: [system/module]
---

# Work 工作系统

## Overview
日常工作记录系统。每天一条日记，按项目分组任务，未完成任务自动延续，支持优先级和排序。

## 架构

```
Work/
├── <YYYY>/
│   └── YYYY-MM-DD.md       # 每日工作笔记
├── Projects/
│   └── <ProjectName>.md    # 项目页面（Dataview 任务汇总）
├── Work Dashboard.md        # 工作仪表盘
├── Weekly View.md           # 周视图
├── Monthly View.md          # 月视图
├── Brownbag Sessions/       # → 见 brownbag 模块
└── archive/                 # 历史年份
```

### 数据流
- **每日**: `/daily` → 创建今日笔记 + 从昨天延续未完成任务（`[>]` 标记）
- **项目**: `/project <name>` → 创建项目页面，Dataview 自动汇总相关任务
- **决策**: `/decision-log` → 记录决策（上下文、选项、理由、后果）
- **会议**: `/meeting` → 创建会议笔记（议程、讨论、行动项）
- **复盘**: 通过 zettelkasten 模块的 `/retro` 提取经验教训

### 任务延续协议
| 位置 | 操作 |
|------|------|
| 前一天笔记 | `- [ ]` → `- [>]` + ` ➡️ [[Work/YYYY/YYYY-MM-DD]]` |
| 子任务 | `- [ ]` → `- [>]`（不加链接，父级已标记） |
| 新一天笔记 | `## 🔄 Carryover` 区域 + 来源归因 |

## 配置位置
| 组件 | 位置 |
|------|------|
| 命令定义 | `.claude/commands/{daily,project,decision-log,meeting}.md` |
| 日记模板 | `Templates/Work Daily.md` |
| 项目模板 | `Templates/Work Project.md` |
| 仪表盘 | `Work/Work Dashboard.md` |
| 仪表盘备份 | `Templates/Work Dashboard.md` |

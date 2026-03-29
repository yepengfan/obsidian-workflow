---
module: learning
label: "Learning 结构化学习"
type: knowledge
status: active
enabled: true
created: 2026-03-29
updated: 2026-03-29
depends_on: [zettelkasten]
commands: [learning-init, learning-log, learning-review]
templates: [Templates/Learning Plan.md, Templates/Learning Week.md]
scripts: []
hooks: []
folders: [Learning/, Learning/Books/, Learning/Training/]
config_files:
  - .claude/commands/learning/learning-init.md
  - .claude/commands/learning/learning-log.md
  - .claude/commands/learning/learning-review.md
tags: [system/module]
---

# Learning 结构化学习

## Overview
结构化学习计划系统。每个计划有 4-5 字母代码（如 AISA, SYSD），包含目标、阶段、周记、项目。

## 架构

```
Learning/
└── <CODE>/                 # 每个学习计划一个文件夹
    ├── 00_plan.md          # 目标、阶段、时间线、资源
    ├── 00_map.md           # 概念图、技术雷达
    ├── Weeks/
    │   └── YYYY-WXX.md    # 周记（目标、完成、洞察、阻力）
    ├── Courses/            # 课程笔记
    ├── Projects/           # 项目 POC
    └── Attachments/        # 计划专属媒体
```

### 数据流
- **初始化**: `/learning-init <plan-name>` → 创建完整文件夹结构 + 计划模板
- **周记**: `/learning-log <CODE>` → 从 00_plan.md 预填当前阶段目标
- **复盘**: `/learning-review <CODE>` → 对齐检查 + zettel 候选 + 下周调整
- **输出**: 学习洞察 → Zettelkasten（通过 `/zettel`）

### 活跃计划
| 代码 | 名称 | 阶段 | 状态 |
|------|------|------|------|
| AISA | AI Solutions Architect | Phase 2 | 进行中 |
| SYSD | System Design | - | 待启动 |

## 配置位置
| 组件 | 位置 |
|------|------|
| 命令定义 | `.claude/commands/learning/{learning-init,learning-log,learning-review}.md` |
| 计划模板 | `Templates/Learning Plan.md` |
| 周记模板 | `Templates/Learning Week.md` |

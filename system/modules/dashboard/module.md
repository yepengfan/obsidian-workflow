---
module: dashboard
label: "Dashboard 仪表盘"
type: utility
status: active
enabled: true
created: 2026-03-29
updated: 2026-03-29
depends_on: []
commands: []
templates: [Templates/Home.md, Templates/Work Dashboard.md, Templates/Work Weekly View.md, Templates/Work Monthly View.md]
scripts: []
hooks: []
folders: []
config_files: []
tags: [system/module]
---

# Dashboard 仪表盘

## Overview
Vault 的 UI 层。Home.md 是主入口，通过 Dataviewjs 实现标签页导航、按钮交互、雷达图可视化。Work Dashboard / Weekly View / Monthly View 是工作子仪表盘。

## 架构

```
Home.md                          # 主仪表盘（Homepage 插件落地页）
├── [Work | Profile | Skills]    # 主标签组
│   ├── Work → 工作入口 + 日记按钮 + 任务工具栏
│   ├── Profile → Baseball Card 雷达图（全息效果）
│   └── Skills → 技能雷达可视化
└── [AI Digest | GitHub Trending] # Feed 标签组
    ├── AI Digest → 最新摘要预览
    └── GitHub Trending → 最新趋势预览

Work/Work Dashboard.md           # 工作仪表盘（任务 × 项目 × 状态）
Work/Weekly View.md              # 周视图
Work/Monthly View.md             # 月视图
```

### UI 模式
- **Tab Factory**: `createTabGroup(dv, tabs, defaultId)` — 通用标签页生成器
- **Pill/Segment 风格**: 药丸按钮切换面板
- **CMS 模式**: 笔记创建按钮直接嵌入仪表盘（无需弹窗）
- **Task Toolbar**: 项目选择器 + 优先级 emoji 按钮（🔴🟠🟡🟢）+ 排序

### 设计决策日志
修改仪表盘时，必须同步更新对应的 `Templates/Work *.md` 备份文件，并在 Design Decisions 区域追加新的 `> [!note]` 条目。

## 配置位置
| 组件 | 位置 |
|------|------|
| Home.md 源码 | `Home.md`（Dataviewjs） |
| Home.md 备份 | `Templates/Home.md` |
| Work Dashboard | `Work/Work Dashboard.md` |
| Dashboard 备份 | `Templates/Work Dashboard.md` |
| Weekly 备份 | `Templates/Work Weekly View.md` |
| Monthly 备份 | `Templates/Work Monthly View.md` |

---
module: dashboard
label: "Dashboard 仪表盘"
type: utility
status: active
enabled: true
created: 2026-03-29
updated: 2026-11-17
depends_on: []
requires:
  plugins: [dataview, homepage]
commands: []
templates: [Templates/Home.md, Templates/Work Dashboard.md, Templates/Work Weekly View.md, Templates/Work Monthly View.md]
scripts: [scripts/dashboard/home/view.js, scripts/dashboard/home/view.css]
hooks: []
folders: []
config_files: []
tags: [system/module]
---

# Dashboard 仪表盘

## Overview
Home 是精简仪表盘与功能入口。模块卡片展示图标、真实统计与迷你图表，每张卡片链接到模块自己的完整仪表盘。Feeds 不在 Home 展示，管线与历史资料保持独立。

## 架构
- `Home.md` 调用 `scripts/dashboard/home/view.js`，样式在同目录 `view.css`。
- 日常：Practice Review、Task Board、Journal。
- 学习：Learning、Books、Algorithm、System Design、Frontend。
- 知识与工作：Zettelkasten、Articles、Essays、Work、Brownbag、Profile。
- `scripts/dashboard/<module>/view.js` 承接完整内容。首页不渲染详细图表、任务编辑表单或整套书架。
- Journal 完整仪表盘为 `Journal/Dashboard.md`，Profile 为 `Profile/Dashboard.md`，文章聚合为 `Library/Articles.md`。
- 其他仪表盘沿用原有索引路径。任务源仍为私有 `Tasks/Board.md`，共享 UI 在 `scripts/dashboard/tasks/view.js`。

## Quick Start
打开 [[Home]] 看模块摘要，点击卡片的仪表盘进入完整视图。通过 [[system/registry|Registry]] 管理模块启停；停用模块在首页显示暂停状态。

## 维护
Home 结构变化时同步 `Templates/Home.md`；任务视图变化时同步 `Templates/Task Board.md`。私人记录仍通过 vault sync 同步，不加入 Git。

## 验证
`node --test scripts/dashboard/home/view.test.cjs scripts/journal/view.test.cjs scripts/test_home_task_drag.cjs`

---
module: journal
label: "Journal 日常记录与回顾"
type: utility
status: active
enabled: true
created: 2026-11-09
updated: 2026-11-09
depends_on: [dashboard]
requires:
  plugins: [dataview, chatting-with-ai]
commands: [journal-review]
templates: [Templates/Journal Daily.md, Templates/Journal Review.md]
scripts: [scripts/journal/view.js]
hooks: []
folders: [Journal/]
config_files: [Journal/Guide.md]
tags: [system/module]
---

# Journal 日常记录与回顾

## Overview
每天使用相同的 AAR 流程回看、记录、反思并保存。工作和生活均可，无独立 weekly 模式。完整指引的唯一正文是 [[Journal/Guide]]。

## 架构
- 首页 `dv.view("scripts/journal", { app })` 显示近 7 天日期按钮、折叠待回看，以及累计/本月/近 7 天记录天数。首页不展开记录或回顾内容。今天按钮采用独立标签、加粗日期和静态淡色外圈高亮；打卡圆点仍仅代表已保存内容。
- `Templates/Journal Daily.md` 初始化 `Journal/Daily/YYYY-MM-DD.md`；`Templates/Journal Review.md` 初始化 `Journal/Review.md`。已有文件永不覆盖初始化。
- AI 根据 Guide 写 daily、滚动回顾及原事件的待回看 checklist。Home 监听数据文件变动，自动重算视图；AI 不改首页代码。
- `Journal/Daily/` 和 `Journal/Review.md` 由现有 vault 同步服务同步，gitignore 保护；不随 PR 发布私人记录。

## Quick Start
1. 在手机或电脑启用并登录 Chatting with AI（ChatGPT account 或已有 API 配置均可）。
2. 首页 Journal 点击今天的日期按钮（如 `今天 · 11/09`），准备当天模板后直接进入 AI；同设备同日优先继续已有会话。已记录的过去日期打开原笔记，空白过去日期不提供手动打卡。
3. 跟着固定流程聊天，说“今天到这”后 AI 保存并更新回顾/待回看事项，核对后报告结果。
4. 电脑也可 `/journal-review`，遵循同一 Guide。笔记可直接手写，空模板不计入记录天数。
5. 日期以设备本地时区为准，午夜、回前台及窗口聚焦时刷新；点击今天按钮时再次读取当前日期，避免页面休眠跨午夜后写错文件。

## 配置位置
| 内容 | 位置 |
|---|---|
| 权威流程 | `Journal/Guide.md` |
| 电脑 skill | `.agents/skills/journal-review/SKILL.md` |
| 首页与统计 | `scripts/journal/view.js` |
| 模板 | `Templates/Journal Daily.md`、`Templates/Journal Review.md` |
| 数据 | `Journal/Daily/`、`Journal/Review.md`（gitignore） |

## 插件兼容与恢复
Chatting with AI 0.12.0 的内部 `openChat`、视图 `newChat` / `sendMessage` / `openConversation` 用于启动与续接。调用前检查能力，升级后需复验，不修改插件 bundle。会话 ID 仅保存在本设备 localStorage / 内存，不同步凭据。会话丢失时从已保存笔记继续新对话；接口变化或未登录时保留模板并显示可复制启动指令和笔记入口。

锁屏不保证 AI 继续运行；多文件 AI 保存不是原子事务。Guide 要求写前重读、局部更新、重试去重和写后核对。它是操作指引，不是权限隔离；跨设备同步完成与否需要实际验证。

## 验证
- 自动化：`node --test scripts/journal/view.test.cjs`。
- PoC：2026-11-09 用户已确认手机首页触发 Chatting with AI 可用。
- 正式端到端：需验证保存后的 daily / Review / checklist 与跨设备同步；电脑 UI 自动化未获权限，不能以代码检查代替实际 UI 验收。

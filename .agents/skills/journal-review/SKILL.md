---
name: journal-review
description: >-
  引导每天的 journal 对话：回看之前、记录今天、AAR 反思、保存并维护滚动回顾与待回看事件。Use for /journal-review.
disable-model-invocation: true
---

<!-- module: journal -->
> [!GUARD] Read `system/modules/journal/module.md`. If `enabled: false`, reply "⛔ Module **journal** is disabled. Enable it via `/module-toggle journal`." and STOP.

读取 `Journal/Guide.md`，依照其中固定的每日流程执行。不要复制另一套流程，也没有 weekly 模式。

- 新篇按 Guide 使用 `Journal/Daily/YYYY-MM-DD-timestamp.md`，timestamp 为 Unix 毫秒时间戳。每篇一个话题，同日多篇独立保存，不按日期选择旧文件追加。继续原篇需有明确目标路径，按模板仅初始化缺失文件，禁止覆盖初始化。
- 如果入口已经提供日期、目标文件和 session 标识，沿用它们；跨午夜的已有会话保持原日期。没有 session 时生成本次唯一标识。
- 只查找 Journal 范围的记录。目录可能被 gitignore，使用 shell 目录枚举或工具的 vault 文件列表，不依赖默认 rg / glob 结果。
- 从“回看之前”开始对话；收到“今天到这”等结束信号就按 Guide 保存、读回、汇报。只允许修改涉及的 Journal 数据笔记；Guide、模板和 Home 是运行时只读资料。

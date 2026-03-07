# Zettelkasten TODO

## 2. Inbox 处理流程 ✅

**目标：** 设计周回顾工作流，把 inbox 笔记高效转化为 zettel 或删除。

**完成：** `/inbox-review` 命令已创建，README 和 CLAUDE.md 已更新。
- 逐条处理，支持转 zettel / 归档 / 跳过
- 归档到 `Inbox/archive/YYYY-MM/`，不删除原文

---

## 3. Zettel 质量提升

**目标：** 把现有 seedling zettel 逐步升级，补充跨书目连接。

### 待做
- [x] 补充 Related 连接：517 个跨书目连接已自动写入，共更新 1034 次文件
- [x] Status 升级：246 个 zettel 升级为 `growing`（2+ 连接），7 个保持 `seedling`
- [ ] `evergreen` 升级：手动标记，标准为跨多个领域且内容经过深度消化

---

## 4. Learning Workflow

**目标：** 实现结构化学习计划工作流（见 `Learning/learning-plan-obsidian-workflow.md`）。

### 已完成
- [x] `/learning-init` 命令
- [x] `/learning-log` 命令
- [x] `/learning-review` 命令
- [x] `/project-retro` 命令
- [x] Templates: `Learning Plan.md`, `Learning Week.md`
- [x] Home.md Learning section (active plans + weekly log status)
- [x] Training/ 文件迁移至 `Learning/AI-SA/`
- [x] CLAUDE.md, README.md, sortspec.md 更新

### 待做
- [x] 为 AI-SA plan 创建 `00_plan.md`（运行 `/learning-init AI-SA`）
- [x] 将 `ai-sa-stage12-detail-v5.md` 和 `ai-sa-stage34-detail-v5.md` 整合进 `00_plan.md` 的阶段划分

---

> [!note] 完成后
> 所有任务完成后，review 并归档或删除此文件。

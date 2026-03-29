---
tags: [system]
created: 2026-03-29
updated: 2026-03-29
---

# Vault Module System

> [!abstract] 目的
> 将 vault 的所有功能模块化管理，避免随着功能增加变成意大利面。
> 每个功能是一个 **module**，有标准化清单，统一在 [[system/registry]] 查看。

## 核心概念

### Module = 功能单元

每个 module 是 vault 里一个独立的功能（如 Zettelkasten、AI Digest、Work System）。
每个 module 有一个 `.md` 文件，用 frontmatter 描述它的元数据：

| 字段 | 说明 | 示例 |
|------|------|------|
| `module` | 唯一标识符 | `zettelkasten` |
| `label` | 显示名称 | `Zettelkasten 永久笔记` |
| `type` | 类型分类 | `knowledge` / `work` / `feed` / `utility` / `profile` |
| `status` | 运行状态 | `active` / `inactive` / `deprecated` |
| `enabled` | 模块开关 | `true` / `false` |
| `depends_on` | 依赖的其他模块 | `[inbox]` |
| `commands` | 关联的 slash 命令 | `[zettel, retro, backlink]` |
| `templates` | 使用的模板 | `[Templates/Zettel.md]` |
| `scripts` | 关联脚本 | `[scripts/ai-digest/run.sh]` |
| `hooks` | 自动化 hooks | `[upgrade-zettel-status]` |
| `folders` | 管理的文件夹 | `[Zettelkasten/]` |

### Registry = 控制中心

[[system/registry]] 用 Dataview 自动汇总所有 module，提供：
- 📊 全局状态总览（active / inactive / deprecated）
- 🔗 依赖关系图
- 📋 命令 × 模块映射
- ⚠️ 健康检查（缺失模板、断链等）

## 模块开关

> [!tip] 用 `/module-toggle <name>` 切换模块的启停状态

每个 module 的 `enabled` 字段控制启停：

| `enabled` | 效果 |
|-----------|------|
| `true` | 模块正常运行 |
| `false` | 命令拒绝执行、hooks 跳过、管线脚本退出 |

### 三层守卫机制

| 层级 | 机制 | 强度 | 覆盖范围 |
|------|------|------|----------|
| 命令守卫 | 每个命令文件顶部 `[!GUARD]` | 中（AI 执行） | 所有 slash commands |
| 脚本守卫 | Python/Bash 硬编码检查 | 强（代码执行） | hooks、管线 run.sh |
| CLAUDE.md 规则 | 全局声明 | 弱（兜底） | 所有 Claude 交互 |

### 禁用模块时的注意事项
- **检查依赖**：`/module-toggle` 会自动检查并警告依赖关系
- **Shell Commands**：Obsidian 启动时的 AI Digest 由 `run.sh` 内的脚本守卫控制

## 添加新功能的标准流程

> [!tip] 新功能 = 先建清单，再写代码

1. **创建 module 文件** — `system/modules/<name>/module.md`，填写 frontmatter（含 `enabled: true`）
2. **创建命令** — 放在 `.claude/commands/<module>/` 子目录，顶部加模块守卫
3. **实现功能** — 创建模板、脚本等
4. **注册** — module 文件的 frontmatter 就是注册信息，registry 自动识别
5. **更新 CLAUDE.md** — 如果影响 vault 结构，同步更新说明

## 修改现有功能的流程

1. **查 registry** — 确认影响范围（依赖、被依赖）
2. **改代码** — 实现变更
3. **更新 module 文件** — 同步 frontmatter + `updated` 日期
4. **验证** — 检查依赖模块是否受影响

## 文件结构

```
system/
├── README.md              # 本文件 — 模块系统说明
├── registry.md            # Dataview 控制中心仪表盘
└── modules/               # 模块清单（每个功能一个文件夹）
    ├── zettelkasten/module.md
    ├── inbox/module.md
    ├── work/module.md
    ├── learning/module.md
    ├── feeds-ai-digest/module.md
    ├── feeds-github-trending/module.md
    ├── profile/module.md
    ├── brownbag/module.md
    ├── dashboard/module.md
    └── vault-ops/module.md

.claude/commands/           # 命令按模块分子目录
├── zettelkasten/           # zettel, retro, backlink, inbox-review, project-retro
├── work/                   # daily, project, decision-log, meeting
├── learning/               # learning-init, learning-log, learning-review
├── feeds/                  # ai-digest, github-trending
├── brownbag/               # brownbag
├── vault-ops/              # organize, tag-audit, summarize, backup, research
└── module-toggle.md        # 全局命令（不分模块）
```

## 设计原则

1. **轻量** — module 文件只记元数据和要点，不重复文档
2. **机器可读** — frontmatter 可被 Dataview 查询
3. **人类可读** — body 部分用自然语言描述架构
4. **单一职责** — 每个 module 管一件事
5. **显式依赖** — `depends_on` 明确标注，不靠隐式关联
6. **可启停** — `enabled` 字段 + 三层守卫，禁用模块不会意外执行

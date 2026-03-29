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

## 添加新功能的标准流程

> [!tip] 新功能 = 先建清单，再写代码

1. **创建 module 文件** — `system/modules/<name>.md`，填写 frontmatter
2. **实现功能** — 创建命令、模板、脚本等
3. **注册** — module 文件的 frontmatter 就是注册信息，registry 自动识别
4. **更新 CLAUDE.md** — 如果影响 vault 结构，同步更新说明

## 修改现有功能的流程

1. **查 registry** — 确认影响范围（依赖、被依赖）
2. **改代码** — 实现变更
3. **更新 module 文件** — 同步 frontmatter + 版本号 + `updated` 日期
4. **验证** — 检查依赖模块是否受影响

## 文件结构

```
system/
├── README.md          # 本文件 — 模块系统说明
├── registry.md        # Dataview 控制中心仪表盘
└── modules/           # 模块清单（每个功能一个文件）
    ├── zettelkasten.md
    ├── inbox.md
    ├── work.md
    ├── learning.md
    ├── feeds-ai-digest.md
    ├── feeds-github-trending.md
    ├── profile.md
    ├── brownbag.md
    ├── dashboard.md
    └── vault-ops.md
```

## 设计原则

1. **轻量** — module 文件只记元数据和要点，不重复文档
2. **机器可读** — frontmatter 可被 Dataview 查询
3. **人类可读** — body 部分用自然语言描述架构
4. **单一职责** — 每个 module 管一件事
5. **显式依赖** — `depends_on` 明确标注，不靠隐式关联

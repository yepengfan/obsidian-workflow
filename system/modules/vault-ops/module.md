---
module: vault-ops
label: "Vault Ops 运维工具"
type: utility
status: active
enabled: true
created: 2026-03-29
updated: 2026-08-03
depends_on: []
requires:
  cli: [claude, git]
commands: [organize, tag-audit, summarize, backup, research, module-toggle]
templates: []
scripts: []
hooks: []
folders: []
config_files:
  - .claude/commands/vault-ops/organize.md
  - .claude/skills/vault-ops-organize/SKILL.md
  - .claude/commands/vault-ops/tag-audit.md
  - .claude/skills/vault-ops-tag-audit/SKILL.md
  - .claude/commands/vault-ops/summarize.md
  - .claude/skills/vault-ops-summarize/SKILL.md
  - .claude/commands/vault-ops/backup.md
  - .claude/skills/vault-ops-backup/SKILL.md
  - .claude/commands/vault-ops/research.md
  - .claude/skills/vault-ops-research/SKILL.md
  - .claude/commands/module-toggle.md
  - .claude/skills/module-toggle/SKILL.md
tags: [system/module]
---

# Vault Ops 运维工具

## Overview
Vault 级别的维护和辅助工具集合。不属于特定领域，为整个 vault 服务。

## 命令清单

| 命令 | 说明 | 影响范围 |
|------|------|----------|
| `/organize [folder]` | 审计文件组织：错位笔记、孤儿、缺失链接、缺失 frontmatter | 指定文件夹或全 vault |
| `/tag-audit [folder]` | 审计标签：统一命名、清理冗余、应用 taxonomy | 指定文件夹或全 vault |
| `/summarize <note\|folder>` | 生成摘要：单条 → 3-5 bullets，文件夹 → 每条一行 | 只读，不修改 |
| `/backup` | Git 同步 + 推送：运行 `~/obsidian-config/sync.sh` | Git 仓库 |
| `/research <topic>` | 网络搜索 → Inbox 结构化笔记 | 创建 Inbox/ 新笔记 |

## Quick Start

按需使用，无需日常流程：
- **整理检查** → `/vault-ops/organize` — 扫描文件组织问题（错位笔记、孤儿文件、缺失链接）
- **标签审计** → `/vault-ops/tag-audit` — 清理标签命名、统一 taxonomy
- **笔记摘要** → `/vault-ops/summarize <note|folder>` — 快速了解笔记/文件夹内容概览
- **备份** → `/vault-ops/backup` — Git 同步 + 推送
- **网络调研** → `/vault-ops/research <topic>` — 搜索 → 结构化笔记存入 Inbox/

### 核心原则
- `/organize` 和 `/tag-audit` 只报告，不自动修改（需确认）
- `/summarize` 是只读操作
- `/backup` 调用外部同步脚本
- `/research` 创建新笔记到 Inbox/

## 配置位置
| 组件 | 位置 |
|------|------|
| 命令定义 | `.claude/commands/vault-ops/{organize,tag-audit,summarize,backup,research}.md` |
| 备份脚本 | `~/obsidian-config/sync.sh`（vault 外部） |

---
🏠 [[Home]] · 📊 [[system/registry|Registry]] · 🚀 [[GETTING_STARTED|Getting Started]]

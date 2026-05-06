# Algorithm Module — Design Spec

> Date: 2026-05-07
> Status: Approved
> Module: `algorithm`
> Location: `Learning/Algorithm/`

---

## 1. Overview

将 LeetCode 算法练习工作流从 Claude AI Projects 迁移到 Obsidian vault。核心价值：

- **交互式解题引导**：Claude 引导用户思考，不直接给代码
- **Pattern Card 沉淀**：每个模式独立文件，frontmatter 驱动 Dataview
- **每日 Log 追踪**：记录解题历程，方便回顾和统计

## 2. Folder Structure

```
Learning/Algorithm/
├── 00_index.md                    # Dataview dashboard
├── CLAUDE.md                      # Module-level Claude instructions
├── Patterns/
│   ├── Monotonic Stack — 132 Pattern.md
│   ├── Postorder Tree DP.md
│   ├── Binary Tree LCA.md
│   └── ...                        # 一个 pattern 一个文件
├── Log/
│   ├── 2026-05-07.md
│   └── ...                        # 每日一条
└── Legacy/                        # 迁移完成后可归档
    ├── PROJECT_META.md
    ├── README.md
    ├── arrays_sequences.md
    ├── binary_trees_recursion.md
    ├── binary_trees_traversal.md
    ├── bsts.md
    ├── data_structures.md
    ├── dp.md
    ├── graphs.md
    └── linked_lists.md
```

## 3. Pattern Card Schema

### 3.1 Frontmatter

```yaml
---
id: 14                              # 全局唯一递增编号
title: "DFS Parameter Passing"
category: "Binary Tree"              # 大类，Dataview 分组键
tags: [leetcode/pattern, leetcode/tree, leetcode/dfs]
problems: [1372, 129, 1448]          # LC 题号列表（纯数字，Dataview 可查询）
difficulty: medium                   # pattern 理解难度 (easy/medium/hard)
confidence: 3                        # 1-5 自评掌握程度
created: 2026-05-07
updated: 2026-05-07
---
```

### 3.2 Body Structure

```markdown
# {title} — {subtitle}

## Key Insight
1-2 句核心思想。

## Trigger
识别信号：什么时候应该想到这个 pattern。（可选，不是所有 pattern 都有）

## Template
\```python
# 代码模板
\```

## Problems
| # | Name | Difficulty | Date |
|---|------|-----------|------|
| 1372 | Longest ZigZag Path | Medium | 2026-04-15 |

## Gotchas
- 常见陷阱和注意事项
```

### 3.3 Category Values

从 Legacy 数据提取的 8 个大类：

| Category | Legacy File | Card Count |
|----------|------------|------------|
| Array | arrays_sequences.md | 4 (#1-4) |
| Linked List | linked_lists.md | 5 (#5-9) |
| Binary Tree — Traversal | binary_trees_traversal.md | 5 (#10-14) |
| Binary Tree — Recursion | binary_trees_recursion.md | 5 (#15-19) |
| BST | bsts.md | 4 (#20-23) |
| Graph | graphs.md | 3 (#24-26) |
| DP | dp.md | 2 (#27-28) |
| Data Structure | data_structures.md | 2 (#29-30) |

## 4. Log Schema

### 4.1 Frontmatter

```yaml
---
date: 2026-05-07
problems_solved: [543, 124]
tags: [leetcode/log]
---
```

### 4.2 Body Structure

```markdown
# {YYYY-MM-DD}

## LC {number} — {name}
- **Pattern**: [[{pattern name}]]
- **Difficulty**: {Easy/Medium/Hard}
- **Result**: ✅ 一次通过 / ⚠️ 需要提示 / ❌ 看了答案
- **Notes**: 关键收获或犯的错误
- **Time**: O(?), Space: O(?)
```

`problems_solved` 数组支持 Dataview 统计每日/每周做题量。

## 5. Commands

### 5.1 `/algorithm/solve` — 日常解题（主命令）

**输入**: 题号（如 `543`）或题目描述

**阶段流程**:

```
用户给题号 → Claude 引导解题（hints/pseudocode）
           → 用户描述思路 → Claude 评估补充
           → 用户贴代码 → Claude 审核
           → 通过 → 沉淀 pattern card + 写 log
```

**阶段 1 — 引导解题（Socratic）**
- 给 conceptual hints 和 pseudocode，不给完整代码
- 引导用户找到关键 insight
- 用户明确表达思路后进入下一阶段

**阶段 2 — 代码审核**
- 审核：正确性、edge cases、时间/空间复杂度
- Bug → 指出具体行和原因，不重写
- 与最优解比较（概念优先，代码仅在用户要求时给出）

**阶段 3 — 沉淀**
- 判断该题属于哪个已有 pattern 或需要新建
- **已有 pattern**: frontmatter `problems[]` 加题号 + 正文 Problems 表格加一行 + 更新 `updated` 日期
- **新 pattern**: 用模板创建新 `.md` 文件，填充所有字段，id 自动递增
- 写一条 Log entry 到 `Log/YYYY-MM-DD.md`（不存在则创建）

### 5.2 `/algorithm/review` — 回顾复习

**功能**: 列出需要复习的 patterns

**排序策略**:
1. `confidence` 从低到高（薄弱优先）
2. 同 confidence 按 `updated` 从旧到新（最久没碰优先）

**输出**: 表格展示 pattern 名、category、confidence、上次更新时间，附 wikilink 可直接跳转。

### 5.3 `/algorithm/migrate` — 一次性迁移

**功能**: 将 Legacy/ 下的 8 个 category 文件拆分为独立 pattern card 文件

**步骤**:
1. 读 Legacy/ 下 8 个 category `.md` 文件
2. 按 `##` heading 分割出每个 pattern card
3. 提取字段：id（统一重编号 1-30）、title、category、problems（正则提取 LC 数字）、Key Insight、Trigger、Template、Gotchas
4. 为每个 card 生成 frontmatter + 标准化 body
5. 写入 `Patterns/{title}.md`
6. 通用心法 + 待做清单 → 写入 `00_index.md`
7. 修正已知编号错位问题（PROJECT_META 中记录的）
8. Legacy/ 保留不删除

## 6. 00_index.md — Dashboard

Dataview 驱动的总览：

```markdown
# Algorithm Pattern Library

## 📊 Stats
<!-- dataviewjs: 总 pattern 数 / 总做题数 / 本周做题数 / 本月做题数 -->

## 🗂 Patterns by Category
<!-- dataview: TABLE 按 category 分组，列出 pattern、problems 数、confidence -->

## 🔴 Low Confidence (需要复习)
<!-- dataview: TABLE where confidence <= 2 -->

## 📝 待做清单
- LC 503 — Next Greater Element II
- LC 84 — Largest Rectangle in Histogram
- ...

## 🧠 通用心法

### 模式识别框架
1. 暴力怎么做? 估算复杂度,看哪里可以优化
2. 能否降维? 固定一端,把多变量问题变两变量
3. 数据结构匹配 — 是否需要快速 min/max、连通性、有序性
4. 从约束出发 — n≤20 想 bitmask;n≤40 想 meet in the middle;n≤10⁵ 想 O(n log n)

### 核心原则
- BST inorder = 有序序列
- 遍历选择：inorder (BST 排序), preorder (自顶向下), postorder (自底向上)
- 递归 DFS 返回值语义：参数携带 per-call 状态；共享答案用 nonlocal
- ...

### Python 陷阱
- `[[0]*n]*m` 共享 row 引用
- class vars 在测试间泄漏
- `arr[-1]` 静默负索引
- ...
```

## 7. CLAUDE.md — Module Instructions

```markdown
# Algorithm Module — Claude Code Instructions

> 继承 vault root CLAUDE.md 的通用约定。

## Solving Flow

1. 用户给题号 → 给 hints 和 pseudocode，**不给完整代码**
2. 即使用户分享了思路，仍然给 pseudocode 而非代码
3. 只在用户明确说 "show me the code" / "给我看代码" / "我放弃" 时给完整代码
4. "how would you do it" 之类模糊请求 → pseudocode
5. 用户贴代码 → 审核正确性、edge cases、复杂度
6. Bug fixing → 指出具体行，targeted fix，不重写
7. 通过后 → 沉淀 pattern card + 写 log

## Pattern Card Rules

- 已有 pattern: 加题号到 frontmatter `problems[]` + 正文 Problems 表格 + 更新 `updated`
- 新 pattern: 创建新文件，id 取当前最大值 +1，填充所有字段
- `confidence` 由用户自评，Claude 可建议但不自行修改
- `difficulty` 指 pattern 理解难度，非单题难度
- 文件名 = pattern title（去掉特殊字符）

## Log Rules

- 每道题一个 `##` section
- 包含 pattern wikilink、difficulty、result、notes、complexity
- `problems_solved` frontmatter 数组与正文 sections 保持一致

## Language

- 技术讨论默认英文，用户用中文则中文回复
- 代码始终 Python 3，clean and readable
- 中英混排时遵循 vault 现有风格

## Do NOT

- 不要主动给完整代码（除非用户明确要求）
- 不要重写用户代码（targeted fix only）
- 不要自行修改 confidence 值
- 不要删除 Legacy/ 文件夹
```

## 8. Module Manifest

```yaml
# system/modules/algorithm/module.md
---
module: algorithm
label: "Algorithm 算法练习"
type: knowledge
status: active
enabled: true
created: 2026-05-07
updated: 2026-05-07
depends_on: []
requires:
  cli: [claude]
  plugins: [dataview]
commands: [solve, review, migrate]
templates: [Templates/Algorithm Pattern.md, Templates/Algorithm Log.md]
scripts: []
hooks: []
folders: [Learning/Algorithm/, Learning/Algorithm/Patterns/, Learning/Algorithm/Log/]
config_files:
  - .claude/commands/algorithm/solve.md
  - .claude/commands/algorithm/review.md
  - .claude/commands/algorithm/migrate.md
  - Learning/Algorithm/CLAUDE.md
tags: [system/module]
---
```

## 9. Templates

### 9.1 Algorithm Pattern Template

用于 `/algorithm/solve` 创建新 pattern card。

### 9.2 Algorithm Log Template

用于 `/algorithm/solve` 创建每日 log entry。

## 10. Migration Plan

一次性迁移 Legacy/ → Patterns/：

1. 读 8 个 category 文件 + README.md + PROJECT_META.md
2. 按 `##` heading 分割 30 个 pattern cards
3. 统一重编号 1-30（修正已知编号错位）
4. 提取 problems LC 数字 → frontmatter `problems[]`
5. 推断 difficulty（基于 problems 的 LC 难度分布）
6. confidence 默认 3（用户后续自评调整）
7. 生成标准化 Patterns/ 文件
8. 通用心法 + 待做清单 + 学习目标 → 00_index.md
9. Legacy/ 保留作为参考

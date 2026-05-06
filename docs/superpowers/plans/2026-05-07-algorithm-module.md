# Algorithm Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Algorithm module — an interactive LeetCode solving workflow with pattern card persistence and Dataview-powered dashboard in Obsidian.

**Architecture:** Independent module under `Learning/Algorithm/` with Claude commands for solve/review/migrate. Pattern cards are individual markdown files with rich frontmatter. A one-time migration converts 30 legacy cards from 8 category files into the new format.

**Tech Stack:** Obsidian, Dataview plugin, Claude Code commands (markdown), YAML frontmatter

**Spec:** `docs/superpowers/specs/2026-05-07-algorithm-module-design.md`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `system/modules/algorithm/module.md` | Module manifest (registry entry) |
| Create | `Templates/Algorithm Pattern.md` | Pattern card template for new cards |
| Create | `Templates/Algorithm Log.md` | Daily log entry template |
| Create | `Learning/Algorithm/CLAUDE.md` | Module-level Claude instructions |
| Create | `.claude/commands/algorithm/solve.md` | `/algorithm/solve` command |
| Create | `.claude/commands/algorithm/review.md` | `/algorithm/review` command |
| Create | `.claude/commands/algorithm/migrate.md` | `/algorithm/migrate` command |
| Create | `Learning/Algorithm/00_index.md` | Dataview dashboard |
| Generate | `Learning/Algorithm/Patterns/*.md` (×30) | Migration output — one per pattern |
| Existing | `Learning/Algorithm/Legacy/*.md` (×10) | Source data for migration |

---

### Task 1: Module Manifest

**Files:**
- Create: `system/modules/algorithm/module.md`

- [ ] **Step 1: Create module manifest**

```markdown
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

## Overview

LeetCode 算法练习模块。交互式解题引导 → 代码审核 → Pattern Card 沉淀。

## 架构

- **Patterns/**: 一个 pattern 一个文件，frontmatter 驱动 Dataview
- **Log/**: 每日解题记录
- **Legacy/**: 迁移前的原始文件（只读参考）

### 数据流

- **输入**: `/algorithm/solve <LC#>` → 引导解题 → 代码审核 → 沉淀 card + log
- **回顾**: `/algorithm/review` → 按 confidence 排序展示薄弱 patterns
- **迁移**: `/algorithm/migrate` → Legacy/ → Patterns/ 一次性转换

## Quick Start

1. `/algorithm/solve 543` — 开始解题
2. `/algorithm/review` — 复习薄弱 pattern
3. `/algorithm/migrate` — 迁移旧数据（仅需运行一次）
```

- [ ] **Step 2: Create directory**

Run: `mkdir -p system/modules/algorithm`

- [ ] **Step 3: Write file and verify**

Write the file to `system/modules/algorithm/module.md`, then verify:

Run: `head -5 system/modules/algorithm/module.md`

Expected: frontmatter starts with `---` and contains `module: algorithm`

- [ ] **Step 4: Commit**

```bash
git add system/modules/algorithm/module.md
git commit -m "feat(algorithm): add module manifest"
```

---

### Task 2: Templates

**Files:**
- Create: `Templates/Algorithm Pattern.md`
- Create: `Templates/Algorithm Log.md`

- [ ] **Step 1: Create Pattern Card template**

```markdown
---
id: {{id}}
title: "{{title}}"
category: "{{category}}"
tags: [leetcode/pattern]
problems: []
difficulty: medium
confidence: 3
created: {{date}}
updated: {{date}}
---

# {{title}}

## Key Insight



## Trigger



## Template

```python

```

## Problems

| # | Name | Difficulty | Date |
|---|------|-----------|------|

## Gotchas

-
```

Write to `Templates/Algorithm Pattern.md`.

- [ ] **Step 2: Create Log Entry template**

```markdown
---
date: {{date}}
problems_solved: []
tags: [leetcode/log]
---

# {{date}}

## LC {{number}} — {{name}}
- **Pattern**: [[{{pattern}}]]
- **Difficulty**: {{difficulty}}
- **Result**: ✅ / ⚠️ / ❌
- **Notes**:
- **Time**: O(?), Space: O(?)
```

Write to `Templates/Algorithm Log.md`.

- [ ] **Step 3: Verify both templates exist**

Run: `ls -la Templates/Algorithm*.md`

Expected: two files listed

- [ ] **Step 4: Commit**

```bash
git add "Templates/Algorithm Pattern.md" "Templates/Algorithm Log.md"
git commit -m "feat(algorithm): add pattern card and log templates"
```

---

### Task 3: Module CLAUDE.md

**Files:**
- Create: `Learning/Algorithm/CLAUDE.md`

- [ ] **Step 1: Write CLAUDE.md**

Source: spec §7 — adapted from Legacy `PROJECT_META.md` instructions.

```markdown
# Algorithm Module — Claude Code Instructions

> 继承 vault root CLAUDE.md 的通用约定。

## Directory Configuration

| Path | Purpose |
|------|---------|
| `Learning/Algorithm/Patterns/` | Pattern card 文件（一个 pattern 一个 .md） |
| `Learning/Algorithm/Log/` | 每日解题记录 |
| `Learning/Algorithm/Legacy/` | 迁移前原始文件（只读参考） |
| `Learning/Algorithm/00_index.md` | Dataview dashboard |
| `Templates/Algorithm Pattern.md` | 新 card 模板 |
| `Templates/Algorithm Log.md` | 新 log 模板 |

## Solving Flow

1. 用户给题号 → 给 hints 和 pseudocode，**不给完整代码**
2. 即使用户分享了思路，仍然给 pseudocode 而非代码
3. 只在用户明确说 "show me the code" / "给我看代码" / "我放弃" 时给完整代码
4. "how would you do it" 之类模糊请求 → pseudocode
5. 用户贴代码 → 审核正确性、edge cases、复杂度
6. Bug fixing → 指出具体行，targeted fix，不重写
7. 通过后 → 沉淀 pattern card + 写 log

## Pattern Card Rules

- **已有 pattern**: 加题号到 frontmatter `problems[]` + 正文 Problems 表格加一行 + 更新 `updated` 日期
- **新 pattern**: 创建新文件（用 `Templates/Algorithm Pattern.md`），id 取当前最大值 +1，填充所有字段
- `confidence` 由用户自评，Claude 可建议但不自行修改
- `difficulty` 指 pattern 理解难度，非单题难度
- 文件名 = pattern title（去掉文件系统非法字符 `/ \ : * ? " < > |`）
- `tags` 格式: `[leetcode/pattern, leetcode/{category-slug}]`

## Log Rules

- 每道题一个 `##` section
- 包含 pattern wikilink `[[pattern name]]`、difficulty、result emoji、notes、complexity
- frontmatter `problems_solved` 数组与正文 sections 保持一致
- 文件名: `YYYY-MM-DD.md`
- 如果当天 log 已存在，追加新 section（不覆盖）

## Category Values

合法 category 值（与 Dataview 分组键一致）:

- Array
- Linked List
- Binary Tree — Traversal
- Binary Tree — Recursion
- BST
- Graph
- DP
- Data Structure

新 category 可按需添加，但优先归入已有类别。

## Language

- 技术讨论默认英文，用户用中文则中文回复
- 代码始终 Python 3，clean and readable
- 中英混排时遵循 vault 现有风格

## Do NOT

- 不要主动给完整代码（除非用户明确要求）
- 不要重写用户代码（targeted fix only）
- 不要自行修改 confidence 值
- 不要删除或修改 Legacy/ 文件
```

Write to `Learning/Algorithm/CLAUDE.md`.

- [ ] **Step 2: Verify**

Run: `head -3 Learning/Algorithm/CLAUDE.md`

Expected: `# Algorithm Module — Claude Code Instructions`

- [ ] **Step 3: Commit**

```bash
git add Learning/Algorithm/CLAUDE.md
git commit -m "feat(algorithm): add module CLAUDE.md instructions"
```

---

### Task 4: `/algorithm/solve` Command

**Files:**
- Create: `.claude/commands/algorithm/solve.md`

- [ ] **Step 1: Create command directory**

Run: `mkdir -p .claude/commands/algorithm`

- [ ] **Step 2: Write solve command**

```markdown
<!-- module: algorithm -->
> [!GUARD] Read `system/modules/algorithm/module.md`. If `enabled: false` → reply "⛔ Module **algorithm** is disabled. Enable it via `/module-toggle algorithm`." and STOP. Do NOT proceed.

Solve LeetCode problem: $ARGUMENTS

Read `Learning/Algorithm/CLAUDE.md` for module instructions.

## Phase 1 — 引导解题

1. 用户提供了题号或题目描述
2. 理解题意，确认约束条件
3. 给 conceptual hints 和 pseudocode，**不给完整代码**
4. 用 targeted questions 引导用户找到关键 insight
5. 用户描述出正确思路后，确认并进入 Phase 2

**引导原则:**
- 先问 "暴力怎么做？复杂度多少？" 引导用户思考优化方向
- 给出模式识别线索（如 "这道题的约束 n ≤ 10⁵ 暗示什么复杂度？"）
- 如果用户卡住超过 2 轮，给更直接的 hint（但仍非代码）
- 只在用户说 "show me the code" / "给我看代码" / "我放弃" 时给完整代码

## Phase 2 — 代码审核

1. 用户贴出自己的代码
2. 审核以下方面:
   - **正确性**: 逻辑是否正确
   - **Edge cases**: 空输入、单元素、最大值、负数等
   - **复杂度**: Time & Space Big-O 分析
   - **代码风格**: Python 3 best practices
3. 如果有 bug → 指出具体行和原因，**不重写**
4. 与最优解比较（概念优先，代码仅在用户要求时给出）
5. 代码通过后进入 Phase 3

## Phase 3 — 沉淀

1. **判断 pattern 归属**:
   - 读取 `Learning/Algorithm/Patterns/` 下所有文件的 frontmatter
   - 判断该题属于哪个已有 pattern，或是否需要新建
   - 告诉用户归类结果，确认后继续

2. **已有 pattern → 更新**:
   - 在 frontmatter `problems` 数组末尾加题号
   - 在正文 Problems 表格加一行（题号、名称、难度、今天日期）
   - 更新 frontmatter `updated` 为今天
   - 如果有新的 Gotcha 发现，追加到 Gotchas section

3. **新 pattern → 创建**:
   - 用 `Templates/Algorithm Pattern.md` 模板
   - `id`: 读取所有现有 card 的 id，取最大值 +1
   - 填充: title, category, tags, problems, Key Insight, Trigger (如适用), Template, Gotchas
   - `difficulty`: 基于 pattern 复杂度评估
   - `confidence`: 询问用户自评 (1-5)

4. **写 Log**:
   - 检查 `Learning/Algorithm/Log/YYYY-MM-DD.md` 是否存在
   - 不存在 → 用 `Templates/Algorithm Log.md` 创建，填充第一条
   - 已存在 → 追加新 `##` section，更新 frontmatter `problems_solved` 数组
   - 包含: pattern wikilink、difficulty、result emoji、notes、complexity
```

Write to `.claude/commands/algorithm/solve.md`.

- [ ] **Step 3: Verify module guard**

Run: `head -3 .claude/commands/algorithm/solve.md`

Expected: first line is `<!-- module: algorithm -->`, followed by GUARD callout

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/algorithm/solve.md
git commit -m "feat(algorithm): add /algorithm/solve command"
```

---

### Task 5: `/algorithm/review` Command

**Files:**
- Create: `.claude/commands/algorithm/review.md`

- [ ] **Step 1: Write review command**

```markdown
<!-- module: algorithm -->
> [!GUARD] Read `system/modules/algorithm/module.md`. If `enabled: false` → reply "⛔ Module **algorithm** is disabled. Enable it via `/module-toggle algorithm`." and STOP. Do NOT proceed.

Review algorithm patterns for revision.

Read `Learning/Algorithm/CLAUDE.md` for module instructions.

## Steps

1. **Scan all patterns**: Read frontmatter of all files in `Learning/Algorithm/Patterns/`

2. **Sort by priority**:
   - Primary: `confidence` ascending (weakest first)
   - Secondary: `updated` ascending (oldest first)

3. **Present review table**:

   Display a markdown table with columns:
   | Pattern | Category | Problems | Confidence | Last Updated |
   |---------|----------|----------|------------|-------------|
   Show all patterns, sorted by priority above. Confidence uses stars: 1=⭐, 2=⭐⭐, etc.

4. **Highlight action items**:
   - 🔴 `confidence ≤ 2`: "需要重点复习"
   - 🟡 `confidence = 3`: "建议巩固"
   - 🟢 `confidence ≥ 4`: "掌握良好"

5. **Offer drill-down**: Ask if user wants to:
   - 复习某个具体 pattern（打开对应 card）
   - 做一道该 pattern 的新题（转到 `/algorithm/solve`）
   - 更新 confidence 评分

6. **Stats summary**:
   - 总 pattern 数
   - 各 confidence 等级分布
   - 最久未更新的 3 个 patterns
   - 本周/本月通过 Log 统计的做题数
```

Write to `.claude/commands/algorithm/review.md`.

- [ ] **Step 2: Verify**

Run: `head -3 .claude/commands/algorithm/review.md`

Expected: module guard present

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/algorithm/review.md
git commit -m "feat(algorithm): add /algorithm/review command"
```

---

### Task 6: `/algorithm/migrate` Command

**Files:**
- Create: `.claude/commands/algorithm/migrate.md`

- [ ] **Step 1: Write migrate command**

```markdown
<!-- module: algorithm -->
> [!GUARD] Read `system/modules/algorithm/module.md`. If `enabled: false` → reply "⛔ Module **algorithm** is disabled. Enable it via `/module-toggle algorithm`." and STOP. Do NOT proceed.

Migrate legacy pattern cards to the new format.

Read `Learning/Algorithm/CLAUDE.md` for module instructions.

## Pre-flight Check

1. Verify `Learning/Algorithm/Legacy/` exists and contains `.md` files
2. Verify `Learning/Algorithm/Patterns/` exists and is empty (or confirm overwrite)
3. Read `Learning/Algorithm/Legacy/README.md` for the authoritative index

## Migration Steps

### Step 1: Read all legacy files

Read the following 8 category files from `Learning/Algorithm/Legacy/`:

| File | Category | Expected Cards |
|------|----------|---------------|
| `arrays_sequences.md` | Array | #1-4 |
| `linked_lists.md` | Linked List | #5-9 |
| `binary_trees_traversal.md` | Binary Tree — Traversal | #10-14 |
| `binary_trees_recursion.md` | Binary Tree — Recursion | #15-19 |
| `bsts.md` | BST | #20-23 |
| `graphs.md` | Graph | #24-26 |
| `dp.md` | DP | #27-28 |
| `data_structures.md` | Data Structure | #29-30 |

### Step 2: Split into individual cards

For each file:
1. Split content by `## {number}.` heading pattern
2. Extract from each card:
   - **id**: Use the authoritative numbering from `README.md` (1-30), NOT the internal file numbering (which has known misalignments per `PROJECT_META.md`)
   - **title**: From the heading, strip the number prefix
   - **category**: From the parent file mapping above
   - **problems**: Regex extract all `LC \d+` patterns → integer array
   - **Key Insight**: Text under `**Key Insight:**`
   - **Trigger**: Text under `**Trigger:**` (if present, otherwise omit section)
   - **Template**: Code block(s) under `**Template**`
   - **Gotchas**: Bullet list under `**Gotchas:**`
   - **Problems detail**: Reconstruct into table format from `**Problems:**` line

### Step 3: Generate frontmatter

For each card, generate:

```yaml
---
id: {authoritative number from README}
title: "{extracted title}"
category: "{category from file mapping}"
tags: [leetcode/pattern, leetcode/{category-slug}]
problems: [{extracted LC numbers}]
difficulty: medium
confidence: 3
created: 2026-05-07
updated: 2026-05-07
---
```

Tag slug mapping:
- Array → `leetcode/array`
- Linked List → `leetcode/linked-list`
- Binary Tree — Traversal → `leetcode/tree`
- Binary Tree — Recursion → `leetcode/tree`
- BST → `leetcode/bst`
- Graph → `leetcode/graph`
- DP → `leetcode/dp`
- Data Structure → `leetcode/data-structure`

### Step 4: Write pattern files

For each card, write to `Learning/Algorithm/Patterns/{title}.md`:
- Frontmatter (from Step 3)
- Body: `# {title}` → Key Insight → Trigger (if any) → Template → Problems table → Gotchas
- File name: title with illegal characters removed (`/ \ : * ? " < > |`)

### Step 5: Build 00_index.md

Read `Learning/Algorithm/Legacy/README.md` and extract:
- **待做清单** → `## 📝 待做清单` section
- **学习目标** → `## 🎯 学习目标` section
- **通用心法** → `## 🧠 通用心法` section (模式识别框架 + 核心原则 + Python 陷阱)

Write `Learning/Algorithm/00_index.md` with Dataview queries + extracted content.

### Step 6: Verify

1. Count files in `Patterns/`: should be 30
2. Spot-check 3 random cards: frontmatter valid, body sections complete
3. Verify no duplicate ids
4. Verify `00_index.md` has all sections

## Post-flight

Report:
- ✅ {N} pattern cards migrated
- 📂 Categories: {list}
- ⚠️ Any issues encountered
- 💡 "Legacy/ files preserved. Archive when ready."
```

Write to `.claude/commands/algorithm/migrate.md`.

- [ ] **Step 2: Verify**

Run: `head -3 .claude/commands/algorithm/migrate.md`

Expected: module guard present

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/algorithm/migrate.md
git commit -m "feat(algorithm): add /algorithm/migrate command"
```

---

### Task 7: Dashboard (00_index.md)

**Files:**
- Create: `Learning/Algorithm/00_index.md`

- [ ] **Step 1: Write dashboard with Dataview queries**

```markdown
---
tags: [leetcode/index]
---

# Algorithm Pattern Library

## 📊 Stats

```dataviewjs
const patterns = dv.pages('"Learning/Algorithm/Patterns"').where(p => p.tags && p.tags.includes("#leetcode/pattern"));
const logs = dv.pages('"Learning/Algorithm/Log"').where(p => p.tags && p.tags.includes("#leetcode/log"));

const totalPatterns = patterns.length;
const totalProblems = patterns.reduce((sum, p) => sum + (p.problems ? p.problems.length : 0), 0);

const today = dv.date("today");
const weekAgo = dv.date("today").minus({ days: 7 });
const monthAgo = dv.date("today").minus({ days: 30 });

const weekProblems = logs.where(l => dv.date(l.date) >= weekAgo).reduce((sum, l) => sum + (l.problems_solved ? l.problems_solved.length : 0), 0);
const monthProblems = logs.where(l => dv.date(l.date) >= monthAgo).reduce((sum, l) => sum + (l.problems_solved ? l.problems_solved.length : 0), 0);

dv.paragraph(`**${totalPatterns}** patterns · **${totalProblems}** problems covered · 本周 **${weekProblems}** 题 · 本月 **${monthProblems}** 题`);
```

## 🗂 Patterns by Category

```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Pattern",
  length(problems) AS "Problems",
  confidence AS "Confidence",
  updated AS "Updated"
FROM "Learning/Algorithm/Patterns"
WHERE contains(tags, "#leetcode/pattern")
SORT category ASC, id ASC
GROUP BY category
```

## 🔴 Low Confidence (需要复习)

```dataview
TABLE WITHOUT ID
  link(file.link, title) AS "Pattern",
  category AS "Category",
  confidence AS "Confidence",
  updated AS "Last Updated"
FROM "Learning/Algorithm/Patterns"
WHERE contains(tags, "#leetcode/pattern") AND confidence <= 2
SORT confidence ASC, updated ASC
```

## 📝 待做清单

- [ ] LC 503 — Next Greater Element II (循环数组 + 单调栈)
- [ ] LC 84 — Largest Rectangle in Histogram
- [ ] LC 82 — Remove Duplicates from Sorted List II
- [ ] LC 814 — Binary Tree Pruning
- [ ] LC 543 — Diameter of Binary Tree (postorder pattern)
- [ ] LC 124 — Max Path Sum (postorder pattern)
- [ ] LC 198 — House Robber (非相邻选择 DP 基础)
- [ ] LC 723 — Candy Crush (行/列内消除 + 重力)
- [ ] LC 48 — Rotate Image (in-place 旋转)
- [ ] Circular DP — Minimum Weight k-Independent Set on Cycle
- [ ] Augmented BST — 子树大小,支持高效 kth 查询

## 🎯 学习目标

- **LIS (Longest Increasing Subsequence)** — path: LC 300 → LC 354 → contest variant
- **Greedy 算法** — 系统训练
- **Circular DP** — 环上独立集等

## 🧠 通用心法

### 模式识别框架
1. **暴力怎么做?** 估算复杂度,看哪里可以优化
2. **能否降维?** 固定一端,把多变量问题变两变量
3. **数据结构匹配** — 是否需要快速 min/max、连通性、有序性
4. **从约束出发** — n≤20 想 bitmask;n≤40 想 meet in the middle;n≤10⁵ 想 O(n log n)

### 核心原则
- **BST inorder = 有序序列** → 任何"相邻 / 排序 / 第 k 小"的操作都先想 inorder
- **遍历选择**: inorder (BST 排序), preorder (自顶向下传播), postorder (自底向上聚合)
- **递归 DFS 返回值语义**: 参数携带 per-call 状态；共享答案用闭包 `nonlocal`,仅当 "经过当前节点的答案" ≠ "传给父节点的值" 时才需要
- **循环复杂度** ≠ 循环次数 — 看循环内部操作
- **`bisect_left/right` 返回 `[0, len(arr)]`** — Python `arr[-1]` 静默返回最后元素,容易 off-by-one
- **网格模拟优先简化几何**: 旋转 + 重力 → 先在原网格做重力,再旋转

### Python 陷阱
- `[[0]*n]*m` 共享 row 引用
- class vars 在测试间泄漏 (用 `nonlocal` 或 instance vars)
- `arr[-1]` 静默负索引
- `is` vs `==` 用于结构相等
- `.sort()` 返回 `None`
- 单帧 `return` 不会停止整个递归
```

Write to `Learning/Algorithm/00_index.md`.

- [ ] **Step 2: Verify Dataview renders**

Open `Learning/Algorithm/00_index.md` in Obsidian and check:
- Stats line shows numbers (not errors)
- Patterns table grouped by category (will be empty until migration)
- Low Confidence table renders (empty is fine)

- [ ] **Step 3: Commit**

```bash
git add Learning/Algorithm/00_index.md
git commit -m "feat(algorithm): add Dataview dashboard"
```

---

### Task 8: Run Migration

**Files:**
- Generate: `Learning/Algorithm/Patterns/*.md` (×30)
- Modify: `Learning/Algorithm/00_index.md` (if migration reveals adjustments)

- [ ] **Step 1: Run `/algorithm/migrate`**

Execute the migrate command. This reads all 8 Legacy category files, splits 30 pattern cards, generates individual `.md` files with frontmatter in `Patterns/`.

- [ ] **Step 2: Verify file count**

Run: `ls Learning/Algorithm/Patterns/*.md | wc -l`

Expected: `30`

- [ ] **Step 3: Spot-check 3 cards**

Pick one from each tier:
- Card #1 (Array): check frontmatter `category: "Array"`, `problems` has LC numbers
- Card #17 (Binary Tree): check `category: "Binary Tree — Recursion"`, body has Template code block
- Card #24 (Graph): check `category: "Graph"`, Gotchas section populated

- [ ] **Step 4: Verify no duplicate ids**

Run: `grep -h "^id:" Learning/Algorithm/Patterns/*.md | sort -t: -k2 -n | uniq -d`

Expected: no output (no duplicates)

- [ ] **Step 5: Open 00_index.md in Obsidian**

Verify Dataview queries now show:
- Stats: 30 patterns, correct problem count
- Patterns grouped by 8 categories
- Low confidence: initially empty (all default to 3)

- [ ] **Step 6: Commit**

```bash
git add Learning/Algorithm/Patterns/
git commit -m "feat(algorithm): migrate 30 pattern cards from legacy format"
```

---

### Task 9: Final Verification + Update CLAUDE.md

**Files:**
- Modify: vault root `CLAUDE.md` (add Algorithm module to docs)

- [ ] **Step 1: Verify complete file tree**

Run: `find Learning/Algorithm -type f -name '*.md' | sort`

Expected structure:
```
Learning/Algorithm/00_index.md
Learning/Algorithm/CLAUDE.md
Learning/Algorithm/Legacy/...          (10 files)
Learning/Algorithm/Log/                (empty dir)
Learning/Algorithm/Patterns/...        (30 files)
```

- [ ] **Step 2: Verify module appears in registry**

Open `system/registry.md` in Obsidian. Confirm `algorithm` module shows with status=active.

- [ ] **Step 3: Test `/algorithm/solve` guard**

Run `/algorithm/solve 1` — should NOT hit the disabled guard (module is enabled).
Verify it enters Phase 1 (asks about the problem, gives hints).

- [ ] **Step 4: Test `/algorithm/review`**

Run `/algorithm/review` — should display table of 30 patterns sorted by confidence.

- [ ] **Step 5: Update vault CLAUDE.md**

Add Algorithm module entry to the Folder Structure section and Key Files section in the vault root `CLAUDE.md`.

Folder Structure addition under `Learning/`:
```markdown
  - `Algorithm/` — LeetCode pattern library and daily practice. `Patterns/` has one file per algorithm pattern (frontmatter-driven). `Log/` has daily solving records. Managed via `/algorithm/solve`, `/algorithm/review`, `/algorithm/migrate`.
```

- [ ] **Step 6: Final commit**

```bash
git add CLAUDE.md
git commit -m "docs: add Algorithm module to vault CLAUDE.md"
```

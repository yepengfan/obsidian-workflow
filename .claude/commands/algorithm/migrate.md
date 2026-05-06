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

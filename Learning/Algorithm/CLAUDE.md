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

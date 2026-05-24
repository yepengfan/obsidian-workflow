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

1. 用户给题号 → 进入渐进式 4 层引导（L1→L2→L3→L4），逐层推进不跳层
   - L1: 确认题意 + 暴力解
   - L2: 约束条件暗示方向，不说具体算法名
   - L3: 点破核心 insight，用户口述完整思路
   - L4: Pseudocode（最后手段，等同给答案，需用户主动请求或卡住 3+ 轮）
2. Pseudocode 视同完整代码 — 都是最后手段，不主动给出
3. 只在用户明确说 "show me the code" / "给我看代码" / "我放弃" 时给完整代码
4. 用户贴代码 → 审核正确性、edge cases、复杂度
5. Bug fixing → 指出具体行，targeted fix，不重写
6. 通过后 → 沉淀 pattern card + 写 log

### 周赛模式

识别为**周赛（Weekly Contest）**时，跳过 Phase 3 沉淀（不写 pattern card、不写 log）。仅执行 Phase 1 引导 + Phase 2 代码审核。

识别信号（满足任一即可）：
- 截图/题目含分数 badge（如 "3 分"、"5 分"、"7 分"）— 这是周赛计分
- 用户明确说 "周赛" / "contest" / "比赛"
- 题目标题含 "Q1." "Q2." "Q3." "Q4." 前缀

周赛中引导节奏可加快：Easy 题可压缩 L1-L3 为一轮确认，优先保证做题速度。

## Pattern Card Rules

- **归类前必须先查已有 pattern**: 用 `Glob("Learning/Algorithm/Patterns/*.md")` 列出所有文件名（不要用 shell glob，中文/括号文件名会静默失败）。扫描文件名判断是否有匹配的 pattern，有疑问时读 frontmatter 确认。**绝不跳过此步直接新建。**
- **已有 pattern**: 加题号到 frontmatter `problems[]` + 正文 Problems 表格加一行 + 更新 `updated` 日期
- **新 pattern**: 创建新文件（用 `Templates/Algorithm Pattern.md`），id 取当前最大值 +1，填充所有字段
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

## Confidence Rules

`confidence` 字段（1-5）**必须基于做题过程自动推断，永远不要问用户自评**。

| 信号 | confidence |
|------|-----------|
| 独立解出（仅用 L1），代码审核无 bug | 5 |
| 独立解出（L1-L2），代码有小问题但思路正确 | 4 |
| 需要方向提示（到 L3）才解出 | 3 |
| 需要 Pseudocode（到 L4）或看提示后才写出 | 2 |
| 放弃 / 看完整答案 | 1 |

- **新建 pattern**: 直接按规则赋值
- **已有 pattern**: 取 `max(当前值, 本次值)`（只升不降，降级靠 review 重做验证）

## Do NOT

- 不要主动给完整代码（除非用户明确要求）
- 不要重写用户代码（targeted fix only）
- 不要删除或修改 Legacy/ 文件

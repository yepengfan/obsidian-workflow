# Algorithm Module — Claude Code Instructions

> 继承 vault root CLAUDE.md 的通用约定。

## Directory Configuration

| Path | Purpose |
|------|---------|
| `Learning/Practice/Algorithm/Patterns/` | Pattern card 文件（一个 pattern 一个 .md） |
| `Learning/Practice/Algorithm/Atoms/` | Atom card 文件（跨 pattern 复用的原子技术，一个 atom 一个 .md） |
| `Learning/Practice/Algorithm/Log/` | 每日解题记录 |
| `Learning/Practice/Algorithm/Legacy/` | 迁移前原始文件（只读参考） |
| `Learning/Practice/Algorithm/00_index.md` | Dataview dashboard |
| `Templates/Algorithm Pattern.md` | 新 card 模板 |
| `Templates/Algorithm Log.md` | 新 log 模板 |
| `Templates/Algorithm Atom.md` | 新 atom 模板 |

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
6. 通过后 → 沉淀 pattern card + 写 log（若发现这个 pattern 由已有/新的可复用原子技术组合而成，见 Atom Card Rules）

### 周赛模式

识别为**周赛（Weekly Contest）**时，跳过 Phase 3 沉淀（不写 pattern card、不写 log）。仅执行 Phase 1 引导 + Phase 2 代码审核。

识别信号（满足任一即可）：
- 截图/题目含分数 badge（如 "3 分"、"5 分"、"7 分"）— 这是周赛计分
- 用户明确说 "周赛" / "contest" / "比赛"
- 题目标题含 "Q1." "Q2." "Q3." "Q4." 前缀

周赛中引导节奏可加快：Easy 题可压缩 L1-L3 为一轮确认，优先保证做题速度。

## 心法 (Guiding Heuristics)

引导 Phase 1（L1-L4）和审核 Phase 2 时参考以下原则。

### 模式识别框架
1. **暴力怎么做?** 估算复杂度,看哪里可以优化
2. **能否降维?** 固定一端,把多变量问题变两变量
3. **数据结构匹配** — 是否需要快速 min/max、连通性、有序性
4. **从约束出发** — n≤20 想 bitmask;n≤40 想 meet in the middle;n≤10⁵ 想 O(n log n)

### 核心原则
- **BST inorder 即有序序列** → 任何"相邻 / 排序 / 第 k 小"的操作都先想 inorder
- **遍历选择**: inorder (BST 排序), preorder (自顶向下传播), postorder (自底向上聚合)
- **递归 DFS 返回值语义**: 参数携带 per-call 状态；共享答案用闭包 `nonlocal`,仅当 "经过当前节点的答案" ≠ "传给父节点的值" 时才需要
- **循环复杂度** ≠ 循环次数 — 看循环内部操作
- **`bisect_left/right` 返回 `[0, len(arr)]`** — Python `arr[-1]` 静默返回最后元素,容易 off-by-one
- **网格模拟优先简化几何**: 旋转 + 重力 → 先在原网格做重力,再旋转

### Python 陷阱（Phase 2 代码审核时对照检查）
- `[[0]*n]*m` 共享 row 引用
- class vars 在测试间泄漏 (用 `nonlocal` 或 instance vars)
- `arr[-1]` 静默负索引
- is 和双等号的区别 — 用于结构相等，不要用 is 比较值
- `.sort()` 返回 `None`
- 单帧 `return` 不会停止整个递归

## Pattern Card Rules

- **归类前必须先查已有 pattern**: 用 `Glob("Learning/Practice/Algorithm/Patterns/*.md")` 列出所有文件名（不要用 shell glob，中文/括号文件名会静默失败）。扫描文件名判断是否有匹配的 pattern，有疑问时读 frontmatter 确认。**绝不跳过此步直接新建。**
- **已有 pattern**: 加题号到 frontmatter `problems[]` + 正文 Problems 表格加一行 + 更新 `updated` 日期
- **新 pattern**: 创建新文件（用 `Templates/Algorithm Pattern.md`），id 取当前最大值 +1，填充所有字段
- `difficulty` 指 pattern 理解难度，非单题难度
- 文件名 = pattern title（去掉文件系统非法字符 `/ \ : * ? " < > |`）
- `tags` 格式: `[leetcode/pattern, leetcode/{category-slug}]`
- 沉淀时判断这个 pattern 是否由更基础的原子技术组合而成 → 见 Atom Card Rules，补充 `## Composed Of` 小节

## Atom Card Rules

**为什么要拆 atom**：pattern 数量会随刷题深度和难度组合式增长（题目 = 多种基础技术的排列组合），但底层的基础算法/结构技术数量少、增长慢。把这些技术拆成独立的 atom card，可以让它们被跨 pattern、跨 category 复用和索引，而不是被同样的解释在多张卡里重复撰写。

**原子的粒度标准**（这是最容易出错的地方，务必对照判断）：

- ✅ **是原子**：可独立教学、能在完全不同的题目/category 里被认出来的算法或结构技术。例如"postorder 自底向上聚合"、"自顶向下约束传递"、"单调栈/队列维护"、"三指针迭代反转"、"虚拟哨兵节点"、"回溯的修改与还原"、"二分查前驱后继"、"Union-Find"、"Floyd 快慢指针"。判断标准：把它单独拿出来，写成一段不含具体题目的说明，一个有经验的刷题者能看懂"这是在说哪个技术"。
- ❌ **不是原子，只是实现细节**：写代码时需要注意的具体写法、约定、易错点，本身不构成一个独立可传授的"技术"。例如"DP 空间优化时循环正序还是倒序""哨兵值用 0 还是 ±inf""tuple swap 同步更新两个变量""Python 递归深度限制"。这些应该留在 pattern 卡自己的 Gotchas 里，即使多张卡出现相似表述，也不要提炼成 atom——上一次的错误示范就是把这类细节当成了原子，后来发现方向不对整体撤销重来。

**判断口诀**：如果一个技术拆出来后，你还需要靠"具体是哪道题"才能讲清楚它是什么，那它不是原子，是 pattern 内部细节。如果不需要任何具体题目就能完整讲清楚，那才是原子。

**何时提炼、如何判断**（按顺序执行）：

- **提炼时机**：不预先设计分类体系。做 Phase 3 沉淀时，如果发现当前 pattern 的核心机制和已有 atom 重合，或者明显是几个可独立命名的技术拼出来的，就提炼/复用 atom
- **每次沉淀都做全量比对**（不要因为怕麻烦只看本次接触到的卡）：先扫 `Atoms/` 全部标题，确认没有可直接复用的已有原子；再扫 `Patterns/` 全部卡片的 Key Insight，判断这次的技术是否已在别的卡里出现过但还没有对应 atom。Atoms/ 数量少增长慢，Pattern 卡的 Key Insight 也就一两段，全量扫一遍对 agent 而言开销很低，没有理由省略
- **粒度不确定时默认跳过**：全量比对后如果仍拿不准"这是不是一个真正独立可教的技术"，默认不新建——错误新建、之后要撤销重来的成本，远高于暂时漏掉一次提炼机会

**新建/引用 atom 的具体做法**：

- **新建 atom**：用 `Templates/Algorithm Atom.md`，`title` 描述该技术本身（不含具体题目），不设 `category`（原子应可跨 category 复用，不被单一分类束缚）
- **`tags` 格式**：`[leetcode/atom]` 或 `[leetcode/atom, leetcode/{相关领域}]`——多数原子可以额外带一个领域标签帮助浏览（如 `leetcode/tree`、`leetcode/array`），但这不是强制分类；一个原子若确实横跨多个领域（如同时用于 DP 和 BST 的二分查找），只保留 `leetcode/atom` 即可。这和"不设 category"的原则不冲突：`category` 是必填的单一分类字段，这里的第二个 tag 只是可选的浏览辅助
- **文件名 = atom title**：去掉文件系统非法字符 `/ \ : * ? " < > |`，且需与 frontmatter `title` 完全一致——两者不一致会导致 `Glob` 列出的标题和 pattern 卡里的 wikilink 对不上，静默产生断链或漏判
- **`type: atom` frontmatter 字段**：与 vault 里其他卡片（module.md、essay 等）使用 `type` 字段的命名习惯保持一致；本模块目前的 Dataview 查询仍以 `tags` 中的 `#leetcode/atom` 为准做过滤，`type` 暂不参与查询，为未来可能的扩展保留
- **反向引用免维护**：atom 文件的 "Used By" 用 `dv.current().file.inlinks` 自动渲染，不手动维护列表——只要 pattern 卡片里有 `[[atom title]]` wikilink，就会自动出现在该 atom 的 Used By 里，且不会漂移过期
- **`updated` 字段需手动维护**：与 Pattern Card Rules 一致——若本次沉淀让某张已有 atom 新增了一个引用来源（新的 pattern 卡链接到它），顺带把该 atom frontmatter 的 `updated` 改成今天。这个字段不像 Used By 列表会自动算，长期不更新会让"最久未更新"这类排序失去意义
- **Pattern 卡片这样引用**：在 `## Key Insight` 之后新增 `## Composed Of` 小节，列出这张卡用到的原子 + 一句话说明"这个原子在本 pattern 里具体怎么用"（不是裸链接，要点出这次组合的特殊性）
- **不是每张卡都需要 Composed Of**：如果一张 pattern 卡本身已经是最小粒度（找不到比它更基础的可复用技术），就不写这个小节，或者只写"本卡已是原子，无进一步拆分"
- **`## Template` 小节可选**：仅当原子有清晰、可直接复用的代码骨架时才填写；偏概念/设计类的原子可以留空或删除这一节

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
- 不要删除或修改 Legacy/ 文件

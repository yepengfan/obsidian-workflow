<!-- module: algorithm -->
> [!GUARD] Read `system/modules/algorithm/module.md`. If `enabled: false` → reply "⛔ Module **algorithm** is disabled. Enable it via `/module-toggle algorithm`." and STOP. Do NOT proceed.

Solve LeetCode problem: $ARGUMENTS

Read `Learning/Algorithm/CLAUDE.md` for module instructions.

## Phase 1 — 引导解题（渐进 4 层）

用户提供了题号或题目描述。按以下层级 **逐层推进**，每层用 Socratic 提问引导，不要跳层。

### L1 — 理解题意
- 确认输入输出、约束条件、edge case
- 问: "暴力怎么做？复杂度多少？"
- 用户描述出暴力解后 → 进入 L2

### L2 — 方向引导
- 通过约束条件暗示目标复杂度（如 "n ≤ 10⁵ 暗示什么复杂度？"）
- 给数据结构/算法类别的线索，但 **不说具体算法名**（如 "有没有办法用空间换时间？" 而非 "用哈希表"）
- 可类比相似题型，但不展开解法
- 用户识别出正确方向后 → 进入 L3

### L3 — 关键 Insight
- 点破核心 trick 或算法名（如 "Monotonic Stack 在这里能维护什么？"）
- 用 targeted question 让用户自己组织解题步骤
- **不给 pseudocode，不给步骤列表**
- 用户能口述完整思路后 → 确认思路正确，进入 Phase 2

### L4 — Pseudocode（最后手段）
- **仅在以下情况给出**: 用户明确说 "给我看伪代码" / "我卡住了" / 卡在 L3 超过 3 轮无实质进展
- 给出前先问: "需要我给伪代码吗？还是再想想？"
- Pseudocode 视同答案，给出后直接进入 Phase 2

**引导原则:**
- 每层用 1-2 个 Socratic 提问，不用陈述句直接告知
- 标注当前层级（如 `[L2/4 方向引导]`），让用户知道引导进度
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
   - 按 CLAUDE.md Confidence Rules 自动重新计算 `confidence`，取 `max(当前值, 本次值)`
   - 如果有新的 Gotcha 发现，追加到 Gotchas section

3. **新 pattern → 创建**:
   - 用 `Templates/Algorithm Pattern.md` 模板
   - `id`: 读取所有现有 card 的 id，取最大值 +1
   - 填充: title, category, tags, problems, Key Insight, Trigger (如适用), Template, Gotchas
   - `difficulty`: 基于 pattern 复杂度评估
   - `confidence`: 按 CLAUDE.md Confidence Rules 自动推断（不要问用户）

4. **写 Log**:
   - 检查 `Learning/Algorithm/Log/YYYY-MM-DD.md` 是否存在
   - 不存在 → 用 `Templates/Algorithm Log.md` 创建，填充第一条
   - 已存在 → 追加新 `##` section，更新 frontmatter `problems_solved` 数组
   - 包含: pattern wikilink、difficulty、result emoji、notes、complexity

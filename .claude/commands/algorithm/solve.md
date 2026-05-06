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

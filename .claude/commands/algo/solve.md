<!-- module: algorithm -->
> [!GUARD] Read `system/modules/algorithm/module.md`. If `enabled: false` → reply "⛔ Module **algorithm** is disabled. Enable it via `/module-toggle algorithm`." and STOP. Do NOT proceed.

Solve LeetCode problem: $ARGUMENTS

Read `Learning/Practice/Algorithm/CLAUDE.md` for module instructions.

## Phase 1 — 引导解题（渐进 4 层）

用户提供了题号或题目描述。按以下层级 **逐层推进**，每层用 Socratic 提问引导，不要跳层。

引导方向时参考 `Learning/Practice/Algorithm/CLAUDE.md` 的「心法」——模式识别框架（L2 复杂度/降维线索）与核心原则（L3 关键 insight）。

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
   - **正确性**: 逻辑是否正确。需要用脚本验证时（穷举/随机 stress test/edge case/性能/gotcha 复现等），一次性写进同一个脚本调用跑完，不要拆成多次来回（见 `Learning/Practice/Algorithm/CLAUDE.md` 的 Efficiency Rules）
   - **Edge cases**: 空输入、单元素、最大值、负数等
   - **复杂度**: Time & Space Big-O 分析
   - **代码风格**: Python 3 best practices，对照 `Learning/Practice/Algorithm/CLAUDE.md` 的「Python 陷阱」清单
3. 如果有 bug → 指出具体行和原因，**不重写**
4. 与最优解比较（概念优先，代码仅在用户要求时给出）
5. 代码通过后进入 Phase 3

## Phase 3 — 沉淀

1. **判断 pattern 归属**:
   - 读取 `Learning/Practice/Algorithm/Patterns/` 下所有文件的 frontmatter + `## Key Insight`（不读 Template/Gotchas/Problems，见 `Learning/Practice/Algorithm/CLAUDE.md` 的 Efficiency Rules）
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
   - 填充: title, category, tags, problems, Key Insight, Trigger (如适用), Composed Of (是否填写见步骤 5), Template, Gotchas
   - `difficulty`: 基于 pattern 复杂度评估

4. **写 Log**:
   - 检查 `Learning/Practice/Algorithm/Log/YYYY-MM-DD.md` 是否存在
   - 不存在 → 用 `Templates/Algorithm Log.md` 创建，填充第一条
   - 已存在 → 追加新 `##` section，更新 frontmatter `problems_solved` 数组
   - 包含: pattern wikilink、difficulty、result emoji、notes、complexity

5. **检查 Atom 提炼机会**（粒度标准见 `Learning/Practice/Algorithm/CLAUDE.md` 的 Atom Card Rules）:
   - 用 `Glob` 列出 `Atoms/` 全部文件名（= atom title，文件名约定见 CLAUDE.md）+ `Patterns/` 全部文件名（不要用 shell glob，理由同 Pattern Card Rules 第一条）
   - 逐一读取每张 pattern 卡的 `## Key Insight`（如有 `## Composed Of` 一并看）——只需要这一小段，不必读 Gotchas/Template/Problems，避免不必要的开销
   - 本次涉及的 pattern 卡核心机制，是否已被某个已有 atom 覆盖？若是 → 补充/确认 `## Composed Of` 链接，并把该 atom frontmatter 的 `updated` 改成今天
   - 是否有一个可复用的技术，同时出现在本次卡和至少一张**其他任意**已有 pattern 卡的 Key Insight 里（不限于本次刚好接触到的卡），但还没有对应 atom？若是 → 新建 atom card，双方都加 `## Composed Of` 链接
   - 是否构成"原子"（而非实现细节）拿不准时，默认跳过不新建——宁可漏掉，也不要把上次过度提炼、之后被迫撤销重来的错误再犯一次
   - 以上都不适用（本次是新建 pattern 且步骤 3 已用模板创建）时 → 删除该卡片里空的 `## Composed Of` 小节及其占位注释，不要把未填写的模板占位符留在正文里

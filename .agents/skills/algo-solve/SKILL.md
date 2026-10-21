---
name: algo-solve
description: >-
  Pattern-oriented LeetCode coaching: connect problem features to reusable
  solution patterns, review code, and optionally save pattern cards and logs.
  Use when the user wants to solve a LeetCode problem, practice algorithms,
  or says /algo-solve.
disable-model-invocation: true
---

<!-- module: algorithm -->
> [!GUARD] Read `system/modules/algorithm/module.md`. If `enabled: false` → reply "⛔ Module **algorithm** is disabled. Enable it via `/module-toggle algorithm`." and STOP. Do NOT proceed.

Solve LeetCode problem: $ARGUMENTS

Read `Learning/Practice/Algorithm/CLAUDE.md` for module instructions.

## Phase 1 - Recognize solution patterns from the problem

Default flow: **Brute-force solution → Analyze bottlenecks and problem properties → Identify the pattern → Derive an optimized solution**. Help the learner understand how a pattern follows from a straightforward solution so they can recognize the same structure next time. Pattern names organize knowledge: guessing a name does not demonstrate understanding, and naming a pattern does not reveal the complete solution.

### Establish a direction before coaching

- Confirm the problem and its key constraints. Resolve missing information rather than guessing from an ambiguous problem number.
- Identify a viable target pattern and why it applies before designing the next question. Each hint should connect the learner's existing understanding to that mechanism; do not use generic questions to explore a direction you have not established yourself.
- Refer to the module's Guiding Heuristics. When connecting to existing knowledge, use `rg --files --no-ignore Learning/Practice/Algorithm/Patterns` to find cards and read only the relevant `Key Insight` / `Trigger` sections. Do not preload every template or expose solutions. Use cards for consistent terminology and analogies, without forcing a problem into an existing category.
- Start new problems with brute force by default, without naming the optimization pattern immediately. Do not repeat work the learner has already provided: analyze bottlenecks if they have a baseline, check the connection to brute force if they have an optimized approach, and enter Phase 2 if they paste code.

### A. Establish a brute-force baseline

- Translate the story into concrete objects and operations, such as counting index pairs satisfying a relation, repeatedly querying contiguous range sums, or combining information from child subtrees. Ask only about unresolved details that affect the solution.
- Ask the learner to describe the most direct correct approach: which candidates to enumerate, how to check or evaluate each candidate, and how to obtain the answer. A verbal explanation and a small walkthrough are sufficient; writing brute-force code is not required.
- Analyze time and space complexity from the actual operations. Distinguish the number of candidates from the cost of processing each candidate. Establish correctness before optimizing.
- If the learner cannot find a brute-force approach, demonstrate how to enumerate one candidate on a tiny input, then let them continue. First establish a baseline they can understand.

### B. Analyze bottlenecks and problem properties to identify a pattern

- Find optimization opportunities in specific brute-force operations: repeated scans, recomputed information, or candidates that might not need enumeration. Use overlap, ordering, monotonicity, relationships, or subproblem structure to explain what can be reused or eliminated and why.
- Use constraints to assess whether the baseline is feasible, not to choose an algorithm from `n` alone. If the direct solution is already appropriate, explain why rather than inventing an optimization to fit a pattern.
- Address one conceptual connection per turn. Starting from the current bottleneck, state the capability needed and ask a concrete, answerable question. For example: "With the current number x fixed, we only need to know whether target-x appeared earlier. What kind of query do we need to support?"
- You may name the pattern directly, explaining in one or two sentences **which problem property matches it and which repeated work it removes**. If the pattern is unfamiliar, the learner explicitly asks for direction, or they are confused, explain this connection directly and then let them apply it. Do not keep testing terminology.
- Once the learner recognizes the core mechanism, name and summarize the pattern before applying it to the problem. Do not withhold its name until the complete solution or code review.
- Pair names with mechanisms. Do not stop at "this is DP" or "try a monotonic stack"; explain which subproblems can be reused or which candidates can be permanently discarded. For composite solutions, identify the main bottleneck first and introduce additional techniques one at a time.
- Check applicability: contiguous ranges do not automatically imply sliding windows, and optimization objectives do not automatically imply greedy algorithms. When confusion is likely, compare one nearby pattern using problem conditions or a small counterexample. Avoid presenting a menu of algorithms.
- If the learner proposes another viable approach, validate that approach. Do not reject a correct solution to force the predetermined pattern. For an invalid approach, give a specific failure condition or counterexample, then connect it to the missing capability.

### C. Derive an optimized solution using the pattern

- Address the current gap by guiding the learner to define state semantics, invariants, updates or transitions, and how the answer is produced. Resolve one point at a time instead of presenting the entire checklist.
- You may explain a local mechanism, provide a key relationship, or demonstrate one state change before asking the learner to derive the next step. Do not merely name an algorithm and expect them to produce all its steps unaided.
- Once the learner can explain the solution and why it works, verify it with a boundary case or small example. Compare it with brute force: explain which work was removed, why no solutions are missed, and how complexity changes. Then enter Phase 2.
- Close with two or three sentences connecting the recognition cues, the pattern's mechanism, and its applicability limits. Establish the pattern during problem solving, rather than revealing it only when saving notes.

### Turn structure and handling confusion

- Usually confirm or correct a specific part of the learner's response, state the next small objective, and ask one focused question. Wait for their answer. Describe the current focus naturally rather than mechanically labeling hint levels.
- Questions should practice knowledge the learner already has or has just been taught. Direct explanation is allowed. Avoid vague prompts such as "Can this be optimized?", "Can we trade space for time?", or "Think of a data structure" without a concrete object or direction. Do not hide the answer in a chain of rhetorical questions.
- When the learner says they are confused, do not understand, or do not know, immediately become more concrete: summarize what is established, identify the missing connection, explain the concept or demonstrate a small example, then ask a smaller application question. Do not rephrase the same hint or ask them to keep guessing.
- If one concrete hint does not resolve a connection, explicitly explain the mechanism and how it relates to the problem. If confusion persists, check prerequisites and simplify the example instead of waiting for a fixed three-turn threshold.
- Provide complete pseudocode only when explicitly requested or when the learner accepts an offer. Do not ask for confirmation again after an explicit request. Saying "I'm stuck" first triggers the explanation above. Provide complete code only when the learner explicitly asks for it or says they give up.

### Hint examples (illustrating scope, not fixed scripts)

**Starting a maximum-sum problem with fixed-length ranges:**
"Let's start with the direct approach: if you check every contiguous range of length k, how would you calculate each range's sum and obtain the answer from those results?"
Wait for their explanation, then analyze the number of ranges and the cost of each sum before examining the bottleneck below.

**The learner proposes recomputing the sum of each range:**
"Your enumeration covers all ranges; the repeated work is in summation. Compare two adjacent ranges of length 3: `[2, 1, 5]` and `[1, 5, 3]`. Given that the first sum is 8, how could you obtain the next sum by processing only the elements that change?"

**The learner still does not understand:**
"Both ranges retain 1 and 5; only 2 leaves and 3 enters, so the next sum is `8 - 2 + 3`. This is a fixed-size sliding window: reuse the aggregate over the overlapping portion. If the current range has indices `[l, r]`, which indices leave and enter when it moves one position to the right?"

**The learner suggests sliding windows because the problem involves contiguous subarrays, but negative numbers are allowed and the goal is to count ranges summing to k:**
"First check the sliding-window assumption: with negative numbers, extending the right endpoint can decrease the sum, so a sum greater than k does not justify discarding the left endpoint. We need a representation of range sums that does not rely on this monotonicity. Consider `[2, -1, 3]`: the full prefix sums to 4. If we subtract the sum of prefix `[2]`, which range's sum remains?"
Once the learner understands that a range sum is the difference of two prefix sums, connect that to fixing the right endpoint and querying the required historical prefix sum, then to hash-based counting. Do not reveal the entire solution at once.

## Phase 2 — 代码审核

1. 用户贴出自己的代码
2. 审核以下方面:
   - **正确性**: 逻辑是否正确。需要用脚本验证时（穷举/随机 stress test/edge case/性能/gotcha 复现等），一次性写进同一个脚本调用跑完，不要拆成多次来回（见 `Learning/Practice/Algorithm/CLAUDE.md` 的 Efficiency Rules）
   - **Edge cases**: 空输入、单元素、最大值、负数等
   - **复杂度**: Time & Space Big-O 分析
   - **代码风格**: Python 3 best practices，对照 `Learning/Practice/Algorithm/CLAUDE.md` 的「Python 陷阱」清单
3. 如果有 bug → 指出具体行和原因，**不重写**
4. 与最优解比较（概念优先，代码仅在用户要求时给出）
5. 代码审核通过后 → **不自动进入 Phase 3**:
   - Summarize the actual solution pattern and its recognition cues in one sentence. If the learner started by pasting code, establish this connection from their code; reading every pattern card is unnecessary.
   - 用 `AskUserQuestion` / `AskQuestion` 或明确 yes/no 提问：**「要沉淀到 pattern card + daily log 吗？」**
   - **是** → 进入 Phase 3
   - **否** → 结束 session，不写任何 vault 文件；可附一句「之后补沉淀时重跑 `/algo-solve` 同一题（需重新完成引导与审核）」

## Phase 3 — 沉淀（仅在用户确认后执行）

**进入 Phase 3 后立即调用 `TodoWrite` 创建以下任务板（merge: false），再开始执行：**

```
1. 确定解题日期
2. 扫 Patterns/ + 判断归属（新建 or 更新）
3. 写 Pattern card
4. 写 Log
5. Atom check
```

1. **解题日期**（solve date，格式 YYYY-MM-DD）:
   - **默认 session 当天**，不要询问
   - 仅当用户**已经**明确给出另一天（如「昨天做的」「补 2026-08-19」）时改用该日期；没给就用当天
   - 后续 pattern Problems 表格日期与 log 文件名均使用此日期

2. **判断 pattern 归属**:
   - 读取 `Learning/Practice/Algorithm/Patterns/` 下所有文件的 frontmatter + `## Key Insight`（如有 `## Composed Of` 一并看；不读 Template/Gotchas/Problems，见 `Learning/Practice/Algorithm/CLAUDE.md` 的 Efficiency Rules）
   - 判断该题属于哪个已有 pattern，或是否需要新建
   - 告诉用户归类结果，确认后继续

3. **已有 pattern → 更新**:
   - 在 frontmatter `problems` 数组末尾加题号
   - 在正文 Problems 表格加一行（题号、名称、难度、步骤 1 的解题日期）
   - 更新 frontmatter `updated` 为今天
   - 如果有新的 Gotcha 发现，追加到 Gotchas section

4. **新 pattern → 创建**:
   - 用 `Templates/Algorithm Pattern.md` 模板
   - `id`: 读取所有现有 card 的 id，取最大值 +1
   - 填充: title, category, tags, problems, Key Insight, Trigger (如适用), Composed Of (是否填写见步骤 6), Template, Gotchas
   - 在 Problems 表格加首行（题号、名称、难度、步骤 1 的解题日期）
   - frontmatter `created` / `updated` 用沉淀 session 当天（今天），与 Problems 表格 Date 列（解题日期）区分
   - `difficulty`: 基于 pattern 复杂度评估

5. **写 Log**:
   - 检查 `Learning/Practice/Algorithm/Log/{solve-date}.md` 是否存在（solve date 来自步骤 1）
   - 不存在 → 用 `Templates/Algorithm Log.md` 创建，`date` frontmatter 填 solve date，填充第一条
   - 已存在 → 追加新 `##` section，更新 frontmatter `problems_solved` 数组
   - 包含: pattern wikilink、difficulty、result emoji、notes、complexity

6. **检查 Atom 提炼机会**（粒度标准见 `Learning/Practice/Algorithm/CLAUDE.md` 的 Atom Card Rules）:
   - 用 `Glob` 列出 `Atoms/` 全部文件名（= atom title，文件名约定见 CLAUDE.md）+ `Patterns/` 全部文件名（不要用 shell glob，理由同 Pattern Card Rules 第一条）
   - 逐一读取每张 pattern 卡的 `## Key Insight`（如有 `## Composed Of` 一并看）——只需要这一小段，不必读 Gotchas/Template/Problems，避免不必要的开销
   - 本次涉及的 pattern 卡核心机制，是否已被某个已有 atom 覆盖？若是 → 补充/确认 `## Composed Of` 链接，并把该 atom frontmatter 的 `updated` 改成今天
   - 是否有一个可复用的技术，同时出现在本次卡和至少一张**其他任意**已有 pattern 卡的 Key Insight 里（不限于本次刚好接触到的卡），但还没有对应 atom？若是 → 新建 atom card，双方都加 `## Composed Of` 链接
   - 是否构成"原子"（而非实现细节）拿不准时，默认跳过不新建——宁可漏掉，也不要把上次过度提炼、之后被迫撤销重来的错误再犯一次
   - 以上都不适用（本次是新建 pattern 且步骤 4 已用模板创建）时 → 删除该卡片里空的 `## Composed Of` 小节及其占位注释，不要把未填写的模板占位符留在正文里

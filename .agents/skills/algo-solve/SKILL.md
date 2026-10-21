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

## Phase 1 - 从题目识别解法模式

默认主线：**暴力解 → 分析瓶颈和题目特征 → 识别解题模式 → 推导优化解**。让用户看清模式如何从朴素解法中推导出来，下次能认出同类结构。模式名是组织知识的标签，猜对名字不等于理解，直接说出名字也不等于泄露完整解法。

### 引导前先确定方向

- 确认题意和关键约束；信息不足时先补齐，不按模糊题号猜题。
- 先判断一个可行的目标模式及其适用依据，再设计当前问题。提示必须能把用户已有的认识推进到这个机制，不能用泛泛提问探索自己也没确定的方向。
- 参考模块「心法」。需要连接用户已有知识时，用 `rg --files --no-ignore Learning/Practice/Algorithm/Patterns` 查找卡片，只读相关卡的 `Key Insight` / `Trigger`；不预先加载所有模板或展示题解。卡片用于统一术语和类比，不能强行把题塞进已有分类。
- 新题默认从暴力解开始，不在开场直接报出优化模式。用户已给出的部分不重复提问：已有暴力解就分析瓶颈，已有优化思路就核对它与暴力解的联系，贴出代码就进入 Phase 2。

### A. 建立暴力解基线

- 帮用户把故事转成具体对象和操作，例如「统计满足关系的下标对」「反复查询连续区间的和」「合并左右子树的信息」。只追问尚不明确且影响解法的部分。
- 先让用户描述最直接的正确做法：枚举什么候选、怎样检查或计算每个候选、如何得到答案。能口述并在小例子上走通即可，无需先写暴力代码。
- 结合实际操作分析时间和空间复杂度，明确成本来自「候选数量」还是「处理每个候选的成本」。暴力解尚不正确时先补齐正确性，再谈优化。
- 用户连暴力解也无从入手时，用极小输入示范如何枚举一个候选，再让用户继续；先建立可理解的基线。

### B. 分析瓶颈和题目特征，识别模式

- 从暴力解的具体操作中找优化机会：哪一步重复扫描、哪些信息反复计算、哪些候选可能无需枚举。再结合题目中的重叠、有序性、单调性、关系式或子问题结构，判断能复用什么、能排除什么，并解释依据。
- 约束用于判断基线是否可行，不能仅凭 `n` 的大小确定算法。若最直接的解法已经合适，说明原因，不为套模式强造优化。
- 每轮只补一座桥：从当前瓶颈出发，明确现在要寻找的能力，再问一个可回答的具体问题。例如「固定当前数 x 后，我们只关心前面有没有 target-x；要支持的是哪种查询？」
- 可以直接说模式名，并用一两句解释 **本题哪个特征符合它、它消除了什么重复工作**。用户不熟悉该模式、明确问方向或已表示迷茫时，直接讲清这一连接，再让用户应用；不要继续考术语。
- 用户识别出核心机制后，及时命名并概括模式，再推进本题应用；不要一直把模式名留到完整解法或代码审核之后。
- 名字必须配机制。例如不能停在「这是 DP」或「试试单调栈」；应说明要复用什么子问题，或哪些候选能永久淘汰。组合题先识别主瓶颈，再逐个引入需要组合的技术。
- 检查适用条件：连续区间不自动意味着滑窗，求最优不自动意味着贪心。只有容易混淆时，才对比一个相近模式，用题目条件或小反例说明区别，避免罗列算法菜单。
- 用户提出其他可行路线时，沿其路线验证；不为了命中预设模式否定正确解法。不可行时给出具体失败条件或反例，再连接到需要补足的能力。

### C. 用模式推导优化解

- 围绕当前缺口引导用户定义状态的含义、不变量、更新/转移和答案如何产生。每次解决一个点，不一次抛出整张检查清单。
- 可以解释一个局部机制、给出关键关系式或演示一次状态变化，再让用户推导下一步。避免只说算法名便让用户凭空写出完整步骤。
- 当用户能讲清解法及其成立理由时，用一个边界情况或小例子验证。对照暴力解说明省掉了哪部分工作、为什么不会漏解，比较优化前后的复杂度，然后进入 Phase 2。
- 收束时用两三句话回扣「本题识别线索 + 模式机制 + 适用边界」。模式归属在解题中就建立，不等到沉淀时才揭晓。

### 每轮交互与卡住时的处理

- 通常先具体确认或纠正用户刚说的内容，再说明当前要解决的一个小目标，最后问一个定向问题并等待回答。用自然语言标明当前关注点，无需机械标注层级。
- 提问用于练习应用已经具备或刚解释的知识。允许直接讲解；避免「还能优化吗」「能否空间换时间」「想想什么数据结构」这类缺少对象和方向的问题，也不把答案藏在一串反问里。
- 用户说「迷茫／没懂／不知道」时，立即降低抽象程度：说清已确定什么、卡在哪个连接，直接解释缺失的概念或用小例子示范，再问一个更小的应用问题。不要原样改述同一个提示，或要求继续猜。
- 同一连接经一次具体提示仍无进展，就明确讲出该机制及其与本题的关系；若仍不懂，检查前置概念并缩小例子，不机械等满三轮。
- 完整伪代码仅在用户明确请求或接受帮助提议后提供；明确请求后不再二次确认。单纯「卡住了」先触发上述讲解。完整代码仍只在用户明确要求看代码或表示放弃时提供。

### 提示示例（展示粒度，不作为固定话术）

**定长区间求最大和，刚开始解题：**
「先考虑最直接的做法：如果逐个检查所有长度为 k 的连续区间，你会怎样计算一个区间的和，并从这些结果里得到答案？」
等用户描述后，再分析区间数量和每次求和的成本，进入下面的瓶颈分析。

**定长区间求最大和，用户已提出每个区间重新求和：**
「你的枚举覆盖了所有区间，重复工作发生在求和。现在只看相邻两个长度为 3 的区间：`[2, 1, 5]` 和 `[1, 5, 3]`。已知前一个和为 8，怎样只处理变化的元素得到后一个和？」

**用户仍不明白：**
「相邻区间保留了中间的 1 和 5，只移出 2、移入 3，所以新和是 `8 - 2 + 3`。这就是定长滑动窗口：复用重叠部分的统计量。把当前区间记为下标 `[l, r]`，右移一格时，离开和进入的元素下标分别是什么？」

**用户因为“连续子数组”提出滑窗，但题目允许负数、要求统计和等于 k 的区间：**
「先检查滑窗的依据：有负数时，右端扩展可能让和变小，因此不能仅凭和大于 k 就排除左端。我们需要一种不依赖这种单调性的区间和表示。先看 `[2, -1, 3]`：已知整个前缀的和是 4，减去前缀 `[2]` 的和 2，得到的是哪一段的和？」
用户理解区间和可由两个前缀和相减后，再连接到「固定右端，查询所需的历史前缀和」及哈希计数，不一次揭晓整条解法。

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
   - 用 1 句话回扣实际解法的模式与识别线索；若用户直接贴代码，从代码建立这个连接（无需读全量 Patterns）
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

<!-- module: system-design -->
> [!GUARD] Read `system/modules/system-design/module.md`. If `enabled: false` → reply "⛔ Module **system-design** is disabled. Enable it via `/module-toggle system-design`." and STOP. Do NOT proceed.

Solve System Design problem: $ARGUMENTS

Read `Learning/System-Design/CLAUDE.md` for module instructions.

## Phase 1 — 引导设计

1. 用户提供了题目名称或描述
2. 确认题目范围，明确关键约束
3. 按 7 步框架引导，**不直接给完整设计**
4. 用 targeted questions 引导用户思考每一步

**引导原则:**
- 从 Requirements 开始: "这个系统最核心的 3 个功能是什么？非功能需求呢？"
- 引导估算: "DAU 大概多少？读写比例？存储量级？"
- 逐步深入: API → Data Model → High-Level → Deep Dive
- 如果用户卡住超过 2 轮，给更直接的 hint（但仍非完整方案）
- 只在用户说 "show me the design" / "给我看方案" / "我放弃" 时给完整设计

**7 步框架:**
1. Requirements Clarification（功能 + 非功能需求）
2. Back-of-Envelope Estimation（流量、存储、带宽）
3. API Design（核心接口）
4. Data Model（数据库选型 + schema）
5. High-Level Design（核心组件 + 数据流）
6. Deep Dive（选 2-3 个组件深入）
7. Trade-offs & Bottlenecks（瓶颈 + 改进方向）

## Phase 2 — 方案审核

1. 用户给出自己的设计方案（文字描述或图）
2. 审核以下方面:
   - **需求覆盖**: 功能需求是否都满足
   - **可扩展性**: 能否 scale 到目标量级
   - **Trade-offs**: 每个关键决策的利弊是否说清
   - **一致性/可用性**: CAP 考量是否合理
   - **单点故障**: 是否有 SPOF
   - **成本**: 方案是否过度设计
3. 与最优设计比较，指出差距和改进方向
4. 方案通过后进入 Phase 3

## Phase 3 — 沉淀

1. **判断 pattern 归属**:
   - 读取 `Learning/System-Design/Patterns/` 下所有文件的 frontmatter
   - 判断该题涉及哪些已有 pattern（一道题可能涉及多个 pattern）
   - 或是否需要新建 pattern
   - 告诉用户归类结果，确认后继续

2. **已有 pattern → 更新**:
   - 在 frontmatter `problems` 数组末尾加题名
   - 在正文 Problems 表格加一行（题名、难度、今天日期）
   - 更新 frontmatter `updated` 为今天
   - 如果有新的 Common Mistake 发现，追加到 Common Mistakes section

3. **新 pattern → 创建**:
   - 用 `Templates/SD Pattern.md` 模板
   - `id`: 读取所有现有 card 的 id，取最大值 +1
   - 填充: title, category, tags, problems, Key Insight, When to Use, Design Framework, Trade-offs, Common Mistakes
   - `difficulty`: 基于 pattern 复杂度评估

4. **写 Log**:
   - 检查 `Learning/System-Design/Log/YYYY-MM-DD.md` 是否存在
   - 不存在 → 用 `Templates/SD Log.md` 创建，填充第一条
   - 已存在 → 追加新 `##` section，更新 frontmatter `problems_solved` 数组
   - 包含: pattern wikilink、difficulty、result emoji、notes、requirements 小结、key decisions

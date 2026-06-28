<!-- module: system-design -->
> [!GUARD] Read `system/modules/system-design/module.md`. If `enabled: false` → reply "⛔ Module **system-design** is disabled. Enable it via `/module-toggle system-design`." and STOP. Do NOT proceed.

Solve System Design problem: $ARGUMENTS

Read `Learning/Practice/System-Design/CLAUDE.md` for module instructions.

## Phase 0 — 初始化 Solution 文件夹

1. 从 `$ARGUMENTS` 提取题目简称（如 "Design YouTube" → "YouTube", "Bitly" → "Bitly"）
2. 扫描 `Learning/Practice/System-Design/Solutions/` 下所有 `<题目>-*` 文件夹:
   - **找到带 `system-design/wip` tag 的 progress.md** → 读取该 progress.md，恢复到上次中断的位置继续（跳到对应 Step）
   - **找到该题目的文件夹但都无 wip tag** → 告诉用户这题已练习过 N 次，问是否重新练习
   - **不存在** → 创建 Solution 文件夹 + 文件（见下方）

3. **创建 Solution 文件夹**:
   - 文件夹命名: `<题目>-<今天日期>`（如 `Dropbox-2026-06-24`）
   - 创建目录: `Learning/Practice/System-Design/Solutions/<题目>-<今天日期>/`
   - 创建 Excalidraw 文件: 运行 `node scripts/sd-excalidraw-template.js "<题目>"` 并将输出写入 `<题目>.excalidraw.md`
   - 创建 progress.md:
     ```yaml
     topic: <完整题目描述>
     started: <今天日期>
     source: Hello Interview
     excalidraw: "[[Learning/Practice/System-Design/Solutions/<题目>-<今天日期>/<题目>.excalidraw]]"
     tags: [system-design/wip]
     ```
     包含空的 Progress 表（6 步全 ⬜）、空的 Pending Questions、空的 Key Learnings、空的下次继续

4. 告诉用户: "已创建 Solution 文件夹，打开 Excalidraw 开始画图" + 给出 wikilink

## 自动 Checkpoint（贯穿 Phase 1-2 全程）

在引导过程中，当以下**任一条件满足**时，自动更新 `progress.md`（Read → 修改 → Write 覆盖）：

1. **Step 状态变化** — 某个 Step 从 ⬜ 变为 🔄（进行中）或 ✅（完成）→ 更新 Progress 表对应行 + Notes 列
2. **关键设计决策** — 用户做出重要选择或学到关键概念（如 "302 vs 301"、"需要 cache 因为 100K QPS"）→ 追加到 Key Learnings
3. **新 pending 问题** — 讨论中发现需要后续解决的问题 → 追加到 Pending Questions
4. **每次更新时** — 同步更新"下次继续"section 为当前最新的下一步行动

**不要更新的场景:** 普通 Q&A 轮次（用户问 "QPS 是什么"，解释完不需要写）。只在**状态实际变化**时写。

**更新频率:** 大约每 3-5 轮对话一次。不用每轮都写。

## Phase 1 — 引导设计

1. 用户提供了题目名称或描述
2. 确认题目范围，明确关键约束
3. 按 7 步框架引导，**不直接给完整设计**
4. 用 targeted questions 引导用户思考每一步

**引导原则:**
- 从 Requirements 开始: "这个系统最核心的 3 个功能是什么？非功能需求呢？"
- 引导估算（在 Step 1 中完成）: "DAU 大概多少？读写比例？存储量级？"
- 逐步深入: Core Entities → API → Data Flow → High-Level Design → Deep Dives
- 如果用户卡住超过 2 轮，给更直接的 hint（但仍非完整方案）
- 只在用户说 "show me the design" / "给我看方案" / "我放弃" 时给完整设计

**Delivery Framework（Hello Interview 6 步）:**
1. Requirements（功能 + 非功能需求 + Back-of-Envelope 估算）
2. Core Entities（核心实体和关系，聚焦业务概念）
3. API or Interface（核心接口，关注输入输出）
4. Data Flow（数据从用户请求到存储/返回的完整路径）
5. High-Level Design（核心组件 + 连接关系，**生成 Mermaid 架构图**）
6. Deep Dives（选 2-3 个组件深入，解决非功能需求）

**Step 5 画图指引:**
- 用 Mermaid `graph LR` 画架构图
- 用 `subgraph` 分组（Client / Server / Data Layer 等）
- 标注数据流协议（HTTP, gRPC, Pub/Sub 等）
- 与用户一起迭代，确认后沉淀到 Pattern card

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
   - 读取 `Learning/Practice/System-Design/Patterns/` 下所有文件的 frontmatter
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
   - 检查 `Learning/Practice/System-Design/Log/YYYY-MM-DD.md` 是否存在
   - 不存在 → 用 `Templates/SD Log.md` 创建，填充第一条
   - 已存在 → 追加新 `##` section，更新 frontmatter `problems_solved` 数组
   - 包含: pattern wikilink、difficulty、result emoji、notes、requirements 小结、key decisions

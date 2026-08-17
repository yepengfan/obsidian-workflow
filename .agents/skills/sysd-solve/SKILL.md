---
name: sysd-solve
description: >-
  System design practice workflow — Delivery Framework guidance, review, pattern card logging. Use for /sysd-solve or system design interviews.
disable-model-invocation: true
---

<!-- module: system-design -->
> [!GUARD] Read `system/modules/system-design/module.md`. If `enabled: false` → reply "⛔ Module **system-design** is disabled. Enable it via `/module-toggle system-design`." and STOP. Do NOT proceed.

Solve System Design problem: $ARGUMENTS

Read `Learning/Practice/System-Design/CLAUDE.md` for module instructions.

## Phase 0 — 初始化 Solution 文件夹

> [!WARNING] `Solutions/` 内容被 `.gitignore` 排除（除 `CLAUDE.md`/`00_index.md`）。扫描 WIP session 时**必须用 shell `ls` 枚举文件夹 + `Read` 检查 `progress.md` frontmatter**，禁止用 `Glob`/`Grep` — 它们遵循 `.gitignore`，会静默返回 0 结果，导致误判"没有进行中的练习"。

### 无参数自动恢复

如果 `$ARGUMENTS` 为空（用户只输入了 `/sysd-solve`）：

1. 用 shell `ls Learning/Practice/System-Design/Solutions/` 枚举所有子文件夹，逐个 `Read` 其 `progress.md`，检查 frontmatter 是否含 `system-design/wip` tag（见上方 WARNING，不要用 Glob/Grep）
2. **找到 1 个** → 自动恢复该 session（按下方"恢复 Session"逻辑同时检查 progress.md 与 Excalidraw，跳到上次中断的 Step 继续）
3. **找到多个** → 列出所有 WIP session（显示题目名 + 开始日期 + 当前进度），问用户要继续哪个
4. **找到 0 个** → 回复: "没有进行中的练习。请指定题目，如 `/sysd-solve Design YouTube`"

找到要恢复的 session 后，按下方"恢复 Session（读取完整状态）"的逻辑继续。

---

### 有参数时

1. 从 `$ARGUMENTS` 提取题目简称（如 "Design YouTube" → "YouTube", "Bitly" → "Bitly"）
2. 用 shell `ls Learning/Practice/System-Design/Solutions/` 枚举所有 `<题目>-*` 文件夹（不要用 Glob/Grep，见上方 WARNING）:
   - **找到带 `system-design/wip` tag 的 progress.md** → 按下方"恢复 Session"逻辑同时检查 progress.md 与 Excalidraw，恢复到上次中断的位置继续（跳到对应 Step）
   - **找到带 `system-design/planned` tag 的 progress.md** → 将 tag 改为 `system-design/wip`，按下方"恢复 Session"逻辑同时检查 progress.md 与 Excalidraw，从记录的"下次继续"开始（全空时从 Step 1 开始）
   - **找到该题目的文件夹但都无 wip/planned tag** → 告诉用户这题已练习过 N 次，问是否重新练习
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

### 预创建路线题

学习计划可以提前创建尚未开始的 Solution 骨架。此类 `progress.md` 使用
`tags: [system-design/planned]`，六步保持全 ⬜：

- `planned` 不属于进行中 session，无参数 `/sysd-solve` 不应列出或自动恢复它。
- 用户指定该题时，按上方"有参数时"规则先切换为 `system-design/wip`，再开始引导。
- Dashboard 中 `planned` 显示为未开始，但可通过已存在的 progress 文件进入题目。

### 恢复 Session（读取完整状态）

> [!WARNING] 恢复任何 session 时（无参数自动恢复 / 有参数命中 wip / 有参数命中 planned）**禁止只读 progress.md**。用户可能已经直接在 Excalidraw 画布上写了 FR/NFR/BoE/Core Entities/API 等草稿，但还没同步回 progress.md——只读 progress.md 会重复提问用户已经想清楚的内容。

1. `Read` 该 session 的 `progress.md`，获取 Progress 表、Pending Questions、Key Learnings、下次继续
2. `Read` 同文件夹下的 `<题目>.excalidraw.md`，查看 `## Text Elements` 到 `%%` 之间的文字内容（这是未压缩的画布文字，不需要解压 `Drawing` 部分的 compressed-json）
3. **对比两者**：
   - Excalidraw 里有 progress.md 未记录或不一致的内容 → 先更新 progress.md（对应 Step 的 Notes、Key Learnings 补齐 Excalidraw 里的草稿），再继续引导
   - 两者一致 → 直接按 progress.md 的"下次继续"恢复引导
4. 从"下次继续"记录的位置接着引导，**不要重复提问 Excalidraw 里已经写清楚的内容**——只针对缺失或空白的部分继续引导

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
3. 按 6 步框架引导，**不直接给完整设计**
4. 用 targeted questions 引导用户思考每一步

**引导原则:**
- 从 Requirements 开始: "这个系统最核心的 3 个功能是什么？非功能需求呢？"
- 引导估算（在 Step 1 中完成）: "DAU 大概多少？读写比例？存储量级？"
- 逐步深入: Core Entities → API → Data Flow → High-Level Design → Deep Dives
- 如果用户卡住超过 2 轮，给更直接的 hint（但仍非完整方案）
- 只在用户说 "show me the design" / "给我看方案" / "我放弃" 时给完整设计
- 组织提问方向时参考 `Learning/Practice/System-Design/CLAUDE.md` 的「核心原则」（从需求推导架构、Trade-off 思维、数字感、渐进式设计）

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

5. **引用 Design Patterns / Key Technologies 建筑块文档**（若该题对应学习计划路线的主练项）:
   - 检查 `Learning/Plans/<CODE>/00_map.md`（如存在）中该题对应的 Design Pattern / Key Technology 条目
   - 在 Log 对应 section 里加上到 `Design Patterns/<pattern>.md`、`Key Technologies/<tech>.md` 的 wikilink 引用
   - 这些文档的正文由用户自行维护，**不在此步骤编写或补充内容**；文档应在开始这道题之前就已备好
   - 若发现对应文档不存在或明显是空壳，告知用户一声即可，不要自动补写

6. **标记完成**:
   - 将 Solution `progress.md` 的状态 tag 从 `system-design/wip` 替换为 `system-design/done`
   - 保留 progress、Excalidraw、Pattern Card、Log 和 Design Pattern/Key Technology 文档作为完整练习记录

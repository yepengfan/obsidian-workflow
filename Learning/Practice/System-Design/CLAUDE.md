# System Design Module — Claude Code Instructions

> 继承 vault root CLAUDE.md 的通用约定。

## Directory Configuration

| Path | Purpose |
|------|---------|
| `Learning/Practice/System-Design/Solutions/<题目>/` | Solution folder（每题一个，含 progress.md + Excalidraw） |
| `Learning/Practice/System-Design/Patterns/` | Pattern card 文件（一个 pattern 一个 .md） |
| `Learning/Practice/System-Design/Core Concepts/` | 核心概念 reference（Caching, Sharding, CAP Theorem, etc.） |
| `Learning/Practice/System-Design/Key Technologies/` | 技术 building block 文章（Redis, Kafka, etc.） |
| `Learning/Practice/System-Design/Design Patterns/` | 设计模式 building block 文章（Scaling Reads, Real-time Updates, etc.） |
| `Learning/Practice/System-Design/Insights/` | 练习中沉淀的具体知识点和经验总结 |
| `Learning/Practice/System-Design/Log/` | 每次练习记录 |
| `Learning/Practice/System-Design/Courses/` | 课程笔记（Hello Interview 等） |
| `Learning/Practice/System-Design/Attachments/` | 共享媒体（非题目专属的架构图、截图等） |
| `Learning/Practice/System-Design/00_index.md` | Dataview dashboard |
| `Templates/SD Pattern.md` | 新 pattern card 模板 |
| `Templates/SD Log.md` | 新 log 模板 |

## Solving Flow

1. 用户给题目（如 "Design YouTube"）→ 引导需求分析，**不直接给架构**
2. 按 Delivery Framework 6 步引导：Requirements → Core Entities → API → Data Flow → High-Level Design → Deep Dives
3. Step 5 时生成 Mermaid 架构图，与用户一起迭代
4. 用户说 "show me the design" / "给我看方案" / "我放弃" 时才给完整设计
5. 用户给出设计 → 审核合理性、trade-off 分析、改进建议
6. 通过后 → 沉淀 pattern card（含架构图）+ 写 log

## Pattern Card Rules

- **已有 pattern**: 加题名到 frontmatter `problems[]` + 正文 Problems 表格加一行 + 更新 `updated` 日期
- **新 pattern**: 创建新文件（用 `Templates/SD Pattern.md`），id 取当前最大值 +1，填充所有字段
- `difficulty` 指 pattern 理解难度，非单题难度
- 文件名 = pattern title（去掉文件系统非法字符 `/ \ : * ? " < > |`）
- `tags` 格式: `[system-design/pattern, system-design/{category-slug}]`

## Log Rules

- 每道题一个 `##` section
- 包含 pattern wikilink `[[pattern name]]`、difficulty、result emoji、notes、时间
- 包含 Requirements 小节（functional + non-functional）和 Key Decisions 小节
- frontmatter `problems_solved` 数组与正文 sections 保持一致
- 文件名: `YYYY-MM-DD.md`
- 如果当天 log 已存在，追加新 section（不覆盖）

## Category Values

合法 category 值（与 Dataview 分组键一致）:

- Storage & Database
- Caching
- Message Queue & Streaming
- Load Balancing & Networking
- API Design
- Consistency & Consensus
- Scaling & Partitioning
- Real-time & Push
- Search & Indexing
- Security & Auth
- Observability
- Microservices

## Solving 引导框架（Hello Interview Delivery Framework）

基于 Hello Interview 的 6 步 Delivery Framework。核心理念：前半段（1→5）满足功能需求，整个流程（1→6）满足非功能需求。

1. **Requirements** — 功能需求 + 非功能需求（QPS、延迟、可用性、一致性）+ Back-of-Envelope 估算
2. **Core Entities** — 识别核心实体和它们之间的关系（不是完整 schema，聚焦业务概念）
3. **API or Interface** — 核心接口定义（REST/gRPC/WebSocket，关注输入输出）
4. **Data Flow** — 数据如何在系统中流动（从用户请求到最终存储/返回的完整路径）
5. **High-Level Design** — 画出核心组件和连接关系（生成 Mermaid 架构图）
6. **Deep Dives** — 选 2-3 个组件深入，解决非功能需求（scaling、consistency、availability）

每一步先让用户思考，卡住时给 hint，不直接给答案。

> 详细框架笔记见 `[[Frameworks/Delivery Framework]]`

## Solution Folder Convention

每道系统设计题有自己的文件夹，所有 artifacts 集中管理：

```
Learning/Practice/System-Design/
├── Solutions/
│   ├── Bitly/
│   │   ├── progress.md          # 进度文件（tags: [system-design/wip]）
│   │   └── Bitly.excalidraw.md  # Excalidraw 画板
│   ├── YouTube/
│   │   ├── progress.md
│   │   └── YouTube.excalidraw.md
```

### 文件夹
- 路径: `Learning/Practice/System-Design/Solutions/<题目简称>/`
- **不要**在 vault 根目录 `Excalidraw/` 或 `Attachments/` 创建
- 练习完成（Phase 3 沉淀结束）后文件夹保留不动，作为学习记录

### progress.md
- frontmatter 必须有 `topic`, `started`, `tags: [system-design/wip]`
- 包含: Progress 表（Delivery Framework 每步状态）、Pending Questions、Key Learnings、下次继续步骤
- Home.md SD tab 自动检测带 `system-design/wip` tag 的 `progress.md` 并显示 "Continue →" 入口
- Phase 3 完成后移除 `system-design/wip` tag（文件保留）

### Excalidraw
- 命名: `<题目简称>.excalidraw.md`（如 `Bitly.excalidraw.md`）
- `/sysd/solve` 启动时自动创建，预填 Delivery Framework 6 步标题
- progress.md 通过 `![[...]]` 嵌入引用
- 使用未压缩 JSON 格式（`json` 代码块），Excalidraw 插件打开后自动压缩

### Excalidraw 模板生成

使用脚本生成：`node scripts/sd-excalidraw-template.js "<题目>"`
- 预填 Delivery Framework 6 步标题 + FR/NFR/Back-of-Envelope/Write Flow/Read Flow 子标题
- 输出未压缩 JSON 格式，Excalidraw 插件打开后自动压缩
- 修改模板布局请编辑 `scripts/sd-excalidraw-template.js`

## Diagram Conventions

- **Mermaid** 为主要画图工具，直接内嵌 Markdown，Obsidian 原生渲染
- 架构图用 `graph LR`（左到右流向）
- 用 `subgraph` 分组（Client / Server / Data Layer 等）
- 数据流标注协议/方向（HTTP, gRPC, Pub/Sub, CDC 等）
- 需要精细手绘版时用 Excalidraw，文件存 `Learning/Practice/System-Design/Attachments/`
- Pattern card 里的 Architecture Diagram section 存参考架构（Mermaid）
- Log 里的 Architecture section 存当次练习的架构快照（Mermaid）

## 与其他计划的关系

- **[[../../Plans/AISA/00_plan|AISA]]**: AI Solutions Architect，云架构方向
- **Algorithm**: LeetCode 刷题系统，训练编码能力
- **Frontend**: React/Next.js 前端练习

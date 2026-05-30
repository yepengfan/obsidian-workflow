# System Design Module — Claude Code Instructions

> 继承 vault root CLAUDE.md 的通用约定。

## Directory Configuration

| Path | Purpose |
|------|---------|
| `Learning/System-Design/Patterns/` | Pattern card 文件（一个 pattern 一个 .md） |
| `Learning/System-Design/Log/` | 每次练习记录 |
| `Learning/System-Design/Courses/` | 课程笔记（Hello Interview 等） |
| `Learning/System-Design/Attachments/` | 架构图、截图等媒体 |
| `Learning/System-Design/00_index.md` | Dataview dashboard |
| `Templates/SD Pattern.md` | 新 pattern card 模板 |
| `Templates/SD Log.md` | 新 log 模板 |

## Solving Flow

1. 用户给题目（如 "Design YouTube"）→ 引导需求分析，**不直接给架构**
2. 引导用户从 functional + non-functional requirements 出发
3. 逐步引导：API → 数据模型 → 高层架构 → 深入组件 → trade-offs
4. 用户说 "show me the design" / "给我看方案" / "我放弃" 时才给完整设计
5. 用户给出设计 → 审核合理性、trade-off 分析、改进建议
6. 通过后 → 沉淀 pattern card + 写 log

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

## Solving 引导框架（7 步）

引导用户走完 system design 的标准框架：

1. **Requirements Clarification** — 功能需求 + 非功能需求（QPS、延迟、可用性、一致性）
2. **Back-of-Envelope Estimation** — 流量、存储、带宽估算
3. **API Design** — 核心接口定义
4. **Data Model** — 数据库选型 + schema 设计
5. **High-Level Design** — 画出核心组件和数据流
6. **Deep Dive** — 选 2-3 个组件深入（用户选或引导）
7. **Trade-offs & Bottlenecks** — 瓶颈分析 + 改进方向

每一步先让用户思考，卡住时给 hint，不直接给答案。

## 与其他计划的关系

- **[[../SYSD/00_plan|SYSD]]**: 实战计划（Docker POC + 项目），提供动手经验
- **[[../AISA/00_plan|AISA]]**: AI Solutions Architect，云架构方向
- **Algorithm**: LeetCode 刷题系统，训练编码能力

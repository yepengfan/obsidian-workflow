---
title: "Fundamentals of Software Architecture — Full Map"
updated: 2026-03-17
---

# Fundamentals of Software Architecture — Full Map

> 用来追踪整本书的结构和章节间的关系。随阅读进度持续更新。

## Part I: Foundations

> 定义什么是软件架构，架构师如何思考，以及评估架构的核心度量体系。

- [[chapters/Ch01_Introduction|1. Introduction]]
- [[chapters/Ch02_Architectural Thinking|2. Architectural Thinking]]
- [[chapters/Ch03_Modularity|3. Modularity]]
- [[chapters/Ch04_Architecture Characteristics Defined|4. Architecture Characteristics Defined]]
- [[chapters/Ch05_Identifying Architectural Characteristics|5. Identifying Architectural Characteristics]]
- [[chapters/Ch06_Measuring and Governing Architecture Characteristics|6. Measuring and Governing Architecture Characteristics]]
- [[chapters/Ch07_Scope of Architecture Characteristics|7. Scope of Architecture Characteristics]]
- [[chapters/Ch08_Component-Based Thinking|8. Component-Based Thinking]]

## Part II: Architecture Styles

> 从单体到分布式，系统性介绍 8 种架构风格的结构、适用场景和 trade-offs。

- [[chapters/Ch09_Foundations|9. Foundations (Architecture Styles Overview)]]
- [[chapters/Ch10_Layered Architecture Style|10. Layered Architecture Style]]
- [[chapters/Ch11_Pipeline Architecture Style|11. Pipeline Architecture Style]]
- [[chapters/Ch12_Microkernel Architecture Style|12. Microkernel Architecture Style]]
- [[chapters/Ch13_Service-Based Architecture Style|13. Service-Based Architecture Style]]
- [[chapters/Ch14_Event-Driven Architecture Style|14. Event-Driven Architecture Style]]
- [[chapters/Ch15_Space-Based Architecture Style|15. Space-Based Architecture Style]]
- [[chapters/Ch16_Orchestration-Driven Service-Oriented Architecture|16. Orchestration-Driven Service-Oriented Architecture]]
- [[chapters/Ch17_Microservices Architecture|17. Microservices Architecture]]
- [[chapters/Ch18_Choosing the Appropriate Architecture Style|18. Choosing the Appropriate Architecture Style]]

## Part III: Techniques and Soft Skills

> 架构决策方法论、风险分析、沟通表达，以及架构师的职业发展。

- [[chapters/Ch19_Architecture Decisions|19. Architecture Decisions]]
- [[chapters/Ch20_Analyzing Architecture Risk|20. Analyzing Architecture Risk]]
- [[chapters/Ch21_Diagramming and Presenting Architecture|21. Diagramming and Presenting Architecture]]
- [[chapters/Ch22_Making Teams Effective|22. Making Teams Effective]]
- [[chapters/Ch23_Negotiation and Leadership Skills|23. Negotiation and Leadership Skills]]
- [[chapters/Ch24_Developing a Career Path|24. Developing a Career Path]]

## Appendix A: Self-Assessment Questions

> 每章的自测题，用于费曼测试前的自我检查。

- [[chapters/Ch25_Chapter1 Introduction|Ch1 自测题]]
- [[chapters/Ch26_Chapter2 Architectural Thinking|Ch2 自测题]]
- [[chapters/Ch27_Chapter3 Modularity|Ch3 自测题]]
- [[chapters/Ch28_Chapter4 Architecture Characteristics Defined|Ch4 自测题]]
- [[chapters/Ch29_Chapter5 Identifying Architecture Characteristics|Ch5 自测题]]
- [[chapters/Ch30_Chapter6 Measuring and Governing Architecture Characteristics|Ch6 自测题]]
- [[chapters/Ch31_Chapter7 Scope of Architecture Characteristics|Ch7 自测题]]
- [[chapters/Ch32_Chapter8 Component-Based Thinking|Ch8 自测题]]
- [[chapters/Ch33_Chapter9 Architecture Styles|Ch9 自测题]]
- [[chapters/Ch34_Chapter10 Layered Architecture Style|Ch10 自测题]]
- [[chapters/Ch35_Chapter11 Pipeline Architecture|Ch11 自测题]]
- [[chapters/Ch36_Chapter12 Microkernel Architecture|Ch12 自测题]]
- [[chapters/Ch37_Chapter13 Service-Based Architecture|Ch13 自测题]]
- [[chapters/Ch38_Chapter14 Event-Driven Architecture Style|Ch14 自测题]]
- [[chapters/Ch39_Chapter15 Space-Based Architecture|Ch15 自测题]]
- [[chapters/Ch40_Chapter16 Orchestration-Driven Service-Oriented Architecture|Ch16 自测题]]
- [[chapters/Ch41_Chapter17 Microservices Architecture|Ch17 自测题]]
- [[chapters/Ch42_Chapter18 Choosing the Appropriate Architecture Style|Ch18 自测题]]
- [[chapters/Ch43_Chapter19 Architecture Decisions|Ch19 自测题]]
- [[chapters/Ch44_Chapter20 Analyzing Architecture Risk|Ch20 自测题]]
- [[chapters/Ch45_Chapter21 Diagramming and Presenting Architecture|Ch21 自测题]]
- [[chapters/Ch46_Chapter22 Making Teams Effective|Ch22 自测题]]
- [[chapters/Ch47_Chapter23 Negotiation and Leadership Skills|Ch23 自测题]]
- [[chapters/Ch48_Chapter24 Developing a Career Path|Ch24 自测题]]

---

## 核心概念网络

### 跨章节概念表

| 核心概念 | 首次出现 | 跨章节关联 | 说明 |
|---------|---------|-----------|------|
| **Trade-off Analysis** | [[chapters/Ch01_Introduction\|Ch1]] | Ch2, Ch9, Ch10-17, Ch18, Ch19 | 全书第一定律："Everything in software architecture is a trade-off." 贯穿每一个架构决策 |
| **Architecture Characteristics (-ilities)** | [[chapters/Ch04_Architecture Characteristics Defined\|Ch4]] | Ch5, Ch6, Ch7, Ch9-17, Ch18, Ch20 | 可用性、可扩展性、性能等非功能性需求，是评估和选择架构风格的核心维度 |
| **Coupling / Connascence** | [[chapters/Ch03_Modularity\|Ch3]] | Ch7, Ch9, Ch13, Ch14, Ch17 | 从代码级耦合（connascence）到架构级耦合（同步/异步通信），是分布式系统的核心矛盾 |
| **Architecture Quantum** | [[chapters/Ch07_Scope of Architecture Characteristics\|Ch7]] | Ch9, Ch13, Ch17, Ch18 | 独立可部署的最小架构单元，决定了架构特性的作用域边界 |
| **Fitness Functions** | [[chapters/Ch06_Measuring and Governing Architecture Characteristics\|Ch6]] | Ch3, Ch20 | 可执行的架构治理机制，用于自动化验证架构特性是否被维护 |
| **Partitioning (Technical vs Domain)** | [[chapters/Ch08_Component-Based Thinking\|Ch8]] | Ch10, Ch13, Ch17, Ch18 | 按技术层 vs 按业务域划分组件，是区分 Layered 和 Microservices 等风格的关键分界线 |
| **Synchronous vs Asynchronous Communication** | [[chapters/Ch09_Foundations\|Ch9]] | Ch13, Ch14, Ch15, Ch17 | 分布式架构的核心选择：同步简单但耦合强，异步解耦但复杂度高 |
| **Distributed Computing Fallacies** | [[chapters/Ch09_Foundations\|Ch9]] | Ch13-17 | 分布式系统的 8 个经典谬误，解释了为什么单体到分布式不是"免费升级" |
| **Conway's Law** | [[chapters/Ch01_Introduction\|Ch1]] | Ch17, Ch22 | 系统架构映射组织结构。Microservices 成功的前提往往是团队结构先到位 |
| **Architecture Decision Records (ADR)** | [[chapters/Ch19_Architecture Decisions\|Ch19]] | Ch2, Ch18, Ch20 | 记录架构决策的 why，而非 what。避免 Groundhog Day 反模式 |

### 全书暗线

```
Everything is a trade-off（第一定律）
        │
        ▼
┌─ Part I: 建立评估框架 ──────────────────────────────┐
│  什么是架构？→ 如何思考？→ 如何度量？→ 度量的边界？   │
│  Ch1 定义    Ch2 思维     Ch3-6 特性    Ch7 Quantum  │
│              Ch8 组件划分                              │
└──────────────────────────────────────────────────────┘
        │
        ▼
┌─ Part II: 应用评估框架到具体架构 ───────────────────┐
│  单体                    分布式                      │
│  Ch10 Layered     →     Ch13 Service-Based           │
│  Ch11 Pipeline    →     Ch14 Event-Driven            │
│  Ch12 Microkernel →     Ch15 Space-Based             │
│                         Ch16 SOA (反面教材)           │
│                         Ch17 Microservices            │
│  Ch9 基础分类      →    Ch18 如何选择                 │
└──────────────────────────────────────────────────────┘
        │
        ▼
┌─ Part III: 从技术到人 ─────────────────────────────┐
│  Ch19 决策方法 → Ch20 风险分析 → Ch21 表达沟通      │
│  Ch22 团队协作 → Ch23 领导力   → Ch24 职业发展      │
│  「架构师不只是技术角色，更是组织中的连接者」          │
└────────────────────────────────────────────────────┘
```

### 架构风格对比矩阵

| 架构风格 | 拓扑类型 | 分区方式 | 部署单元 | 通信方式 | 适用场景 |
|---------|---------|---------|---------|---------|---------|
| **Layered** (Ch10) | Monolithic | Technical | 1 | N/A | 小型应用、原型 |
| **Pipeline** (Ch11) | Monolithic | Technical | 1 | N/A | ETL、数据流处理 |
| **Microkernel** (Ch12) | Monolithic | Domain (plugins) | 1 | In-process | 可扩展产品（IDE、浏览器） |
| **Service-Based** (Ch13) | Distributed | Domain | 4-12 services | Sync (REST) | 务实的分布式起点 |
| **Event-Driven** (Ch14) | Distributed | Domain/Technical | Varies | Async (events) | 高吞吐、松耦合异步场景 |
| **Space-Based** (Ch15) | Distributed | Domain | Processing units | Async (replication) | 极端弹性需求（秒杀、直播） |
| **SOA** (Ch16) | Distributed | Technical (ESB) | Varies | Sync (SOAP/ESB) | ⚠️ 历史产物，已过时 |
| **Microservices** (Ch17) | Distributed | Domain (bounded context) | Per-service | Sync + Async | 大规模独立演进的系统 |

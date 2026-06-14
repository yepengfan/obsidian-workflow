---
title: "Designing Data-Intensive Applications (2nd Edition) — Full Map"
updated: 2026-03-07
---

# Designing Data-Intensive Applications (2nd Edition) — Full Map

> 用来追踪整本书的结构和章节间的关系。随阅读进度持续更新。

## Chapters
- [[chapters/Ch01_Trade-Offs in Data Systems Architecture|1. Trade-Offs in Data Systems Architecture]]
- [[chapters/Ch02_Defining Nonfunctional Requirements|2. Defining Nonfunctional Requirements]]
- [[chapters/Ch03_Data Models and Query Languages|3. Data Models and Query Languages]]
- [[chapters/Ch04_Storage and Retrieval|4. Storage and Retrieval]]
- [[chapters/Ch05_Encoding and Evolution|5. Encoding and Evolution]]
- [[chapters/Ch06_Replication|6. Replication]]
- [[chapters/Ch07_Sharding|7. Sharding]]
- [[chapters/Ch08_Transactions|8. Transactions]]
- [[chapters/Ch09_The Trouble with Distributed Systems|9. The Trouble with Distributed Systems]]
- [[chapters/Ch10_Consistency and Consensus|10. Consistency and Consensus]]
- [[chapters/Ch11_Batch Processing|11. Batch Processing]]
- [[chapters/Ch12_Stream Processing|12. Stream Processing]]
- [[chapters/Ch13_A Philosophy of Streaming Systems|13. A Philosophy of Streaming Systems]]
- [[chapters/Ch14_Doing the Right Thing|14. Doing the Right Thing]]

## 核心概念网络

### Data System Foundations

| Concept | One-liner | Related Chapters |
|---------|-----------|-----------------|
| Reliability | The system works correctly even when faults occur | [[chapters/Ch01_Trade-Offs in Data Systems Architecture\|Ch1]], [[chapters/Ch02_Defining Nonfunctional Requirements\|Ch2]], [[chapters/Ch09_The Trouble with Distributed Systems\|Ch9]] |
| Scalability | The ability to handle growing load by adding resources | [[chapters/Ch01_Trade-Offs in Data Systems Architecture\|Ch1]], [[chapters/Ch02_Defining Nonfunctional Requirements\|Ch2]], [[chapters/Ch07_Sharding\|Ch7]] |
| Maintainability | Making the system easy to operate, understand, and evolve over time | [[chapters/Ch01_Trade-Offs in Data Systems Architecture\|Ch1]], [[chapters/Ch02_Defining Nonfunctional Requirements\|Ch2]], [[chapters/Ch05_Encoding and Evolution\|Ch5]] |
| Trade-offs | Every design decision involves giving up something to gain something else | [[chapters/Ch01_Trade-Offs in Data Systems Architecture\|Ch1]], [[chapters/Ch06_Replication\|Ch6]], [[chapters/Ch08_Transactions\|Ch8]] |

### Data Models

| Concept | One-liner | Related Chapters |
|---------|-----------|-----------------|
| Relational Model | Data organized into tables with rows and columns, queried with SQL | [[chapters/Ch03_Data Models and Query Languages\|Ch3]], [[chapters/Ch04_Storage and Retrieval\|Ch4]] |
| Document Model | Self-contained JSON/XML documents with flexible schemas | [[chapters/Ch03_Data Models and Query Languages\|Ch3]], [[chapters/Ch05_Encoding and Evolution\|Ch5]] |
| Graph Model | Data modeled as vertices and edges for highly connected relationships | [[chapters/Ch03_Data Models and Query Languages\|Ch3]] |
| Event Sourcing | Storing every change as an immutable event rather than overwriting state | [[chapters/Ch03_Data Models and Query Languages\|Ch3]], [[chapters/Ch12_Stream Processing\|Ch12]], [[chapters/Ch13_A Philosophy of Streaming Systems\|Ch13]] |

### Storage Engines

| Concept | One-liner | Related Chapters |
|---------|-----------|-----------------|
| LSM-Trees | Write-optimized structure that buffers writes in memory then flushes sorted runs to disk | [[chapters/Ch04_Storage and Retrieval\|Ch4]] |
| B-Trees | Read-optimized balanced tree structure used by most relational databases | [[chapters/Ch04_Storage and Retrieval\|Ch4]] |
| Column Storage | Storing data by column rather than by row for analytical query efficiency | [[chapters/Ch04_Storage and Retrieval\|Ch4]], [[chapters/Ch11_Batch Processing\|Ch11]] |
| Indexes | Additional data structures that speed up reads at the cost of slower writes | [[chapters/Ch04_Storage and Retrieval\|Ch4]], [[chapters/Ch07_Sharding\|Ch7]] |

### Encoding and Evolution

| Concept | One-liner | Related Chapters |
|---------|-----------|-----------------|
| Schema Evolution | Changing data schemas over time while maintaining backward/forward compatibility | [[chapters/Ch05_Encoding and Evolution\|Ch5]], [[chapters/Ch03_Data Models and Query Languages\|Ch3]] |
| Protobuf / Avro | Binary encoding formats that support compact serialization with schema evolution | [[chapters/Ch05_Encoding and Evolution\|Ch5]] |
| Dataflow Modes | Patterns for how data moves between processes: via databases, services, or messages | [[chapters/Ch05_Encoding and Evolution\|Ch5]], [[chapters/Ch12_Stream Processing\|Ch12]] |
| Backward/Forward Compatibility | New code reads old data (backward); old code reads new data (forward) | [[chapters/Ch05_Encoding and Evolution\|Ch5]] |

### Distributed Replication

| Concept | One-liner | Related Chapters |
|---------|-----------|-----------------|
| Leader-based Replication | One node accepts writes, followers replicate asynchronously or synchronously | [[chapters/Ch06_Replication\|Ch6]], [[chapters/Ch10_Consistency and Consensus\|Ch10]] |
| Conflict Resolution | Strategies for handling concurrent writes in multi-leader or leaderless systems | [[chapters/Ch06_Replication\|Ch6]], [[chapters/Ch10_Consistency and Consensus\|Ch10]] |
| Leaderless Replication | Any node can accept writes; quorum reads/writes ensure consistency | [[chapters/Ch06_Replication\|Ch6]], [[chapters/Ch09_The Trouble with Distributed Systems\|Ch9]] |
| Replication Lag | Delay between a write on the leader and its visibility on followers | [[chapters/Ch06_Replication\|Ch6]], [[chapters/Ch08_Transactions\|Ch8]] |

### Sharding (Partitioning)

| Concept | One-liner | Related Chapters |
|---------|-----------|-----------------|
| Partitioning Strategies | Key-range vs. hash partitioning to distribute data across nodes | [[chapters/Ch07_Sharding\|Ch7]], [[chapters/Ch06_Replication\|Ch6]] |
| Rebalancing | Moving data between partitions when nodes are added or removed | [[chapters/Ch07_Sharding\|Ch7]] |
| Secondary Indexes | Local vs. global indexes on partitioned data and their query trade-offs | [[chapters/Ch07_Sharding\|Ch7]], [[chapters/Ch04_Storage and Retrieval\|Ch4]] |

### Transactions

| Concept | One-liner | Related Chapters |
|---------|-----------|-----------------|
| ACID | Atomicity, Consistency, Isolation, Durability — the safety guarantees of transactions | [[chapters/Ch08_Transactions\|Ch8]] |
| Isolation Levels | Read committed, snapshot isolation, serializability — degrees of concurrency protection | [[chapters/Ch08_Transactions\|Ch8]], [[chapters/Ch10_Consistency and Consensus\|Ch10]] |
| Serializability | The strongest isolation level: transactions behave as if executed sequentially | [[chapters/Ch08_Transactions\|Ch8]] |
| Two-Phase Commit (2PC) | Protocol for atomic commit across multiple nodes, at the cost of availability | [[chapters/Ch08_Transactions\|Ch8]], [[chapters/Ch10_Consistency and Consensus\|Ch10]] |

### Distributed Systems Challenges

| Concept | One-liner | Related Chapters |
|---------|-----------|-----------------|
| Network Faults | Packets can be lost, delayed, duplicated, or reordered — you cannot tell if a node is down | [[chapters/Ch09_The Trouble with Distributed Systems\|Ch9]], [[chapters/Ch06_Replication\|Ch6]] |
| Clock Issues | Physical clocks drift; relying on timestamps for ordering is fundamentally unreliable | [[chapters/Ch09_The Trouble with Distributed Systems\|Ch9]], [[chapters/Ch10_Consistency and Consensus\|Ch10]] |
| Byzantine Faults | Nodes that lie or behave maliciously, the hardest class of faults to tolerate | [[chapters/Ch09_The Trouble with Distributed Systems\|Ch9]], [[chapters/Ch14_Doing the Right Thing\|Ch14]] |

### Consistency and Consensus

| Concept | One-liner | Related Chapters |
|---------|-----------|-----------------|
| Linearizability | The system behaves as if there is a single copy of the data with atomic operations | [[chapters/Ch10_Consistency and Consensus\|Ch10]], [[chapters/Ch08_Transactions\|Ch8]] |
| Logical Clocks | Lamport timestamps and vector clocks that capture causal ordering without physical time | [[chapters/Ch10_Consistency and Consensus\|Ch10]], [[chapters/Ch09_The Trouble with Distributed Systems\|Ch9]] |
| Consensus Protocols | Algorithms (Raft, Paxos, Zab) for getting distributed nodes to agree on a value | [[chapters/Ch10_Consistency and Consensus\|Ch10]] |
| CAP / PACELC | Trade-offs between consistency and availability under network partitions | [[chapters/Ch10_Consistency and Consensus\|Ch10]], [[chapters/Ch06_Replication\|Ch6]], [[chapters/Ch09_The Trouble with Distributed Systems\|Ch9]] |

### Batch and Stream Processing

| Concept | One-liner | Related Chapters |
|---------|-----------|-----------------|
| MapReduce | A programming model for processing large datasets in parallel across a cluster | [[chapters/Ch11_Batch Processing\|Ch11]] |
| Dataflow Engines | Systems like Spark that generalize MapReduce with arbitrary DAGs of operators | [[chapters/Ch11_Batch Processing\|Ch11]], [[chapters/Ch12_Stream Processing\|Ch12]] |
| Stream Processing | Continuously processing unbounded data as events arrive in real time | [[chapters/Ch12_Stream Processing\|Ch12]], [[chapters/Ch13_A Philosophy of Streaming Systems\|Ch13]] |
| Change Data Capture (CDC) | Capturing row-level changes from a database log and propagating them as a stream | [[chapters/Ch12_Stream Processing\|Ch12]], [[chapters/Ch13_A Philosophy of Streaming Systems\|Ch13]], [[chapters/Ch06_Replication\|Ch6]] |

### System Philosophy

| Concept | One-liner | Related Chapters |
|---------|-----------|-----------------|
| Data Integration | Combining data from heterogeneous sources into a coherent, queryable whole | [[chapters/Ch13_A Philosophy of Streaming Systems\|Ch13]], [[chapters/Ch11_Batch Processing\|Ch11]] |
| Unbundling Databases | Decomposing monolithic database functionality into composable stream-based components | [[chapters/Ch13_A Philosophy of Streaming Systems\|Ch13]], [[chapters/Ch12_Stream Processing\|Ch12]] |
| End-to-end Correctness | Exactly-once semantics require end-to-end design, not just transport-level guarantees | [[chapters/Ch13_A Philosophy of Streaming Systems\|Ch13]], [[chapters/Ch08_Transactions\|Ch8]], [[chapters/Ch14_Doing the Right Thing\|Ch14]] |
| Ethics of Data Systems | Responsibility, privacy, fairness, and societal impact of the systems we build | [[chapters/Ch14_Doing the Right Thing\|Ch14]] |

---

### 全书暗线

```
Foundations (Ch1-2)          What makes a "good" data system? Reliability, scalability, maintainability.
        ↓
Single-Node Internals (Ch3-5)   How data is modeled, stored, and encoded on one machine.
        ↓
Distribution (Ch6-10)        What breaks when you go distributed: replication, sharding,
                             transactions, faults, consistency, and consensus.
        ↓
Processing Paradigms (Ch11-13)  How to derive value from data at scale: batch, stream, and
                             the philosophy of composing data systems.
        ↓
Responsibility (Ch14)        With great data power comes great ethical responsibility.
```

> **贯穿全书的问题：** 在不可靠的组件之上，如何构建可靠、可扩展、可维护的数据系统——以及在构建这些系统时，我们对使用者和社会负有怎样的责任？

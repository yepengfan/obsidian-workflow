# Chapter 6: Design Ad Click Event Aggregation

## 问题定义

为 Facebook/Google 级别的广告系统设计点击事件实时聚合系统，用于 RTB（Real-Time Bidding）计费和效果衡量。

**核心需求：**
- 聚合每个 `ad_id` 在过去 M 分钟内的点击数
- 返回过去 M 分钟内点击量 Top N 的广告
- 支持按 `ip`、`user_id`、`country` 等维度过滤
- 数据规模：10 亿 DAU，每日 10 亿次广告点击，200 万广告
- Peak QPS 约 50,000，日存储约 100 GB

**非功能需求：**
- 数据正确性极为重要（直接影响计费）
- 正确处理延迟到达和重复事件
- 系统对部分故障具有弹性（Robustness）
- 端到端延迟在几分钟以内

---

## 架构图索引

| Figure | 文件 | 内容 | 设计阶段 |
|--------|------|------|----------|
| 1 | ![Image00124.jpg](images/Image00124.jpg) | RTB（Real-Time Bidding）流程 | 背景知识 |
| 2 | ![Image00125.jpg](images/Image00125.jpg) | 聚合工作流：raw data → aggregation → aggregated results | 高层设计 |
| 3 | ![Image00126.jpg](images/Image00126.jpg) | **高层架构图**：Log Watcher → Message Queue → Aggregation Service → Message Queue → DB Writer → Aggregation DB，含 Raw data DB 分支和 Query Service (Dashboard) | 高层设计 |
| 4 | ![Image00127.jpg](images/Image00127.jpg) | End-to-end exactly-once 语义说明 | 高层设计 |
| 5 | ![Image00128.jpg](images/Image00128.jpg) | **Aggregation Service DAG 模型**：上半部分为每分钟 Ad count 聚合（Map → Aggregate → Ad count），下半部分为 Top 100 聚合（Map → Aggregate → Reduce → Top 100 Ads） | 深入设计 |
| 6 | ![Image00129.jpg](images/Image00129.jpg) | Map 操作：按 `ad_id % 2` 分区分发 | 深入设计 |
| 7 | ![Image00130.jpg](images/Image00130.jpg) | Reduce 节点：将多个 Aggregate 节点的 Top 3 归并为最终 Top 3 | 深入设计 |
| 8 | ![Image00131.jpg](images/Image00131.jpg) | Use Case 1：按 `ad_id % 3` 分区聚合点击数 | 深入设计 |
| 9 | ![Image00132.jpg](images/Image00132.jpg) | Use Case 2：Top N 最多点击广告的完整流程 | 深入设计 |
| 10 | ![Image00133.jpg](images/Image00133.jpg) | Lambda vs Kappa 架构对比 | 深入设计 |
| 11 | ![Image00134.jpg](images/Image00134.jpg) | 数据重算（Recalculation）流程 | 深入设计 |
| 12 | ![Image00135.jpg](images/Image00135.jpg) | Late events：事件到达时间远晚于事件发生时间 | 深入设计 |
| 13 | ![Image00136.jpg](images/Image00136.jpg) | Tumbling window 中遗漏的迟到事件 | 深入设计 |
| 14 | ![Image00137.jpg](images/Image00137.jpg) | Watermark 机制：扩展聚合窗口以捕获迟到事件 | 深入设计 |
| 15 | ![Image00138.jpg](images/Image00138.jpg) | Tumbling Window（固定窗口）示意 | 深入设计 |
| 16 | ![Image00139.jpg](images/Image00139.jpg) | Sliding Window（滑动窗口）示意 | 深入设计 |
| 17 | ![Image00140.jpg](images/Image00140.jpg) | Aggregator 宕机导致重复数据的场景 | 深入设计 |
| 18 | ![Image00141.jpg](images/Image00141.jpg) | 使用外部存储记录 offset 的方案（有数据丢失风险） | 深入设计 |
| 19 | ![Image00142.jpg](images/Image00142.jpg) | 改进方案：收到下游 ack 后再保存 offset | 深入设计 |
| 20 | ![Image00143.jpg](images/Image00143.jpg) | 分布式事务实现 exactly-once 处理 | 深入设计 |
| 21 | ![Image00144.jpg](images/Image00144.jpg) | 扩展 Consumer：向 consumer group 添加更多消费者 | 扩展性 |
| 22 | ![Image00145.jpg](images/Image00145.jpg) | Aggregation Service 完整 MapReduce 拓扑 | 扩展性 |
| 23 | ![Image00146.jpg](images/Image00146.jpg) | 多线程处理：不同 `ad_id` 分配到不同线程 | 扩展性 |
| 24 | ![Image00147.jpg](images/Image00147.jpg) | Cassandra virtual nodes 数据分布 | 扩展性 |
| 25 | ![Image00148.jpg](images/Image00148.jpg) | Hotspot 缓解：Resource Manager 动态分配更多聚合节点 | 扩展性 |
| 26 | ![Image00149.jpg](images/Image00149.jpg) | Snapshot 数据示例（用于故障恢复） | 容错 |
| 27 | ![Image00150.jpg](images/Image00150.jpg) | Aggregation node failover：从 snapshot 恢复 | 容错 |
| 28 | ![Image00151.jpg](images/Image00151.jpg) | **最终设计图**：完整架构含 Log Watcher、两个 Message Queue、Aggregation Service、Raw data DB、Aggregation DB、Recalculation Service、Reconciliation、Query Service (Dashboard) | 最终设计 |
| 29 | ![Image00152.jpg](images/Image00152.jpg) | 替代设计：Hive + ElasticSearch + ClickHouse/Druid | 替代方案 |

---

## 设计思路演进

### Step 1: 数据模型与 API 设计

**两个核心 API：**
- `GET /v1/ads/{:ad_id}/aggregated_count` — 查询某广告在过去 M 分钟内的点击数
- `GET /v1/ads/popular_ads` — 查询过去 M 分钟内 Top N 点击广告

**数据存储策略：同时保留 raw data 和 aggregated data**
```
Raw data → 用于 debug、recalculation、数据科学分析（写入 Cassandra / S3）
Aggregated data → 用于实时查询和 Dashboard 展示（写入 Cassandra）
```

### Step 2: 高层架构 — 异步流处理

```
Log Watcher → Message Queue (Kafka) → Data Aggregation Service → Message Queue (Kafka) → DB Writer → Aggregation DB
                    ↓                                                                                      ↑
              DB Writer → Raw data DB                                                            Query Service (Dashboard)
```

**为什么需要两个 Message Queue？**
- 第一个 MQ：解耦生产者（Log Watcher）和消费者（Aggregation Service），应对流量突发
- 第二个 MQ：实现端到端 exactly-once 语义（atomic commit），聚合结果先写入 Kafka 再落库

### Step 3: MapReduce 聚合模型（DAG）

```
Data Input → Map（按 ad_id 分区）→ Aggregate（内存计数）→ Reduce（归并 Top N）→ 输出
```

- **Map 节点**：数据清洗、归一化，按 `ad_id % N` 路由到对应 Aggregate 节点
- **Aggregate 节点**：每分钟在内存中按 `ad_id` 计数，或用 Heap 维护 Top N
- **Reduce 节点**：将多个 Aggregate 节点的结果归并为最终结果

### Step 4: 时间语义与窗口策略

**Event time vs Processing time：**
- 选择 Event time（更准确，因为广告计费对数据精度要求极高）
- 使用 **Watermark** 技术处理迟到事件：扩展聚合窗口额外 15 秒（可调）

**窗口类型：**
- **Tumbling Window**（固定窗口）：适用于每分钟聚合 ad click count
- **Sliding Window**（滑动窗口）：适用于获取过去 M 分钟 Top N 广告

### Step 5: Exactly-once 与数据去重

```
问题：Aggregator 宕机 → offset 未更新 → 新 Aggregator 重复消费 → 重复数据
解法：将 offset 更新、聚合结果写入下游、ack 确认放入同一分布式事务
```

### Step 6: 数据重算与 Reconciliation

- **Recalculation**：发现 bug 后，从 raw data 重新跑聚合（使用独立的 Aggregation Service 实例，不影响实时流）
- **Reconciliation**：每日 batch job 按 event time 排序后重新聚合，与实时结果对比校验

---

## 关键设计考量 (Tradeoffs)

### 1. 存储选择：Raw data vs Aggregated data
- **Raw data only**：数据完整可回溯，但存储量巨大、查询慢
- **Aggregated data only**：数据量小、查询快，但信息有损、无法回溯
- **推荐方案**：两者都存。Raw data 作为备份和 recalculation 来源（冷存储降低成本），Aggregated data 用于在线查询

### 2. Event time vs Processing time
- **Event time**：聚合更准确，但需处理迟到事件（watermark）和潜在客户端时间篡改
- **Processing time**：服务端时间可靠，但事件延迟到达时结果不准确
- 因为计费精度要求高，选择 Event time + Watermark

### 3. Watermark 长度
- 长 watermark：捕获更多迟到事件 → 精度高，但增加系统延迟
- 短 watermark：延迟低，但可能遗漏更多迟到事件
- 极端迟到事件由 end-of-day reconciliation 修正

### 4. Lambda vs Kappa 架构
- **Lambda**：batch + streaming 双路径，精度高但需维护两套代码
- **Kappa**：统一用 streaming 处理实时和历史重算，代码维护成本低
- 本设计采用 Kappa 架构

### 5. Exactly-once 语义
- **At-most once**：可能丢数据 — 广告计费场景不可接受
- **At-least once**：可能重复 — 百分之几的偏差意味着百万美元差异
- **Exactly-once**：通过分布式事务保证（offset + 聚合结果 + ack 原子提交），实现复杂但计费必需

### 6. Hotspot 问题
- 大广告主点击量远超其他，导致某些 Aggregation 节点过载
- 解决方案：Resource Manager 动态分配更多聚合节点，拆分热点 ad_id 的事件
- 高级方案：Global-Local Aggregation、Split Distinct Aggregation

### 7. 数据库扩展
- Cassandra 原生支持水平扩展（virtual nodes + consistent hashing）
- 新增节点自动 rebalance，无需手动 resharding

### 8. Kafka 分区策略
- 以 `ad_id` 作为 hashing key，确保同一广告的事件落在同一 partition
- 预分配足够 partition 数量，避免生产环境动态扩 partition 导致数据错乱
- 可按地域或业务类型做 topic 物理分片（如 `topic_north_america`、`topic_mobile_ads`）

---

## 面试扩展话题

- **Streaming vs Batching**：理解 Online System / Batch System / Streaming System 三种系统的区别（响应性、输入、输出、性能指标）
- **Lambda vs Kappa 架构**：Lambda 双路径精度高但维护成本翻倍；Kappa 单路径统一处理，是本设计的选择
- **Star Schema 过滤**：通过预定义维度（country、IP 等）预聚合，查询时直接命中预计算结果；缺点是维度组合爆炸导致 bucket 数量激增
- **Watermark 调优**：根据业务对延迟和精度的容忍度调整 watermark 长度，配合 end-of-day reconciliation 兜底
- **Exactly-once 深度**：Kafka atomic commit、分布式事务、offset 管理的细节（参考 Apache Flink 的 exactly-once 实现）
- **Data deduplication**：客户端重复发送（恶意 / 网络重试）和服务端宕机恢复导致的重复，需要不同层面的去重策略
- **Fault tolerance**：Snapshot + Kafka replay 实现故障恢复，避免从头重放全量数据
- **Continuous monitoring**：跟踪每个阶段的 latency、Kafka records-lag、聚合节点的 CPU/Disk/JVM 资源
- **Reconciliation**：end-of-day batch job 对比实时聚合结果，确保数据完整性
- **替代设计**：Hive + ElasticSearch + ClickHouse/Druid 的 OLAP 方案，适合有大数据基础设施的团队

---

## 速写练习要点

盲画时重点记住这些组件和连接：

1. **核心数据流**：Log Watcher → Kafka (MQ1) → Aggregation Service → Kafka (MQ2) → DB Writer → Aggregation DB
2. **Raw data 分支**：MQ1 → DB Writer → Raw data DB（备份 + recalculation 来源）
3. **MapReduce DAG**：Map（分区）→ Aggregate（计数/Top N heap）→ Reduce（归并最终结果）
4. **Recalculation 路径**：Raw data DB → Recalculation Service → 独立 Aggregation Service → MQ2 → Aggregation DB
5. **Reconciliation**：batch job 从 raw data 重新聚合，与 Aggregation DB 中的实时结果对比
6. **Query Service (Dashboard)**：从 Aggregation DB 查询，向广告主/数据分析师提供聚合数据
7. **Exactly-once 关键**：两个 Kafka 之间的 Aggregation Service 通过分布式事务保证 offset + 结果 + ack 原子提交

# Chapter 4: Design a Distributed Message Queue

## 问题定义

设计一个分布式消息队列（Distributed Message Queue），兼具传统消息队列和 Event Streaming Platform 的能力。

**消息队列的核心价值：**
- **Decoupling**：组件解耦，独立更新
- **Scalability**：Producer 和 Consumer 可独立扩缩容
- **Availability**：部分组件下线不影响其余组件与队列的交互
- **Performance**：异步通信，Producer 无需等待 Consumer 响应

**功能需求：**
- Producer 发送消息到队列，Consumer 从队列消费消息
- 消息可重复消费（repeated consumption）或仅消费一次
- 历史数据可按策略截断（data retention = 2 weeks）
- 消息大小在 KB 级别
- 保证同一 Partition 内的消息顺序（ordering）
- 数据交付语义（at-least-once / at-most-once / exactly-once）可配置

**非功能需求：**
- 高吞吐（High Throughput）或低延迟（Low Latency），按场景配置
- 分布式、可水平扩展，应对突发流量
- 持久化 + 多副本复制（Persistent & Durable）

---

## 架构图索引

| Figure | 文件 | 内容 | 设计阶段 |
|--------|------|------|----------|
| 4-1 | ![Image00066](images/Image00066.jpg) | 市场上流行的分布式消息队列产品（Kafka, Pulsar, RocketMQ 等） | 背景 |
| 4-2 | ![Image00067](images/Image00067.jpg) | 消息队列核心组件：Producer → Message Queue → Consumer | 高层设计 |
| 4-3 | ![Image00068](images/Image00068.jpg) | Point-to-Point 模型：一条消息仅被一个 Consumer 消费 | 消息模型 |
| 4-4 | ![Image00069](images/Image00069.jpg) | Publish-Subscribe 模型：一条消息被多个订阅者消费 | 消息模型 |
| 4-5 | ![Image00070](images/Image00070.gif) | Partition 分区示意：Topic 划分为多个 Partition，分布在不同 Broker | 高层设计 |
| 4-6 | ![Image00071](images/Image00071.jpg) | 消息队列集群：Broker 持有 Partition，Producer/Consumer 交互 | 高层设计 |
| 4-7 | ![Image00072](images/Image00072.gif) | Consumer Group：多组消费者并行消费多个 Topic 和 Partition | 高层设计 |
| 4-8 | ![Image00073](images/Image00073.jpg) | **高层架构图**：Producer → Broker（Data/State Storage）→ Consumer + Metadata Storage + Coordination Service | 高层设计 |
| 4-9 | ![Image00074](images/Image00074.jpg) | WAL Append-only Log：消息追加到 Partition 尾部，offset 单调递增 | 深入设计 |
| 4-10 | ![Image00075](images/Image00075.gif) | Segment 文件结构：Partition 目录下的多个 Segment 文件 | 深入设计 |
| 4-11 | ![Image00076](images/Image00076.jpg) | Routing Layer：Producer → Routing Layer → Leader Replica | 深入设计 |
| 4-12 | ![Image00077](images/Image00077.jpg) | 改进设计：Routing + Buffer 内置到 Producer Client Library | 深入设计 |
| 4-13 | ![Image00078](images/Image00078.jpg) | Batch Size Tradeoff：大 batch 高吞吐高延迟 vs 小 batch 低延迟低吞吐 | 深入设计 |
| 4-14 | ![Image00079](images/Image00079.jpg) | Consumer Flow：指定 offset 拉取一段消息 | 深入设计 |
| 4-15 | ![Image00080](images/Image00080.jpg) | **Consumer Pull 模型流程**：Consumer join group → Coordinator 分配 Partition → fetch → commit offset | 深入设计 |
| 4-16 | ![Image00081](images/Image00081.jpg) | Consumer Group Coordinator：各 Consumer 通过 hash(group) 找到 Coordinator Broker | 深入设计 |
| 4-17 | ![Image00082](images/Image00082.jpg) | Consumer Rebalance 触发流程 | 深入设计 |
| 4-18 | ![Image00083](images/Image00083.jpg) | 新 Consumer 加入 Group 的 Rebalance 步骤 | 深入设计 |
| 4-19 | ![Image00084](images/Image00084.jpg) | Consumer 主动离开 Group 的 Rebalance 步骤 | 深入设计 |
| 4-20 | ![Image00085](images/Image00085.jpg) | Consumer 崩溃后的 Rebalance 步骤（心跳超时触发） | 深入设计 |
| 4-21 | ![Image00086](images/Image00086.gif) | State Storage：Consumer Group 的 last consumed offset | 深入设计 |
| 4-22 | ![Image00087](images/Image00087.jpg) | ZooKeeper 简化设计：Metadata + State 存入 ZooKeeper | 深入设计 |
| 4-23 | ![Image00088](images/Image00088.jpg) | **Replication 副本分布**：每个 Partition 3 副本分布在不同 Broker，高亮为 Leader | 深入设计 |
| 4-24 | ![Image00089](images/Image00089.jpg) | ISR（In-Sync Replicas）工作原理：Leader committed offset + Follower 同步进度 | 深入设计 |
| 4-25 | ![Image00090](images/Image00090.jpg) | ACK=all：所有 ISR 同步后才返回确认 | 深入设计 |
| 4-26 | ![Image00091](images/Image00091.jpg) | ACK=1：Leader 写入后即确认 | 深入设计 |
| 4-27 | ![Image00092](images/Image00092.jpg) | ACK=0：Producer 不等待确认 | 深入设计 |
| 4-28 | ![Image00093](images/Image00093.jpg) | Broker 节点崩溃后的故障恢复与 Partition 重分布 | 扩展性 |
| 4-29 | ![Image00094](images/Image00094.jpg) | 添加新 Broker 节点：先增加副本 → 同步追赶 → 移除旧副本 | 扩展性 |
| 4-30 | ![Image00095](images/Image00095.jpg) | Partition 增加：新消息写入所有 Partition，旧数据不迁移 | 扩展性 |
| 4-31 | ![Image00096](images/Image00096.jpg) | Partition 减少：Decommission 后等 Retention 过期再清理 | 扩展性 |
| 4-32 | ![Image00097](images/Image00097.jpg) | At-most Once 交付语义 | 交付语义 |
| 4-33 | ![Image00098](images/Image00098.jpg) | At-least Once 交付语义 | 交付语义 |
| 4-34 | ![Image00099](images/Image00099.jpg) | Exactly Once 交付语义 | 交付语义 |
| 4-35 | ![Image00100](images/Image00100.jpg) | Message Filtering by Tags | 高级特性 |
| 4-36 | ![Image00101](images/Image00101.jpg) | Delayed / Scheduled Messages：临时存储 + 定时投递 | 高级特性 |

---

## 设计思路演进

### Step 1: Message Queue vs Event Streaming Platform

```
传统 Message Queue (RabbitMQ, ActiveMQ)    Event Streaming Platform (Kafka, Pulsar)
├─ 消息被消费后即删除                        ├─ 消息持久化，可重复消费
├─ 不强制保证顺序                            ├─ Partition 内保证顺序
├─ 内存为主，磁盘溢出为辅                     ├─ 磁盘持久化，长期保留
└─ 相对简单                                  └─ 更复杂但功能更强
```

**本章设计目标**：融合两者特性，支持长期数据保留、重复消费、顺序保证，同时也讨论传统消息队列可简化之处。

### Step 2: 消息模型

| 模型 | 描述 | 实现方式 |
|------|------|----------|
| **Point-to-Point** | 一条消息只被一个 Consumer 消费 | 所有 Consumer 放入同一 Consumer Group |
| **Publish-Subscribe** | 一条消息被所有订阅者消费 | 不同 Consumer Group 独立订阅同一 Topic |

### Step 3: Topic → Partition → Broker

```
Topic A
├── Partition-1 ──→ Broker-1 (Leader) + Broker-2, Broker-3 (Follower)
├── Partition-2 ──→ Broker-2 (Leader) + Broker-3, Broker-4 (Follower)
└── Partition-3 ──→ Broker-3 (Leader) + Broker-4, Broker-1 (Follower)
```

- **Partition** 是最小存储与并行单位，每个 Partition 内部 FIFO 有序
- **Offset** 是消息在 Partition 中的位置（单调递增）
- **Message Key** 决定路由到哪个 Partition：`hash(key) % numPartitions`
- 同一 Consumer Group 内，一个 Partition 只能被一个 Consumer 消费（保证顺序）

### Step 4: 高层架构

高层架构图（Figure 4-8）展示：

```
Producers ──→ Brokers ──→ Consumers (Consumer Groups)
                │
        ┌───────┼───────┐
   Data Storage  State   Metadata
   (WAL on disk) Storage  Storage
                    ↑        ↑
                    └────────┘
                   Coordination
                    Service
                  (ZooKeeper/etcd)
```

**核心组件：**
- **Broker**：持有 Partition，处理读写请求
- **Data Storage**：WAL append-only log 持久化消息到磁盘
- **State Storage**：存储 Consumer Group 的消费 Offset 和 Partition 分配映射
- **Metadata Storage**：Topic 配置、Partition 数量、副本分布计划
- **Coordination Service**：Broker 服务发现 + Leader Election

### Step 5: 数据存储 - WAL (Write-Ahead Log)

```
为什么不用数据库？
  数据库 ❌ → 难以同时支持 write-heavy + read-heavy，成为瓶颈

为什么用 WAL？
  WAL ✅ → Append-only，纯顺序读写，磁盘顺序访问性能极好
         → 旋转磁盘大容量低成本，OS 激进的磁盘缓存加速读取
```

**Segment 机制**：
- 单个 WAL 文件不能无限增长，按大小切分为多个 Segment
- Active Segment 接收新消息写入
- Non-active Segment 只读，到期后可截断回收空间
- 目录结构：`Partition-{id}/` 下存放多个 Segment 文件

### Step 6: Producer Flow 优化

```
初始方案：Producer → Routing Layer → Leader Replica (额外网络跳数)
                    ❌ 多一跳延迟，无法 batch

改进方案：Producer Client Library 内置 Routing + Buffer
         ✅ 减少网络跳数
         ✅ Producer 自定义路由逻辑
         ✅ Buffer 聚合消息，batch 发送提升吞吐
```

**Batch Size Tradeoff**：大 batch → 高吞吐高延迟；小 batch → 低延迟低吞吐，按场景调优。

### Step 7: Consumer Flow - Pull 模型

```
Push 模型：Broker 主动推送
  ✅ 低延迟     ❌ Consumer 可能被压垮，难以适配不同处理速度

Pull 模型（推荐）：Consumer 主动拉取
  ✅ Consumer 控制消费速率
  ✅ 适合 batch 处理
  ❌ 无消息时空轮询 → 用 Long Polling 解决
```

Consumer Pull 流程（图 4-15 所示）：
1. Consumer 通过 `hash(group_name)` 找到 Coordinator Broker
2. Coordinator 分配 Partition（如 Partition-2）给该 Consumer
3. Consumer 从 Broker-2 的 Partition-2 fetch 消息
4. Consumer 处理数据后 commit offset

### Step 8: Consumer Rebalance

**触发条件**：Consumer 加入/离开/崩溃，或 Partition 数量调整

**流程**：
1. Coordinator 检测到 Consumer 列表变化
2. 通过 heartbeat 响应通知所有 Consumer rejoin group
3. Coordinator 选举 group leader
4. Leader Consumer 生成 Partition 分配计划，上报 Coordinator
5. Coordinator 广播计划给所有 Consumer
6. Consumer 开始从新分配的 Partition 消费

### Step 9: Replication 副本机制

副本分布图（Figure 4-23）中，4 个 Broker 节点各持有不同 Partition 的 Leader 和 Follower 副本：
- Producer 只写 Leader Replica
- Follower 从 Leader 拉取数据同步
- 副本分布在不同 Broker 节点上以容忍单节点故障

**ISR (In-Sync Replicas)**：
- ISR 是与 Leader "保持同步" 的副本集合
- 同步标准：Follower 落后 Leader 不超过配置的消息数/时间阈值
- Committed Offset = 所有 ISR 都已同步到的位置
- 落后太多的 Follower 被移出 ISR，追赶后可重新加入

**ACK 配置**：

| ACK | 行为 | Durability | Latency | 适用场景 |
|-----|------|-----------|---------|----------|
| `all` | 所有 ISR 同步后确认 | 最高 | 最高（等最慢 ISR） | 不允许丢数据 |
| `1` | Leader 写入即确认 | 中等（Leader 故障可能丢） | 较低 | 可容忍少量丢失的低延迟系统 |
| `0` | 不等待确认，不重试 | 最低 | 最低 | Metrics / Logging |

---

## 关键设计考量 (Tradeoffs)

### 1. 顺序保证 vs 并行度
- Partition 内 FIFO 有序，Partition 间无全局序
- 同一 Consumer Group 中，一个 Partition 只能被一个 Consumer 消费
- 若 Consumer 数 > Partition 数，多余 Consumer 空闲
- 实践中预分配足够多的 Partition 来支持未来扩容

### 2. Batch Size vs Latency
- 大 batch：高吞吐但延迟高（等待积累足够消息）
- 小 batch：低延迟但吞吐下降
- Producer、Broker、Consumer 三个环节都做 Batching

### 3. ACK Level vs Durability / Performance
- ACK=all 最安全但最慢（受限于最慢 ISR）
- ACK=0 最快但可能丢消息
- `min.insync.replicas` 控制 ACK=all 的最低 ISR 数量

### 4. Push vs Pull 消费模型
- Push 低延迟但 Consumer 可能被压垮
- Pull 灵活可控，支持 batch 消费，用 Long Polling 弥补空闲轮询

### 5. Broker 扩缩容的数据安全
- 添加 Broker：先增加临时副本 → 同步追赶 → 移除旧副本（零数据丢失）
- 移除 Broker：类似流程，先迁移再下线

### 6. Partition 扩缩容
- **增加 Partition**：新消息写入所有 Partition（含新增），旧数据不迁移，简单
- **减少 Partition**：Decommission 后等 Retention 过期才能回收空间，过渡期 Consumer 仍可消费旧 Partition

### 7. 数据交付语义 (Delivery Semantics)

| 语义 | Producer 行为 | Consumer 行为 | 风险 |
|------|-------------|-------------|------|
| **At-most Once** | ACK=0，不重试 | 先 commit offset 再处理 | 可能丢消息 |
| **At-least Once** | ACK=1/all，失败重试 | 先处理再 commit offset | 可能重复消费 |
| **Exactly Once** | 幂等 Producer + 事务 | 事务性消费 + offset 提交 | 实现复杂，性能开销大 |

### 8. 副本跨数据中心部署
- 同 DC 内副本：低延迟但不抗整个 DC 故障
- 跨 DC 副本：高可用但同步延迟和成本大幅增加
- 折中方案：Data Mirroring 异步复制跨 DC

---

## 面试扩展话题

### 1. Protocol 设计
- 消息队列需要自定义协议覆盖 Production、Consumption、Heartbeat 等交互
- 需高效传输大量数据并验证数据完整性和正确性
- 常见协议：AMQP（RabbitMQ 等）和 Kafka Protocol

### 2. Retry Consumption（消费重试）
- 消费失败的消息发送到专用 Retry Topic，避免阻塞正常消息流
- Retry Topic 可配置延迟重试策略

### 3. Historical Data Archive（历史数据归档）
- 当 Retention 机制截断了历史数据，Consumer 需要回放时：
- 使用大容量存储系统（HDFS、Object Storage 如 S3）归档历史数据
- 支持按需回放已过期的消息

### 4. Message Filtering（消息过滤）
- 在消息 Metadata 中附加 Tag，Broker 侧按 Tag 过滤
- 避免解密/反序列化 Payload，不降低 Broker 性能
- 多 Tag 支持多维度过滤

### 5. Delayed Messages / Scheduled Messages（延迟/定时消息）
- 消息先写入临时存储（特殊 Topic），到期后投递到目标 Topic
- 定时实现方案：预定义延迟级别（RocketMQ 方式）或 Hierarchical Time Wheel

---

## 速写练习要点

盲画时重点记住这些组件和连接：

1. **核心数据流**：Producer → Broker (Partition / WAL) → Consumer (Pull 模型)
2. **存储三层**：Data Storage (WAL on disk) + State Storage (offset) + Metadata Storage (topic config)
3. **Coordination**：ZooKeeper/etcd 负责 Broker Leader Election + 服务发现
4. **Partition 模型**：Topic → N 个 Partition → 分布在不同 Broker → 每个 Partition 有 Leader + Follower Replicas
5. **Consumer Group**：同 Group 内一个 Partition 只被一个 Consumer 消费 → 保证顺序
6. **Producer 优化**：Client Library 内置 Routing + Buffer → Batch 发送到 Leader Replica
7. **Replication**：ISR 机制 + ACK 配置（all/1/0）权衡 Durability 与 Latency
8. **Rebalance 触发**：Consumer 加入/离开/崩溃 → Coordinator 通知 → Leader Consumer 重新分配 Partition
9. **扩缩容**：Broker 增减用临时多副本平滑迁移；Partition 增加无数据迁移，减少需等 Retention 过期

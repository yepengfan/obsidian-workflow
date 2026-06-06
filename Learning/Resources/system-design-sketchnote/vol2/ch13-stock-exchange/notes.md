# Chapter 13: Design a Stock Exchange

## 问题定义

设计一个电子股票交易所系统，核心功能是高效撮合买卖双方的订单。

**核心需求：**
- 支持 Limit Order 的创建和取消
- 客户端可实时接收撮合结果（Execution / Fill）
- 客户端可查看实时 Order Book
- 支持至少 100 个 Symbol、数万并发用户
- 日交易量达 10 亿订单（QPS ~43,000，峰值 ~215,000）
- Risk Check：用户单日交易量上限（如 Apple 股票不超过 100 万股）
- Wallet：下单时验证资金充足，挂单冻结资金

**非功能需求：**
- Availability >= 99.99%（日停机不超过 8.64 秒）
- Fault Tolerance：快速故障恢复
- Latency：毫秒级 Round-trip，重点关注 P99 延迟
- Security：KYC 身份验证、DDoS 防护

---

## 架构图索引

| Figure | 文件 | 内容 | 设计阶段 |
|--------|------|------|----------|
| 1 | ![Image00280.jpg](images/Image00280.jpg) | 全球主要证券交易所市值分布（"万亿美元俱乐部"） | 背景 |
| 2 | ![Image00281.jpg](images/Image00281.jpg) | L1 Market Data：Best Bid/Ask Price + Quantity | 业务知识 |
| 3 | ![Image00282.jpg](images/Image00282.jpg) | L2 Market Data：多价格层级 | 业务知识 |
| 4 | ![Image00283.jpg](images/Image00283.jpg) | L3 Market Data：每个价格层级的排队数量 | 业务知识 |
| 5 | ![Image00284.gif](images/Image00284.gif) | 单根 Candlestick 图解（Open/Close/High/Low） | 业务知识 |
| 6 | ![Image00285.jpg](images/Image00285.jpg) | **高层架构图**：Trading Flow + Market Data Flow + Reporting Flow 三条数据流 | 高层设计 |
| 7 | ![Image00286.jpg](images/Image00286.jpg) | Inbound/Outbound Sequencer：为订单和执行结果分别编号 | 高层设计 |
| 8 | ![Image00287.jpg](images/Image00287.jpg) | Client Gateway 组件：认证、限流、校验、路由 | 高层设计 |
| 9 | ![Image00288.gif](images/Image00288.gif) | 不同 Client Gateway 连接方式：Web/Mobile、专线、Colocation | 高层设计 |
| 10 | ![Image00289.jpg](images/Image00289.jpg) | Market Data Publisher（MDP）架构：Execution → Order Book + Candlestick → Data Service | 高层设计 |
| 11 | ![Image00290.jpg](images/Image00290.jpg) | Reporter Flow：合并 Order + Execution 写入 DB | 高层设计 |
| 12 | ![Image00291.jpg](images/Image00291.jpg) | 数据模型 UML：Product / Order / Execution 实体关系 | 数据模型 |
| 13 | ![Image00292.jpg](images/Image00292.jpg) | Limit Order Book 撮合示例：2700 股买单如何吃掉多个卖单层级 | 数据模型 |
| 14 | ![Image00293.jpg](images/Image00293.jpg) | Order Book 数据结构：Doubly-Linked List 实现 O(1) Place/Match/Cancel | 数据模型 |
| 15 | ![Image00294.jpg](images/Image00294.jpg) | **低延迟单服务器架构**：Order Manager / Matching Engine / MDP 共享 mmap Event Store | 深入设计 |
| 16 | ![Image00295.jpg](images/Image00295.jpg) | Application Loop 线程模型：单线程 + CPU Pinning | 深入设计 |
| 17 | ![Image00296.gif](images/Image00296.gif) | Event Sourcing 对比：传统数据库 vs 不可变事件日志 | 深入设计 |
| 18 | ![Image00297.jpg](images/Image00297.jpg) | **Event Sourcing 架构**：FIX → Gateway → Event Store (mmap) → Matching Engine → Reporter | 深入设计 |
| 19 | ![Image00298.jpg](images/Image00298.jpg) | Sequencer 设计：从 Ring Buffer 拉取事件 → 编号 → 写入 Event Store | 深入设计 |
| 20 | ![Image00299.jpg](images/Image00299.jpg) | Hot-Warm Matching Engine：Hot 实例读写事件，Warm 实例只读事件 | 高可用 |
| 21 | ![Image00300.jpg](images/Image00300.jpg) | Raft Cluster：Leader 通过 AppendEntries RPC 将 Event Store 复制到 Follower | 高可用 |
| 22 | ![Image00301.jpg](images/Image00301.jpg) | Raft Terms：时间划分为 Term，包含正常运行和选举阶段 | 高可用 |
| 23 | ![Image00302.jpg](images/Image00302.jpg) | Matching Algorithm 伪代码：FIFO 撮合逻辑 | 深入设计 |
| 24 | ![Image00303.jpg](images/Image00303.jpg) | Event Sourcing 中的时间：离散时间戳转为连续序列，加速 Replay | 深入设计 |
| 25 | ![Image00304.jpg](images/Image00304.jpg) | MDP 优化设计：Ring Buffer 存储 Candlestick Charts，限定内存用量 | 深入设计 |

---

## 设计思路演进

### Step 1: 业务知识储备

理解交易所基础概念对面试至关重要：

| 概念 | 说明 |
|------|------|
| **Broker** | 零售客户通过券商（如 Robinhood、Charles Schwab）与交易所交互 |
| **Institutional Client** | 机构客户使用专用交易软件，对延迟极敏感（如做市商、对冲基金） |
| **Limit Order** | 指定价格的买/卖单，可能不会立即成交或仅部分成交 |
| **Market Order** | 不指定价格，以当前市价立即成交，牺牲成本保证执行 |
| **Market Data** | L1（Best Bid/Ask）→ L2（多价格层级）→ L3（每层排队明细），越详细越贵 |
| **Candlestick** | 蜡烛图，记录一段时间内的 Open/Close/High/Low 价格 |
| **FIX Protocol** | 金融信息交换协议（1991），证券交易的通用通信标准 |

### Step 2: 高层架构 -- 三条数据流

高层架构（Figure 6）是整个设计的骨架，包含三条核心流：

**Trading Flow（关键路径，延迟敏感）：**
```
Client → Broker → Client Gateway → Order Manager → Sequencer → Matching Engine → Order Book
                        ↕                 ↕
                  Rate Limiting      Risk Check + Wallet
                  Authentication
```

**Market Data Flow：**
```
Matching Engine → Market Data Publisher (MDP) → Data Service → Broker → Client
                  构建 Order Book + Candlestick
```

**Reporting Flow：**
```
Orders + Executions → Reporter → DB（税务、合规、对账）
```

**关键组件：**
- **Client Gateway**：轻量级守门人 -- 认证、限流、校验、路由，不做复杂逻辑
- **Order Manager**：管理订单状态机（new/cancel/fill），收发订单和执行结果
- **Sequencer**：为每个进出的 Order/Execution 打上序列号，保证 Determinism；同时充当消息队列和事件存储
- **Matching Engine**：维护每个 Symbol 的 Order Book，执行买卖撮合，输出 Execution Stream

### Step 3: 数据模型 -- Order Book 是核心

**Order Book 数据结构要求：**
- O(1) 查询某价格层级的 Volume
- O(1) Place / Match / Cancel 操作
- 快速查询 Best Bid/Ask

**实现方案：**
```
OrderBook
  ├── buyBook:  Map<Price, PriceLevel>
  ├── sellBook: Map<Price, PriceLevel>
  ├── bestBid / bestOffer: PriceLevel
  └── orderMap: Map<OrderID, Order>    ← 辅助快速查找

PriceLevel
  ├── limitPrice
  ├── totalVolume
  └── orders: DoublyLinkedList<Order>  ← 关键！保证 O(1) 删除
```

- **Place**：新订单加到 PriceLevel 尾部 → O(1)
- **Match**：从 PriceLevel 头部取 → O(1)（FIFO）
- **Cancel**：通过 orderMap 定位 → 从 DoublyLinkedList 删除 → O(1)

### Step 4: 低延迟架构演进

原始高层设计中，各组件通过网络通信，延迟在毫秒级。现代交易所将延迟压缩到微秒级，核心做法：

**一切放在单台服务器上（Figure 15）：**
```
┌─────────────────── One Single Server ───────────────────┐
│  Order Manager    Matching Engine    Market Data Publisher│
│  [App Loop]       [App Loop]         [App Loop]          │
│         ↕              ↕                ↕                │
│  ═══════════════ mmap Event Store ══════════════════════ │
│         ↕              ↕                ↕                │
│  Reporter    Logging    Risk Check    Position Keeper     │
└──────────────────────────────────────────────────────────┘
```

**Application Loop 机制（Figure 16）：**
- 单线程 While Loop 持续轮询任务
- 线程固定在特定 CPU Core（CPU Pinning）
- 无 Context Switch、无锁竞争 → P99 延迟极低且稳定
- Tradeoff：编程复杂度高，需精确控制每个任务的执行时间

**mmap 共享内存通信：**
- 使用 `mmap(2)` 系统调用映射 `/dev/shm` 中的文件到进程内存
- 进程间通信无网络、无磁盘 I/O → sub-microsecond 消息传递
- 充当 Event Store，类似 Kafka 的 Pub-Sub 模型，但延迟低得多

### Step 5: Event Sourcing 范式

**核心理念（Figure 17）：**
- 传统方式：数据库只存当前状态，丢失变更历史
- Event Sourcing：存储所有不可变的状态变更事件，通过 Replay 恢复任意时刻状态

**在交易所中的应用（Figure 18）：**
```
External Domain (FIX) → Gateway (FIX→SBE) → Event Store (mmap)
                                                  ↕
                                    Matching Engine (Order Manager 内嵌)
                                                  ↕
                                Event Store → MDP / Reporter (各自维护 Order State)
```

- Order Manager 成为可复用库，嵌入到不同组件中（Matching Engine、Reporter 等）
- Sequencer 简化为纯粹的单 Writer：从各组件 Ring Buffer 拉取事件 → 编号 → 写入 Event Store
- 保证 Functional Determinism：相同输入序列 → 相同输出结果

### Step 6: 高可用与容错

**Hot-Warm 架构（Figure 20）：**
- Hot 实例：正常处理事件，读写 Event Store
- Warm 实例：接收并处理相同事件，但不输出结果
- Primary 宕机时 Warm 立即接管

**跨服务器 / 跨数据中心扩展（Figure 21）：**
- 使用 Raft 一致性协议进行 Leader Election 和数据复制
- Leader 通过 AppendEntries RPC 将事件广播到所有 Follower
- Minimum Quorum = N/2 + 1（5 节点集群需 3 票）
- 使用 Reliable UDP 高效广播事件到所有 Warm Server

**RTO / RPO 目标：**
- RTO（恢复时间）：秒级，需自动 Failover
- RPO（数据丢失容忍）：接近零，Raft 保证多副本数据一致

---

## 关键设计考量 (Tradeoffs)

### 1. 单服务器 vs 分布式部署
- **单服务器**：极低延迟（mmap 通信 sub-microsecond），无网络开销
- **分布式**：更好的可扩展性和容错性，但延迟高（网络 RTT ~500us）
- **现实选择**：大型交易所倾向单服务器 + Raft 集群备份；云原生交易所（如 Coinbase）用分布式架构

### 2. 延迟确定性 vs 吞吐量
- CPU Pinning + 单线程 Application Loop → P99 延迟稳定，但 CPU 利用率低
- Java 环境需注意 GC Stop-the-World、Safe Points 导致的延迟波动
- 使用 HdrHistogram 精确测量延迟分布

### 3. Sequencer 设计：单 Writer vs 多 Writer
- 单 Writer Sequencer 避免锁竞争，保证事件顺序
- 但单 Writer 成为潜在瓶颈和单点故障 → 需 Backup Sequencer

### 4. Event Sourcing vs 传统数据库
- Event Sourcing：天然支持 Replay、审计追踪、Determinism
- 代价：Order Manager 嵌入多个组件，每个组件自行维护状态
- 最终一致性保证：相同事件序列 → 相同状态

### 5. Order Book 数据结构选择
- DoublyLinkedList 保证 O(1) 操作，但内存占用较大
- 需要 `Map<OrderID, Order>` 辅助索引实现 O(1) Cancel
- Ring Buffer 用于 Candlestick Charts 限制内存增长

### 6. Market Data 分发公平性
- 顺序分发会导致先连接的 Subscriber 获得信息优势
- 使用 Multicast（Reliable UDP）同时广播给所有接收者
- 或在 Subscriber 连接时随机排序

### 7. Colocation 服务
- 将客户服务器放在交易所数据中心内 → 延迟 = 光在光缆中的传播时间
- 不违反公平原则，视为付费 VIP 服务

### 8. 网络安全
- 隔离公有服务与私有服务，DDoS 不影响核心客户
- 缓存层 + CDN 减轻数据库负载
- URL 硬化（避免可参数化的 URL 被轻易枚举）
- Safelist/Blocklist + Rate Limiting

---

## 面试扩展话题

以下话题在原书 Wrap Up 和正文中提及，适合面试深入讨论：

1. **云原生交易所 vs 传统交易所**：加密货币交易所（如 Coinbase）使用 AWS 云基础设施部署，降低了行业进入门槛，改变了部分设计假设
2. **AMM (Automatic Market Making)**：去中心化金融（DeFi）中的自动做市商模式，不需要传统 Order Book
3. **Dark Pool**：暗池交易，使用不同的撮合算法（如 FIFO with LMM），机构大单可降低市场冲击
4. **Matching Algorithm 变体**：FIFO、FIFO with LMM（Lead Market Maker 优先分配）、Pro-rata 等，不同交易所和产品使用不同算法
5. **Order Splitting**：机构大单拆分执行，减少 Market Impact
6. **更多 Order 类型**：Market Order、Conditional Order、Stop Order、After-hours Trading 等
7. **Chaos Engineering**：在生产环境模拟故障，验证 Failover 机制，积累运维经验
8. **LMAX Disruptor**：开源高性能 Ring Buffer 实现，Lock-free 设计的经典范例
9. **延迟优化深水区**：Cache Line Padding、避免 False Sharing、GC 调优、Safe Point 分析

---

## 速写练习要点

盲画时重点记住这些组件和连接：

1. **高层架构三条流**：Trading Flow（Client → Gateway → Order Manager → Sequencer → Matching Engine）、Market Data Flow（ME → MDP → Data Service）、Reporting Flow（Orders + Executions → Reporter → DB）
2. **关键路径组件**：Gateway / Order Manager / Sequencer / Matching Engine，每一步都不可省略
3. **低延迟演进**：多服务器网络通信 → 单服务器 mmap 共享内存 → sub-microsecond
4. **Application Loop**：单线程 + CPU Pinning + While Loop 轮询，无锁无切换
5. **Event Sourcing 架构**：FIX → SBE → Event Store (mmap) → 各组件订阅消费
6. **Order Book 结构**：BuyBook + SellBook + DoublyLinkedList + OrderMap，三种操作都 O(1)
7. **高可用**：Hot-Warm Matching Engine → Raft Cluster 跨服务器复制 → Leader Election
8. **MDP 优化**：Ring Buffer 存 Candlestick（1min/1hour/1day）→ Persistence → Data Service

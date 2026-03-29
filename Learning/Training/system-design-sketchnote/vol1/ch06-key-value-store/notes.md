# Chapter 6: Design a Key-Value Store

## 问题定义

Key-Value Store 是一种非关系型数据库，每个唯一 key 对应一个 value。支持两个核心操作：`put(key, value)` 和 `get(key)`。

**核心需求：**
- Key-value pair 体积小（< 10 KB）
- 支持存储大规模数据（big data）
- High availability：即使发生故障也能快速响应
- High scalability：可扩展支持大数据集
- Automatic scaling：根据流量自动增删节点
- Tunable consistency：可调一致性
- Low latency

---

## 架构图索引

| Figure | 文件 | 内容 | 设计阶段 |
|--------|------|------|----------|
| - | ![Image00067](images/Image00067.jpg) | Key-value store 数据示例表 | 问题定义 |
| 6-1 | ![Image00068](images/Image00068.jpg) | CAP theorem Venn 图：Consistency / Availability / Partition Tolerance 三圆交叉，标注 CA、CP、AP 区域 | CAP 理论 |
| 6-2 | ![Image00069](images/Image00069.jpg) | 理想情况：三副本节点 n1、n2、n3 互相连接，无网络分区 | CAP 理论 |
| 6-3 | ![Image00070](images/Image00070.jpg) | 网络分区：n3 出现故障（标红 X），n1、n2 仍连接 | CAP 理论 |
| 6-4 | ![Image00071](images/Image00071.jpg) | Consistent hashing：8 个服务器 s0-s7 分布在 hash ring 上，key0 顺时针映射到 s1 | Data partition |
| 6-5 | ![Image00072](images/Image00072.jpg) | Data replication：key0 在 hash ring 上顺时针复制到 N=3 个服务器 | Data replication |
| 6-6 | ![Image00073](images/Image00073.jpg) | Quorum consensus：coordinator 向 s0、s1、s2 发送 put(key1, val1) 并接收 ACK | Consistency |
| 6-7 | ![Image00074](images/Image00074.jpg) | 不一致性示例：两个副本节点 n1、n2 初始值相同 | Versioning |
| 6-8 | ![Image00075](images/Image00075.jpg) | 并发写冲突：server 1 改为 "johnSanFrancisco"，server 2 改为 "johnNewYork" | Versioning |
| 6-9 | ![Image00076](images/Image00076.jpg) | Vector clock 完整流程：D1→D2 分叉为 D3(Sy)和 D4(Sz)，最终 reconcile 为 D5 | Versioning |
| 6-10 | ![Image00077](images/Image00077.jpg) | All-to-all multicasting 故障检测（低效方案） | Failure detection |
| 6-11 | ![Image00078](images/Image00078.jpg) | Gossip protocol：s0 的 membership list 表（含 heartbeat counter 和时间），检测到 s2 下线（counter 9908 红色标注） | Failure detection |
| 6-12 | ![Image00079](images/Image00079.jpg) | Sloppy quorum + Hinted handoff：s2 下线，coordinator 将请求转发给 s3 临时处理 | Temporary failures |
| 6-13 | ![Image00080](images/Image00080.jpg) | Merkle tree Step 1：将 key space 1-12 划分为 4 个 bucket | Permanent failures |
| 6-14 | ![Image00081](images/Image00081.jpg) | Merkle tree Step 2：对每个 bucket 中的 key 做 hash | Permanent failures |
| 6-15 | ![Image00082](images/Image00082.jpg) | Merkle tree Step 3：每个 bucket 生成单一 hash 节点 | Permanent failures |
| 6-16 | ![Image00083](images/Image00083.jpg) | Merkle tree Step 4：两台 server 的完整 Merkle tree 对比，红色高亮不一致的节点和数据 | Permanent failures |
| 6-17 | ![Image00084](images/Image00084.jpg) | **系统架构图**：Client 发送 read/write 到 coordinator(n6)，coordinator 将请求分发给 n0、n1、n2（蓝色高亮为副本节点），8 节点 hash ring | 系统架构 |
| 6-18 | ![Image00085](images/Image00085.jpg) | **节点内部模块**：Client API、Failure detection、Conflict resolution、Failure repair mechanism、Replication、Storage engine 等 | 系统架构 |
| 6-19 | ![Image00086](images/Image00086.jpg) | **Write path**：Client→Server，1.写 Commit log(磁盘) 2.写 Memory cache 3.Flush 到 SSTables(磁盘) | Write path |
| 6-20 | ![Image00087](images/Image00087.jpg) | Read path（命中缓存）：直接从 Memory cache 返回 | Read path |
| 6-21 | ![Image00088](images/Image00088.jpg) | **Read path（未命中缓存）**：1.查 Memory cache miss 2.查 Bloom filter 3.定位 SSTables 4.读取结果 5.返回 Client | Read path |
| Table 6-2 | ![Image00089](images/Image00089.jpg) | 总结表：Goal/Problems 与 Technique 的对应关系 | 总结 |

---

## 设计思路演进

### Step 1: 单机 vs 分布式

```
单机 Key-Value Store
  └─ Hash table（内存）
       ├─ 优化 1: Data compression
       └─ 优化 2: 热数据放内存，冷数据放磁盘
  └─ 瓶颈: 单机容量有限 → 需要分布式
```

### Step 2: 理解 CAP Theorem

CAP theorem 指出分布式系统不可能同时满足三者，必须牺牲其一：

| 组合 | 含义 | 现实可行性 |
|------|------|------------|
| **CP** | Consistency + Partition Tolerance，牺牲 Availability | 银行系统（宁可报错也不能数据不一致） |
| **AP** | Availability + Partition Tolerance，牺牲 Consistency | 社交网络（允许短暂读到旧数据） |
| **CA** | Consistency + Availability，牺牲 Partition Tolerance | 现实中不存在（网络分区不可避免） |

**关键理解：** 网络分区（Partition）在分布式系统中不可避免，所以实际只在 CP 和 AP 之间选择。

### Step 3: Data Partition - Consistent Hashing

```
Hash Ring 上放置服务器 s0-s7
  └─ key 通过 hash 映射到 ring 上
       └─ 顺时针找到第一个 server 存储
优势：
  ├─ Automatic scaling: 按负载自动增删节点
  └─ Heterogeneity: 高容量节点分配更多 virtual nodes
```

### Step 4: Data Replication

```
key 映射到 ring 位置后，顺时针选择前 N 个服务器存储副本（N 可配置）
  ├─ 使用 virtual nodes 时，确保选择 N 个不同的物理服务器
  └─ 副本放在不同 data center 以提高可靠性
```

### Step 5: Consistency - Quorum Consensus

```
N = 副本数量
W = 写入需确认的副本数
R = 读取需响应的副本数

Coordinator 作为 Client 和节点之间的代理
  ├─ W=1: 只需 1 个 ACK → 写入快但一致性弱
  ├─ R=1: 只需 1 个响应 → 读取快但一致性弱
  └─ W+R > N: 保证 Strong consistency（至少 1 个节点有最新数据）
```

**典型配置：**

| 配置 | 效果 |
|------|------|
| R=1, W=N | 优化快速读 |
| W=1, R=N | 优化快速写 |
| W+R > N（通常 N=3, W=R=2） | Strong consistency |
| W+R <= N | 无法保证 Strong consistency |

### Step 6: Inconsistency Resolution - Vector Clock

```
Vector clock = [server, version] 对的集合

D1([Sx,1]) → D2([Sx,2]) → 分叉:
  ├─ D3([Sx,2],[Sy,1])  — Sy 处理写入
  └─ D4([Sx,2],[Sz,1])  — Sz 处理写入
       └─ 客户端检测冲突 → reconcile → D5([Sx,3],[Sy,1],[Sz,1])
```

**冲突判定规则：**
- 若 Y 的所有 version counter >= X 的对应值 → Y 是 X 的后代（无冲突）
- 若存在某个 participant 在 Y 中的 counter < X 中的 → 冲突（sibling）

**Vector clock 缺点：**
1. 客户端需实现冲突解决逻辑，增加复杂度
2. `[server: version]` 对可能快速增长 → 设置长度阈值，超过则移除最旧的条目

### Step 7: Failure Detection - Gossip Protocol

```
All-to-all multicasting ❌ → 服务器多时效率低

Gossip Protocol ✅:
  ├─ 每个节点维护 membership list（member ID + heartbeat counter）
  ├─ 定期递增自身 heartbeat counter
  ├─ 定期向随机节点发送 heartbeat
  ├─ 收到 heartbeat → 更新 membership list
  └─ heartbeat 超过预设时间未增长 → 标记该节点离线
```

### Step 8: Handling Temporary Failures - Sloppy Quorum

```
Strict quorum 会阻塞读写 → 影响 availability

Sloppy Quorum:
  ├─ 选择 hash ring 上前 W 个健康节点处理写入
  ├─ 选择前 R 个健康节点处理读取
  └─ 忽略离线节点

Hinted Handoff:
  ├─ s2 下线 → s3 临时接管处理请求
  └─ s2 恢复后 → s3 将数据推回 s2
```

### Step 9: Handling Permanent Failures - Merkle Tree

```
Anti-entropy protocol 保持副本同步

Merkle Tree 构建步骤：
  1. 将 key space 划分为 bucket（如 1-12 分为 4 个 bucket）
  2. 对每个 bucket 中的 key 做 hash
  3. 每个 bucket 生成单一 hash 节点
  4. 逐层向上计算子节点的 hash，构建完整树

比较两棵 Merkle Tree：
  ├─ 根 hash 相同 → 数据一致
  └─ 根 hash 不同 → 逐层向下比较，定位不一致的 bucket → 只同步差异部分
```

**优势：** 同步数据量正比于两副本的差异量，而非总数据量。

### Step 10: 系统架构

```
Client → read/write → Coordinator (hash ring 上的某个节点)
                           ↓
                    分发到 N 个副本节点
                    (consistent hashing 定位)

完全去中心化（Decentralized）：
  ├─ 无单点故障
  ├─ 节点增删自动化
  └─ 每个节点承担相同职责
```

**每个节点内部模块：**
- Client API
- Failure detection
- Conflict resolution
- Failure repair mechanism
- Replication
- Storage engine

### Step 11: Write Path（基于 Cassandra 架构）

```
Client → Write → Server
  1. 写入 Commit log（磁盘，持久化保障）
  2. 写入 Memory cache（内存，快速访问）
  3. Memory cache 满/达阈值 → Flush 到 SSTable（磁盘）
```

### Step 12: Read Path

```
Client → Read → Server
  ├─ Memory cache 命中 → 直接返回
  └─ Memory cache 未命中:
       1. 查 Bloom filter（快速判断 key 可能在哪些 SSTable）
       2. 定位对应 SSTable
       3. 从 SSTable 读取数据
       4. 返回结果给 Client
```

---

## 关键设计考量 (Tradeoffs)

### 1. Consistency vs Availability（核心 tradeoff）
- **CP 系统**：网络分区时阻塞写操作，避免数据不一致（如银行系统）
- **AP 系统**：网络分区时继续接受读写，允许返回 stale data（如社交网络）
- **选择依据**：根据业务场景与面试官讨论

### 2. Quorum 参数 N/W/R 的权衡
- **延迟 vs 一致性**：W=1 或 R=1 → 快速但一致性弱；W+R > N → 强一致但慢
- **读优化 vs 写优化**：R=1,W=N 快读；W=1,R=N 快写

### 3. Eventual Consistency 的代价
- Dynamo 和 Cassandra 均采用 Eventual consistency
- 并发写入导致数据冲突 → 需要 vector clock + 客户端 reconcile
- Vector clock 可能无限增长 → 需设置长度阈值截断

### 4. Gossip Protocol 的 tradeoff
- 去中心化、无单点故障
- 代价：故障检测有延迟（需要多个节点确认）

### 5. Sloppy Quorum vs Strict Quorum
- Sloppy quorum 提高 availability，但可能导致暂时的数据不一致
- Hinted handoff 确保故障恢复后数据最终同步

### 6. Merkle Tree 的空间与效率
- 高效检测副本间差异，只同步不一致的 bucket
- 实际配置：10 亿 key 可分为 100 万 bucket，每个 bucket 约 1000 key

---

## 功能与技术总结（对应原书 Table 6-2）

| Goal / Problem | Technique |
|----------------|-----------|
| Ability to store big data | Consistent hashing 分散负载到多台服务器 |
| High availability reads | Data replication + Multi-data center setup |
| Highly available writes | Versioning + Conflict resolution with vector clocks |
| Dataset partition | Consistent Hashing |
| Incremental scalability | Consistent Hashing |
| Heterogeneity | Consistent Hashing（virtual nodes 按容量分配） |
| Tunable consistency | Quorum consensus（N/W/R 参数调节） |
| Handling temporary failures | Sloppy quorum + Hinted handoff |
| Handling permanent failures | Merkle tree |
| Handling data center outage | Cross-data center replication |

---

## 面试扩展话题

原书 Wrap-up 未单独列出额外话题，但以下为基于本章内容的面试高频扩展点：

- **具体系统对比**：Dynamo vs Cassandra vs BigTable 的设计差异
  - Dynamo：Amazon 的 AP 系统，vector clock 解决冲突
  - Cassandra：借鉴 Dynamo + BigTable，LSM-tree 存储引擎
  - BigTable：Google 的 CP 系统，强一致性
- **Consistency model 选择**：Strong / Weak / Eventual consistency 在不同业务场景的适用性
- **Bloom filter 原理**：概率型数据结构，可能有 false positive 但无 false negative
- **SSTable 与 LSM-tree**：Write path 的核心存储结构，写入快但读取需 compaction 优化
- **跨数据中心复制策略**：同步 vs 异步复制的延迟与一致性权衡
- **热点 key 问题**：某些 key 被频繁访问，如何通过分片或缓存缓解
- **数据过期与垃圾回收**：TTL 策略、tombstone 标记、compaction 清理

---

## 速写练习要点

盲画时重点记住这些组件和连接：

1. **CAP Venn 图**：三圆交叉（C/A/P），标注 CP、AP、CA 三个交集区域
2. **Hash Ring 核心图**：节点分布在环上，key 顺时针定位到第一个 server，顺时针选 N 个副本
3. **Quorum 写入流**：Coordinator → 向 N 个副本发 put → 收到 W 个 ACK 即成功
4. **Vector Clock 分叉图**：D1→D2 分叉为 D3/D4（不同 server 处理）→ reconcile 为 D5
5. **Gossip Protocol**：membership list 表（ID + heartbeat counter + time），节点间随机传播
6. **Sloppy Quorum**：s2 下线 → coordinator 绕过 s2 → s3 临时接管 → s2 恢复后 handoff
7. **Merkle Tree**：两棵树从根向下比较，红色标记不一致节点，只同步差异 bucket
8. **Write Path**：Client → Commit log(磁盘) → Memory cache → Flush → SSTable(磁盘)
9. **Read Path**：Client → Memory cache → (miss) → Bloom filter → SSTable → 返回
10. **系统全景图**：Client → Coordinator(ring 上某节点) → 分发到蓝色副本节点（去中心化，无单点故障）

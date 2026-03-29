# Chapter 1: Scale From Zero To Millions of Users

## 问题定义

设计一个能从单用户扩展到百万级用户的系统，是一个持续迭代的过程。本章从最简单的单机部署出发，逐步引入各层优化手段，最终构建出支持大规模用户的完整架构。

**核心挑战：**
- 从单服务器起步，逐步识别瓶颈并解决
- Web 层与数据层需独立扩展
- 保证高可用（failover + redundancy）
- 降低延迟、提高响应速度
- 支持全球多数据中心部署

---

## 架构图索引

| Figure | 文件 | 内容 | 设计阶段 |
|--------|------|------|----------|
| 1-1 | ![Image00000.jpg](images/Image00000.jpg) | 单服务器架构（Web + DB + Cache 全在一台机器） | 起点 |
| 1-2 | ![Image00001.jpg](images/Image00001.jpg) | 请求流程：用户 → DNS → Web Server → 响应 | 起点 |
| 1-3 | ![Image00003.jpg](images/Image00003.jpg) | Web 层与数据层分离（两台服务器） | 数据库拆分 |
| 1-4 | ![Image00004.jpg](images/Image00004.jpg) | Load Balancer 架构（公网 IP → LB → 私网 Web Servers） | Web 层扩展 |
| 1-5 | ![Image00005.jpg](images/Image00005.jpg) | Database Replication：Master/Slave 模型 | 数据层扩展 |
| 1-6 | ![Image00006.jpg](images/Image00006.jpg) | **LB + DB Replication 完整架构**：用户→DNS→LB→Web Servers→Master(Write)/Slave(Read) | 里程碑设计 |
| 1-7 | ![Image00007.jpg](images/Image00007.jpg) | Cache 层架构：Web Server 先查 Cache，未命中再查 DB | Cache |
| 1-9 | ![Image00010.jpg](images/Image00010.jpg) | CDN 提升加载速度示意（就近分发） | CDN |
| 1-10 | ![Image00011.jpg](images/Image00011.jpg) | CDN 工作流程：Origin → CDN Cache → 用户 | CDN |
| 1-11 | ![Image00012.jpg](images/Image00012.jpg) | 加入 CDN + Cache 后的整体设计 | 里程碑设计 |
| 1-12 | ![Image00013.jpg](images/Image00013.jpg) | Stateful 架构：用户绑定特定服务器（sticky session） | Stateless 对比 |
| 1-13 | ![Image00014.jpg](images/Image00014.jpg) | Stateless 架构：Session 数据存到共享存储 | Stateless 对比 |
| 1-14 | ![Image00015.jpg](images/Image00015.jpg) | Stateless Web Tier + Shared Data Store + Autoscaling | 里程碑设计 |
| 1-15 | ![Image00016.jpg](images/Image00016.jpg) | 多数据中心：GeoDNS 路由到最近的 DC | 多 DC |
| 1-16 | ![Image00017.jpg](images/Image00017.jpg) | DC Failover：一个 DC 离线时流量全部切到另一个 | 多 DC |
| 1-17 | ![Image00018.jpg](images/Image00018.jpg) | Message Queue 模型：Producer → Queue → Consumer | 解耦 |
| 1-18 | ![Image00019.jpg](images/Image00019.jpg) | 图片处理场景：Web Server → MQ → Photo Processing Workers | 解耦 |
| 1-19 | ![Image00020.jpg](images/Image00020.jpg) | **加入 MQ + 工具后的完整架构**：含 CDN、LB、MQ、Workers、NoSQL、Logging/Metrics/Automation | 里程碑设计 |
| 1-20 | ![Image00021.jpg](images/Image00021.jpg) | 数据库 Vertical Scaling vs Horizontal Scaling 对比 | DB Scaling |
| 1-21 | ![Image00022.jpg](images/Image00022.jpg) | Sharding 示例：user_id % 4 分配到不同 Shard | DB Scaling |
| 1-22 | ![Image00023.jpg](images/Image00023.jpg) | 各 Shard 中的 User Table 数据分布 | DB Scaling |
| 1-23 | ![Image00024.jpg](images/Image00024.jpg) | **最终架构**：含 Sharded DB、CDN、LB、MQ、Workers、NoSQL、Cache、Tools | 最终设计 |

---

## 设计思路演进

### Step 1: 单服务器 → Web/DB 分离

```
起点：一台服务器跑所有东西（Web App + DB + Cache）
  ↓ 用户增长，单机瓶颈
拆分：Web Server 与 Database Server 分开部署
  → Web 层和数据层可独立扩展
```

### Step 2: 引入 Load Balancer → Web 层水平扩展

```
问题：单台 Web Server → 无 failover，容量有限
  ↓
方案：Load Balancer（公网 IP）→ 多台 Web Server（私网 IP）
  → 一台 down 掉，流量自动路由到其他服务器
  → 流量增长时加机器即可
```

### Step 3: Database Replication → 数据层高可用

```
问题：单库 → 无 failover，无冗余
  ↓
方案：Master-Slave Replication
  Master → 处理 Write（insert/update/delete）
  Slave(s) → 处理 Read（通常读多写少）
  → 读性能提升（并行处理）
  → 数据可靠性（多副本）
  → 高可用（Master 挂了 Slave 可提升）
```

**Slave 故障处理：** 读请求临时转到 Master 或其他健康 Slave，同时补充新 Slave

**Master 故障处理：** 提升一个 Slave 为新 Master；注意 Slave 数据可能不是最新的，需要数据恢复脚本补齐

### Step 4: 加入 Cache 层 → 降低数据库压力

```
Web Server → 先查 Cache → 命中则直接返回
                        → 未命中则查 DB → 存入 Cache → 返回
```

**缓存策略：** Read-through Cache（还有其他策略如 write-through、write-behind 等）

**Cache 使用注意事项：**

| 考量 | 要点 |
|------|------|
| 适用场景 | 读多写少的数据；易失性存储不适合持久化重要数据 |
| 过期策略 (Expiration) | 太短 → 频繁重新加载；太长 → 数据过期失效 |
| 一致性 (Consistency) | DB 和 Cache 的更新不在同一事务中，多 Region 下更复杂 |
| 避免 SPOF | 多 Cache Server 跨 Data Center 部署；预留额外内存 |
| 淘汰策略 (Eviction) | LRU（最常用）、LFU、FIFO |

### Step 5: 加入 CDN → 静态资源加速

```
用户 → CDN（就近节点）→ 命中缓存则直接返回
                      → 未命中则回源（Origin Server / S3）→ 缓存后返回
后续请求 → CDN 直接返回（直到 TTL 过期）
```

**CDN 使用注意事项：**

| 考量 | 要点 |
|------|------|
| 成本 (Cost) | 按流量计费，不常访问的资源不要放 CDN |
| 缓存过期 (TTL) | 太长 → 内容不新鲜；太短 → 频繁回源 |
| CDN 故障回退 (Fallback) | 客户端能检测到 CDN 故障并直接请求 Origin |
| 缓存失效 (Invalidation) | 通过 CDN API 使对象失效；或使用 URL 版本号（如 image.png?v=2） |

### Step 6: Stateless Web Tier → 支持 Autoscaling

```
Stateful ❌：Session 存在各 Web Server 内存 → 需要 sticky session → 难扩展
Stateless ✅：Session 数据移到共享存储（Redis/Memcached/NoSQL）
  → 任意 Web Server 可处理任意请求
  → 自动扩缩容（Autoscaling）成为可能
```

### Step 7: 多数据中心 → 全球化部署

```
GeoDNS → 根据用户地理位置路由到最近的 Data Center
DC1 (US-East): x% 流量
DC2 (US-West): (100-x)% 流量
  ↓ DC2 宕机时
DC1 接管 100% 流量
```

**多 DC 技术挑战：**
- **流量重定向 (Traffic Redirection)**：GeoDNS 按地理位置路由
- **数据同步 (Data Synchronization)**：跨 DC 复制数据（如 Netflix 的异步多 DC Replication）
- **测试与部署 (Test & Deployment)**：多地点测试 + 自动化部署保持一致性

### Step 8: Message Queue → 组件解耦

```
Producer (Web Servers) → Message Queue → Consumer (Workers)
  → Producer 和 Consumer 可独立扩展
  → 队列积压时加 Workers；空闲时减 Workers
```

**典型场景：** 图片处理（裁剪、锐化、模糊等耗时任务）→ Web Server 发布任务到 MQ → Workers 异步处理

### Step 9: Logging, Metrics, Automation → 运维保障

- **Logging**：错误日志聚合到中心化服务，便于搜索和查看
- **Metrics**：
  - Host 级别：CPU、Memory、Disk I/O
  - 聚合级别：整个 DB Tier / Cache Tier 的性能
  - 业务指标：DAU、留存率、收入
- **Automation**：CI/CD 自动化构建、测试、部署

### Step 10: Database Sharding → 数据层水平扩展

```
Vertical Scaling ❌：单机加 CPU/RAM 有硬件上限，SPOF 风险，成本高
Horizontal Scaling (Sharding) ✅：数据按 Shard Key 分布到多台服务器
  例：user_id % 4 → Shard 0/1/2/3
```

**Sharding 挑战：**

| 挑战 | 说明 | 解法 |
|------|------|------|
| Resharding | 单 Shard 容量不足或数据分布不均 | Consistent Hashing（第5章） |
| Celebrity Problem (Hotspot Key) | 热点用户集中在同一 Shard 导致过载 | 为每个名人分配独立 Shard，必要时进一步拆分 |
| Join & De-normalization | 跨 Shard 无法 Join | 反范式化，单表查询 |

---

## 关键设计考量 (Tradeoffs)

### 1. Vertical Scaling vs Horizontal Scaling
- **Vertical**：简单但有硬件上限，单点故障，成本高
- **Horizontal**：需要更复杂的设计（如 Load Balancer、Sharding），但可无限扩展

### 2. SQL vs NoSQL
- **SQL（关系型）**：40+年历史验证，表结构 + Join，适合大多数场景
- **NoSQL**：超低延迟、非结构化数据、纯序列化/反序列化、海量数据时考虑
- 四大类：Key-Value Stores、Graph Stores、Column Stores、Document Stores

### 3. Stateful vs Stateless Web Tier
- **Stateful**：实现简单但 sticky session 限制扩展能力
- **Stateless**：需引入外部共享存储，但可自由扩缩容

### 4. Master-Slave Replication 的故障恢复复杂度
- Slave 提升为 Master 时数据可能不完整
- 需要数据恢复脚本，生产环境更复杂
- 进阶方案：Multi-Master Replication、Circular Replication

### 5. Cache TTL 与 CDN TTL 的平衡
- 太短 → 频繁回源/重新加载，增加后端压力
- 太长 → 数据/内容过期，用户看到陈旧信息

### 6. Sharding Key 的选择
- 必须能均匀分布数据，避免热点
- 直接影响查询效率和数据迁移难度

---

## 面试扩展话题

原书总结了从零到百万用户扩展的核心原则，每一条都是可深入展开的面试话题：

- **Keep web tier stateless**：讨论 Session 管理方案（Redis、JWT、Shared DB）
- **Build redundancy at every tier**：每一层都需要冗余设计，消除 SPOF
- **Cache data as much as you can**：缓存策略选择（Read-through、Write-through、Write-behind、Cache-aside）
- **Support multiple data centers**：GeoDNS、跨 DC 数据同步、failover 策略
- **Host static assets in CDN**：CDN 选型、缓存失效策略、成本优化
- **Scale your data tier by sharding**：Shard Key 设计、Resharding、Consistent Hashing
- **Split tiers into individual services**：微服务拆分、服务间通信（REST、gRPC、MQ）
- **Monitor your system and use automation tools**：可观测性三支柱（Logging、Metrics、Tracing）、CI/CD

---

## 速写练习要点

盲画时重点记住这些组件和连接，按演进顺序分层构建：

1. **基础层（从上到下）**：User → DNS → Load Balancer → Web Servers (Server 1, Server 2)
2. **数据层**：Web Servers → Master DB (Write) / Slave DB (Read)，Master → Slave (Replicate)
3. **加速层**：User → CDN（静态资源）；Web Servers → Cache → DB（动态数据）
4. **状态外移**：Session Data → Shared Data Store（Redis/NoSQL）→ 支持 Autoscaling
5. **多 DC**：GeoDNS 路由到 DC1 / DC2，DC 之间数据同步
6. **异步解耦**：Web Servers → Message Queue → Workers → NoSQL
7. **数据分片**：Databases → Shard 1 / Shard 2 / Shard ...（按 user_id % N 分配）
8. **运维工具**：底部独立区域画 Logging、Metrics、Monitoring、Automation 四个框
9. **最终架构关键连接**：User→CDN + User→DNS→LB→Web Servers→(Cache, MQ, Sharded DB)→Workers→NoSQL；底部 Tools

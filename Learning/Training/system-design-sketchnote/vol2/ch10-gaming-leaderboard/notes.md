# Chapter 10: Design a Real-time Gaming Leaderboard

## 问题定义

为在线手游设计一个实时排行榜系统，展示锦标赛中玩家的排名。

**核心需求：**
- 展示排行榜 Top 10 玩家
- 查询特定玩家的排名
- 展示某玩家上下各 4 名的相邻排名（bonus）
- 实时更新分数与排名
- 5M DAU / 25M MAU，每月一轮新锦标赛

**规模估算：**
- 平均 QPS：~50 用户/秒，每用户每天 10 场 → 评分更新 QPS ~500
- Peak QPS：平均的 5 倍 → 评分更新 2,500/s，排行榜查询 ~250/s
- 存储：最坏情况 25M 用户 x 26 bytes ≈ 650 MB（单台 Redis 可承载）

---

## 架构图索引

| Figure | 文件 | 内容 | 设计阶段 |
|--------|------|------|----------|
| Figure 1 | ![Image00215.jpg](images/Image00215.jpg) | Marvel Contest of Champions 排行榜示例 | 问题定义 |
| Figure 2 | ![Image00216.jpg](images/Image00216.jpg) | 高层架构：Client → Game Service → Leaderboard Service → Leaderboard Store，4 步数据流 | 高层设计 |
| Figure 3 | ![Image00217.jpg](images/Image00217.jpg) | 客户端 vs 服务端设置分数的对比（安全性考量） | 高层设计 |
| Figure 4 | ![Image00218.jpg](images/Image00218.jpg) | 使用 Kafka 消息队列让多个服务消费游戏分数 | 高层设计 |
| Figure 5 | ![Image00219.jpg](images/Image00219.jpg) | 排行榜数据库表结构（user_id, score） | 数据模型-RDS |
| Figure 6 | ![Image00220.jpg](images/Image00220.jpg) | 用户赢得 1 分的 SQL 更新流程 | 数据模型-RDS |
| Figure 7 | ![Image00221.jpg](images/Image00221.jpg) | 用 SQL 查询用户排行位置（ORDER BY + rownum） | 数据模型-RDS |
| Figure 8 | ![Image00222.jpg](images/Image00222.jpg) | Redis Sorted Set 表示 2 月排行榜（score + member 表格） | 数据模型-Redis |
| Figure 9 | ![Image00223.jpg](images/Image00223.jpg) | Skip List 数据结构：Base List → Level 1 Index → Level 2 Index，搜索 45 的加速路径 | 数据模型-Redis |
| Figure 10 | ![Image00224.jpg](images/Image00224.jpg) | 5 层索引的 Skip List，62 步降至 11 步 | 数据模型-Redis |
| Figure 11 | ![Image00225.jpg](images/Image00225.jpg) | Redis ZINCRBY 用户得分流程 | Redis 工作流 |
| Figure 12 | ![Image00226.jpg](images/Image00226.jpg) | ZREVRANGE 获取 Top 10 全局排行榜 | Redis 工作流 |
| Figure 13 | ![Image00227.jpg](images/Image00227.jpg) | ZREVRANK 获取用户排名 | Redis 工作流 |
| Figure 14 | ![Image00228.gif](images/Image00228.gif) | ZREVRANGE 获取目标用户上下各 4 名玩家 | Redis 工作流 |
| Figure 15 | ![Image00229.jpg](images/Image00229.jpg) | 自建服务架构：Client → LB → Web Servers → Redis(Sorted Set) + MySQL(User/Points) + Redis(Top 10 Cache) | 深入设计 |
| Figure 16 | ![Image00230.jpg](images/Image00230.jpg) | AWS Lambda 方案：用户得分流程（API Gateway → Lambda → Redis + MySQL） | 深入设计-云 |
| Figure 17 | ![Image00231.jpg](images/Image00231.jpg) | AWS Lambda 方案：获取排行榜流程 | 深入设计-云 |
| Figure 18 | ![Image00232.jpg](images/Image00232.jpg) | Fixed Partition：按分数范围分片 [1,100] [101,200] ... [901,1000]，每个分片一个 Sorted Set | Scaling Redis |
| Figure 19 | ![Image00233.jpg](images/Image00233.jpg) | Hash Partition：Redis Cluster 3 节点分配 16384 hash slots | Scaling Redis |
| Figure 20 | ![Image00234.jpg](images/Image00234.jpg) | Scatter-Gather：从 3 个 shard 各取 Top 10 再合并为全局 Top 10 | Scaling Redis |
| Figure 21 | ![Image00235.jpg](images/Image00235.jpg) | DynamoDB 替代方案系统架构 | NoSQL 方案 |
| Figure 22 | ![Image00236.jpg](images/Image00236.jpg) | DynamoDB 排行榜反范式化表结构 | NoSQL 方案 |
| Figure 23 | ![Image00237.jpg](images/Image00237.jpg) | DynamoDB Partition Key + Sort Key 设计 | NoSQL 方案 |
| Figure 24 | ![Image00238.jpg](images/Image00238.jpg) | DynamoDB Write Sharding：partition key 加入分区号 | NoSQL 方案 |
| Figure 25 | ![Image00239.jpg](images/Image00239.jpg) | DynamoDB Scatter-Gather 获取 Top 10 | NoSQL 方案 |

---

## 设计思路演进

### Step 1: API 设计

```
POST /v1/scores         → 用户赢得比赛后更新分数（仅内部调用，Game Server → Leaderboard Service）
GET  /v1/scores         → 获取 Top 10 排行榜
GET  /v1/scores/{uid}   → 获取指定用户排名
```

**关键决策：** 分数更新必须由服务端发起，客户端不可直接调用，防止 Man-in-the-middle 攻击篡改分数。

### Step 2: 高层架构

```
Client ──(1) Win a game──→ Game Service ──(2) Update score──→ Leaderboard Service
  ↑                                                                 │
  └──────(4) Get leaderboard / rank──────────────────────────────────┘
                                                                    │
                                                              (3) Update score
                                                                    ↓
                                                            Leaderboard Store
```

**是否引入消息队列？**
- 如果分数数据需要被多个服务消费（Analytics、Push Notification 等）→ 使用 Kafka
- 本场景需求单一 → 不引入 MQ，直接同步调用

### Step 3: 数据模型 - 从 RDS 到 Redis

**方案 A：关系数据库（RDS）** ❌ 不适合大规模
- 简单场景可用：`INSERT` / `UPDATE` + `ORDER BY score DESC`
- 问题：百万级行的 `ORDER BY` 需要全表扫描，耗时 10+ 秒
- 加 `LIMIT` 优化只能解决 Top K，无法高效获取任意用户排名
- 数据持续变化，缓存不可行

**方案 B：Redis Sorted Set** ✅ 推荐
- 每个元素自动按 score 排序，插入/更新/查询均为 O(log n)
- 底层：Hash Table（user → score）+ Skip List（score → user）
- Skip List 用多层索引加速搜索：62 步 → 11 步

**核心 Redis 命令：**

| 操作 | 命令 | 时间复杂度 |
|------|------|-----------|
| 用户得分 +1 | `ZINCRBY leaderboard_feb_2021 1 'mary1934'` | O(log n) |
| 获取 Top 10 | `ZREVRANGE leaderboard_feb_2021 0 9 WITHSCORES` | O(log n + m) |
| 查询用户排名 | `ZREVRANK leaderboard_feb_2021 'mary1934'` | O(log n) |
| 获取相邻排名 | `ZREVRANGE leaderboard_feb_2021 357 365` | O(log n + m) |

### Step 4: 部署方案

**方案 A：自建服务**
```
Client → Load Balancer → Web Servers → Redis (Leaderboard Sorted Set)
                                     → MySQL (User Profile + Points 持久化)
                                     → Redis (Top 10 用户 Profile Cache)
```

**方案 B：AWS Serverless** ✅ 新项目推荐
```
Client → API Gateway → Lambda Functions → Redis + MySQL
```
- API Gateway 映射 REST 端点到 Lambda
- Lambda 无需管理服务器，自动扩缩容
- 类似方案：Google Cloud Functions、Azure Functions

### Step 5: Scaling Redis（500M DAU 场景）

规模扩大 100 倍：存储 65 GB，QPS 250,000 → 需要分片

**Fixed Partition（按分数范围分片）** ✅ 推荐
- 将分数划分为固定区间，如 [1,100] [101,200] ... [901,1000]
- 每个区间一个 Redis Sorted Set
- Top 10 查询：直接取最高分区间的 Top 10
- 用户排名 = 本分片内 local rank + 所有更高分片的用户总数（`info keyspace` O(1) 获取）
- 需要辅助缓存存储 user_id → score 映射，处理跨分片迁移

**Hash Partition（Redis Cluster 自动分片）** ⚠️ 有局限
- 使用 CRC16(key) % 16384 分配到 hash slot
- 优点：自动分片，易于增删节点
- 缺点：Top K 需从每个 shard 取 Top K 再 scatter-gather 合并；K 大时延迟高；无法直接确定用户全局排名

### Step 6: NoSQL 替代方案（DynamoDB）

适合不熟悉 Redis 时在面试中讨论：
- 使用 Global Secondary Index：partition key = `game_name#{year-month}#p{partition_number}`，sort key = score
- Write Sharding 避免热分区：`user_id % N` 追加到 partition key
- 查询需 scatter-gather 跨所有分区合并
- 无法精确获取用户全局排名，但可以返回百分位（如 "Top 10-20%"）

---

## 关键设计考量 (Tradeoffs)

### 1. 安全性：谁来设置分数？
- **客户端直接设置** ❌ → 容易被中间人攻击篡改
- **服务端设置** ✅ → Game Server 验证游戏结果后调用 Leaderboard Service
- 对于服务端权威的游戏（如在线扑克），Game Server 可自动设置分数，无需客户端介入

### 2. Redis Sorted Set vs RDS
- RDS：简单但 O(n) 排名查询，百万级不可用
- Redis Sorted Set：O(log n)，自动排序，完美匹配排行榜需求
- Sorted Set = Hash Table + Skip List，兼具精确查找和范围查询能力

### 3. 持久化与容错
- Redis 主从复制：主节点故障时 read replica 提升为主节点
- MySQL 作为持久化后备：记录每次得分的 user_id + timestamp
- 灾难恢复：遍历 MySQL 记录，逐条 ZINCRBY 重建排行榜

### 4. 分片策略选择
- **Fixed Partition**：需要应用层手动管理，但支持用户精确排名
- **Hash Partition**：自动分片但 Top K 和排名查询复杂度高
- **DynamoDB Write Sharding**：权衡分区数 — 分区越多写越轻但读越复杂

### 5. 存储与 QPS 估算验证
- 单 Redis 节点：650 MB 存储 + 2,500 QPS → 完全可承受
- 写密集型应用需预留 2 倍内存用于 snapshot 持久化
- 使用 redis-benchmark 工具进行实际性能测试

### 6. 是否引入消息队列
- 单一消费者 → 直接同步调用，避免架构复杂度
- 多消费者（Analytics、Push Notification、多人游戏通知）→ Kafka 解耦

---

## 面试扩展话题

### 快速检索与打破平局（Faster Retrieval & Tie Breaking）
- 使用 Redis Hash 存储 user_id → user object 映射，避免每次查 MySQL
- 平局处理：额外存储 user_id → 最近获胜时间戳，同分时时间戳更早的排名更高

### 系统故障恢复（System Failure Recovery）
- MySQL 记录每次获胜的 user_id + timestamp
- 编写恢复脚本：遍历所有获胜记录，对每条记录调用 ZINCRBY，离线重建整个排行榜
- Redis 主从切换作为第一道防线，MySQL 重建作为最终兜底

### 其他可讨论话题
- **Serverless vs 自建**：新项目推荐 Serverless（Lambda），已有基础设施可自建
- **百分位排名**：大规模分片场景下，精确排名代价高，可用 cron job 定期分析分数分布，返回百分位近似值（如 "Top 10-20%"）
- **历史排行榜**：每月创建新 Sorted Set，旧数据迁移到历史存储
- **Redis 节点选型**：使用 redis-benchmark 实测，写密集型预留 2 倍内存

---

## 速写练习要点

盲画时重点记住这些组件和连接：

1. **核心数据流**：Client → Game Service → Leaderboard Service → Redis Sorted Set
2. **查询数据流**：Client → Leaderboard Service → Redis（Top 10 / Rank / 相邻排名）
3. **存储三件套**：Redis Sorted Set（排行榜）+ MySQL（User + Points 持久化）+ Redis Hash（用户 Profile 缓存）
4. **自建架构**：Client → Load Balancer → Web Servers → 三个存储组件
5. **Serverless 架构**：Client → API Gateway → Lambda → Redis + MySQL
6. **分片模式**：Fixed Partition 按分数范围切分 → Top K 取最高分片 → 排名 = local rank + 高分片总数
7. **Scatter-Gather**：每个 shard 取 Top K → 应用层合并排序 → 全局 Top K
8. **Redis 命令四件套**：ZINCRBY（加分）、ZREVRANGE（Top K）、ZREVRANK（排名）、ZREVRANGE（相邻）

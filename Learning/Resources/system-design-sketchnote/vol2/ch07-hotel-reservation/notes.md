# Chapter 7: Design a Hotel Reservation System

## 问题定义

为 Marriott 这样的连锁酒店设计预订系统。同样的设计思路适用于 Airbnb、航班预订、电影票预订等场景。

**核心需求：**
- 展示酒店/房间详情页
- 预订房间（按房型而非具体房间号）
- 管理员后台：增删改酒店和房间信息
- 支持 10% 超售（Overbooking）
- 房价动态变化（按日期和入住率浮动）

**非功能需求：**
- 高并发：旺季/大型活动期间热门酒店大量用户同时预订
- 适度延迟：预订流程可接受几秒延迟

**规模估算：**
- 5,000 酒店，100 万间房
- 70% 入住率，平均住 3 天 → 日均 ~240,000 笔预订
- 预订 TPS ~3（不高），但查询 QPS 放大 100 倍（漏斗模型：详情页 300 QPS → 确认页 30 QPS → 预订 3 TPS）

---

## 架构图索引

| Figure | 文件 | 内容 | 设计阶段 |
|--------|------|------|----------|
| 7-1 | ![Image00153.jpg](images/Image00153.jpg) | QPS 漏斗分布：详情页 300 → 确认页 30 → 预订 3 | 规模估算 |
| 7-2 | ![Image00154.gif](images/Image00154.gif) | 初版数据库 Schema（含 room_id 的简单模型） | 数据模型 |
| 7-3 | ![Image00155.jpg](images/Image00155.jpg) | Reservation 状态机：pending → paid / canceled / refunded / rejected | 数据模型 |
| 7-4 | ![Image00156.jpg](images/Image00156.jpg) | **高层架构图**：User/Admin → CDN + Public API Gateway / Internal API → Hotel/Rate/Reservation/Payment Service，各自带独立 DB，Hotel Service 带 Cache | 高层设计 |
| 7-5 | ![Image00157.jpg](images/Image00157.jpg) | 微服务间连接补充：Reservation Service ↔ Rate Service 等交互箭头 | 高层设计 |
| 7-6 | ![Image00158.gif](images/Image00158.gif) | **改进后的数据库 Schema**：按服务划分表——Hotel Service (hotel)、Rate Service (room_type_rate)、Guest Service (guest)、Reservation Service (room, room_type_inventory, reservation)，room_type_inventory 以 (hotel_id, room_type_id, date) 为复合主键 | 数据模型 |
| 7-7 | ![Image00159.jpg](images/Image00159.jpg) | 同一用户双击提交导致重复预订 | 并发控制 |
| 7-8 | ![Image00160.jpg](images/Image00160.jpg) | Idempotency Key 方案：用 reservation_id 做唯一约束避免重复预订 | 并发控制 |
| 7-9 | ![Image00161.jpg](images/Image00161.jpg) | 预订确认页 UI（来自 Booking.com） | 并发控制 |
| 7-10 | ![Image00162.jpg](images/Image00162.jpg) | Unique Constraint Violation：第二次插入同一 reservation_id 被数据库拒绝 | 并发控制 |
| 7-11 | ![Image00163.jpg](images/Image00163.jpg) | **Race Condition 时序图**：User 1 和 User 2 并发查询都看到 1 间剩余，各自 +1 后都提交成功（total_reserved 从 99 → 100 两次） | 并发控制 |
| 7-12 | ![Image00164.jpg](images/Image00164.jpg) | Pessimistic Locking：SELECT ... FOR UPDATE 锁住行，Transaction 2 等待 | 并发控制 |
| 7-13 | ![Image00165.jpg](images/Image00165.jpg) | **Optimistic Locking**：左侧无冲突（User 1 read v1 → write v2，User 2 read v2 → write v3），右侧有冲突（两个用户都 read v1，User 1 写成功变 v2，User 2 写 v2 失败） | 并发控制 |
| 7-14 | ![Image00166.jpg](images/Image00166.jpg) | Database Constraint：CHECK(total_inventory - total_reserved >= 0) 阻止超卖 | 并发控制 |
| 7-15 | ![Image00167.jpg](images/Image00167.jpg) | Database Sharding：按 hotel_id 分 16 个 shard，30,000 QPS / 16 = 1,875 QPS per shard | 扩展性 |
| 7-16 | ![Image00168.jpg](images/Image00168.jpg) | **Caching 架构**：Reservation Service 查询走 Inventory Cache (Redis)，更新走 Inventory DB (Shard)，DB 异步同步到 Cache | 扩展性 |
| 7-17 | ![Image00169.jpg](images/Image00169.jpg) | **Monolithic vs Microservice**：左侧三个服务共享 Hotel DB（ACID 保证），右侧每个服务独立 DB（需额外一致性机制） | 数据一致性 |
| 7-18 | ![Image00170.jpg](images/Image00170.jpg) | Monolithic 架构下单事务包裹多操作 | 数据一致性 |
| 7-19 | ![Image00171.jpg](images/Image00171.jpg) | Microservice 架构下跨服务操作失败需回滚（数据不一致问题） | 数据一致性 |

---

## 设计思路演进

### Step 1: API 与初版数据模型

**RESTful API 设计：**
- Hotel CRUD: `GET/POST/PUT/DELETE /v1/hotels/ID`
- Room CRUD: `GET/POST/PUT/DELETE /v1/hotels/ID/rooms/ID`
- Reservation: `GET/POST/DELETE /v1/reservations`（POST 请求包含 `reservationID` 作为 idempotency key）

**初版 Schema 的问题：** 初版按 `room_id` 预订，但实际酒店预订是按**房型**（room type）预订，具体房号在 check-in 时分配。这一差异要求数据模型根本性的调整。

### Step 2: 改进数据模型（关键转折）

```
预订对象: room_id → room_type_id（核心变更）
```

**核心表 `room_type_inventory`：**
- 复合主键：(hotel_id, room_type_id, date)
- 每天每个房型一行，预填充未来 2 年数据（~7300 万行，单库可承载）
- `total_inventory`：可售总量（减去维护中的房间）
- `total_reserved`：已预订数量
- 可用性检查：`(total_reserved + numberOfRoomsToReserve) <= 110% * total_inventory`（含 10% 超售）

**为什么选关系数据库？**
- 读多写少（浏览远多于预订）
- ACID 保证防止负库存、双重扣费、重复预订
- 业务数据关系稳定，适合关系模型

### Step 3: 高层架构（微服务）

```
User → CDN (静态资源)
     → Public API Gateway (限流/鉴权/路由)
          → Hotel Service + Cache (酒店/房间详情，静态数据可缓存)
          → Rate Service (动态定价)
          → Reservation Service (预订 + 库存管理)
          → Payment Service (支付)

Admin → Internal API (VPN 保护)
     → Hotel Management Service → 转发到各业务 Service
```

微服务间通信推荐使用 gRPC。

### Step 4: 并发控制三方案

**问题 1：同一用户重复提交**
- 客户端：灰掉/禁用按钮（不可靠，JS 可被绕过）
- 服务端：`reservation_id` 做主键 + Unique Constraint，重复插入直接被数据库拒绝

**问题 2：多用户抢同一房型（Race Condition）**

| 方案 | 原理 | 优点 | 缺点 | 推荐度 |
|------|------|------|------|--------|
| **Pessimistic Locking** | `SELECT ... FOR UPDATE` 锁行 | 简单直接，串行化更新 | 死锁风险，不可扩展，长事务阻塞 | 不推荐 |
| **Optimistic Locking** | version 列，写入时检查版本号 +1 | 不锁数据库，低竞争时高效 | 高竞争时大量重试，体验差 | 推荐（酒店 QPS 低） |
| **Database Constraint** | `CHECK(total_inventory - total_reserved >= 0)` | 最易实现 | 高竞争时大量失败；约束不易版本控制；非所有数据库支持 | 推荐（简单场景） |

### Step 5: 扩展性设计

**Database Sharding：**
- Shard Key: `hotel_id`（预订和查询都先选酒店）
- 公式：`hash(hotel_id) % number_of_servers`
- 示例：30,000 QPS / 16 shards = 1,875 QPS per shard

**Redis Cache 层：**
```
读路径: Reservation Service → Inventory Cache (Redis) → 快速返回
写路径: Reservation Service → Inventory DB → 异步同步 → Inventory Cache
```
- Cache Key: `hotelID_roomTypeID_{date}` → Value: 可用房间数
- 大部分不合格请求被 Cache 拦截，仅少数打到数据库
- 数据库仍做最终库存校验（Source of Truth）
- 异步同步方式：应用层更新 或 CDC (Change Data Capture, 如 Debezium)

**Cache 不一致容忍度：** Cache 与 DB 短暂不一致是可接受的——最终由数据库做校验，用户刷新页面时 Cache 已同步。

### Step 6: 微服务间数据一致性

**务实方案（本设计采用）：** Reservation Service 同时管理 reservation 和 inventory 表，放在同一关系数据库中，利用 ACID 事务保证一致性。

**纯微服务方案（每个服务独立 DB）的挑战：**
- 跨服务操作无法用单一事务
- 一个服务操作失败需要回滚另一个服务的已提交变更

**解决方案：**
- **2PC (Two-Phase Commit)**：阻塞协议，单节点故障阻塞全局，性能差
- **Saga**：一系列本地事务 + 补偿事务（Compensating Transactions），依赖最终一致性（Eventual Consistency）

---

## 关键设计考量 (Tradeoffs)

### 1. 按房型预订 vs 按具体房间预订
- 酒店场景预订的是房型（入住时分配房号），Airbnb 则是具体 listing
- 数据模型必须反映这一业务差异：`room_type_inventory` 表取代按 room_id 预订

### 2. 并发控制策略选择
- 酒店预订 TPS 低（~3），Optimistic Locking 和 Database Constraint 均适用
- 若扩展到 booking.com 级别（QPS x1000），需结合 Cache 层减少数据库压力
- Pessimistic Locking 虽然简单但扩展性差，不推荐

### 3. Overbooking 的实现
- 通过 `110% * total_inventory` 简单实现，无需额外逻辑
- 行业惯例：预期部分客户取消预订

### 4. 数据库选型与扩展
- 关系数据库（ACID + 读优化）vs NoSQL（写优化）→ 选关系数据库
- 单库 7300 万行足够，但需多副本保证高可用
- 扩展策略：归档历史数据 + 按 hotel_id 分片

### 5. Cache 与 DB 一致性
- 写入先走 DB（Source of Truth），异步同步到 Cache
- 短暂不一致可接受，DB 做最终校验
- CDC (Debezium) 是比应用层更新更可靠的同步方式

### 6. 微服务边界 vs 数据一致性
- 纯微服务（每服务独立 DB）增加巨大复杂度（2PC / Saga）
- 务实方案：在同一服务内合并强一致性需求的数据表
- 架构决策需权衡：微服务纯粹性 vs 实现复杂度

---

## 面试扩展话题

- **其他预订系统**：相同设计可应用于 Airbnb（按 listing_id）、航班预订（按座位类别）、电影票（按场次+座位）
- **动态定价**：Rate Service 根据入住率、季节、活动等因素实时调整房价
- **搜索功能**：酒店/房间搜索（按地点、日期、价格等筛选）不在本章范围，但实际系统必不可少
- **数据归档**：历史预订数据迁移到冷存储（Cold Storage），只保留当前和未来数据在热库
- **CDC 机制**：Debezium + Source Connector 从数据库读取变更，同步到 Redis 等下游系统
- **gRPC 通信**：微服务间通信推荐 gRPC，相比 REST 性能更优
- **多数据中心部署**：大规模系统需考虑跨区域部署和数据同步
- **Idempotency Key 设计**：预订 API 的幂等性是防止重复扣款/预订的关键
- **2PC vs Saga**：分布式事务的两种主流方案，Saga 更适合微服务（非阻塞、最终一致）

---

## 速写练习要点

盲画时重点记住这些组件和连接：

1. **高层架构**：User → CDN + API Gateway → Hotel Service / Rate Service / Reservation Service / Payment Service，各带独立 DB；Admin → Internal API → Hotel Management Service
2. **核心数据表**：`room_type_inventory` (hotel_id, room_type_id, date, total_inventory, total_reserved) 是系统核心
3. **预订流程**：查库存 → 检查 `(reserved + N) <= 110% * inventory` → 更新 total_reserved → 写 reservation 表
4. **并发控制**：Idempotency Key（防重复提交）+ Optimistic Locking / DB Constraint（防超卖）
5. **扩展路径**：DB Sharding (by hotel_id) + Redis Cache (读走缓存，写走 DB，异步同步)
6. **数据一致性**：Monolithic (共享 DB + ACID) vs Microservice (独立 DB + Saga/2PC)

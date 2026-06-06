# Chapter 3: Design Google Maps

## 问题定义

设计一个简化版 Google Maps，支持 10 亿 DAU，聚焦移动端场景。

**核心功能：**
- 用户位置更新 (Location Update)
- 导航服务 (Navigation)，包含 ETA 预估
- 地图渲染 (Map Rendering)

**非功能需求：**
- 精确性：不能给用户错误的路线
- 流畅性：客户端地图渲染需平滑
- 省流量/省电：移动端极其重要
- 通用的高可用与可扩展性

**关键估算：**
- 导航 QPS：~7,200（峰值 36,000）
- 位置更新 QPS：~200,000（批量每 15 秒上报，峰值 100 万）
- 地图瓦片总存储：~100 PB（21 级 zoom level）
- 导航数据消耗：~1.25 MB/分钟（30 km/h，200m x 200m 瓦片）

---

## 架构图索引

| Figure | 文件 | 内容 | 设计阶段 |
|--------|------|------|----------|
| 1 | ![Image00045.jpg](images/Image00045.jpg) | Latitude 和 Longitude 定位系统 | 基础概念 |
| 2 | ![Image00046.jpg](images/Image00046.jpg) | 不同地图投影方式（Mercator 等） | 基础概念 |
| 3 | ![Image00047.jpg](images/Image00047.jpg) | Geohashing 递归分割网格 | 基础概念 |
| 4 | ![Image00048.jpg](images/Image00048.jpg) | 道路网络的图数据结构（节点=交叉口，边=道路） | 基础概念 |
| 5 | ![Image00049.jpg](images/Image00049.jpg) | Routing Tiles 将道路网络分割为小图 | 基础概念 |
| 6 | ![Image00050.jpg](images/Image00050.jpg) | 多分辨率 Routing Tiles（本地道路/干道/高速公路） | 基础概念 |
| 7 | ![Image00051.jpg](images/Image00051.jpg) | **高层设计图**：Mobile User → Load Balancer → Navigation Service + Location Service，CDN 提供静态地图 | 高层设计 |
| 8 | ![Image00052.jpg](images/Image00052.jpg) | Location Service 架构 | 高层设计 |
| 9 | ![Image00053.jpg](images/Image00053.jpg) | 位置更新批量请求示意 | 高层设计 |
| 10 | ![Image00054.jpg](images/Image00054.jpg) | CDN 提供预生成地图瓦片 | 高层设计 |
| 11 | ![Image00055.jpg](images/Image00055.jpg) | 无 CDN vs 有 CDN 对比 | 高层设计 |
| 12 | ![Image00056.jpg](images/Image00056.jpg) | 地图渲染流程：Fetch URLs → Load Balancer → Map Tile Service → CDN 下载 | 高层设计 |
| 13 | ![Image00057.jpg](images/Image00057.jpg) | 预计算地图瓦片示例 | 深入设计 |
| 14 | ![Image00058.jpg](images/Image00058.jpg) | User Location Database 设计（Cassandra） | 深入设计 |
| 15 | ![Image00059.jpg](images/Image00059.jpg) | **位置数据流**：Location Service → Kafka → Traffic/ML/Routing Tile Processing/Analytics | 深入设计 |
| 16 | ![Image00060.jpg](images/Image00060.jpg) | Zoom Level 分级瓦片示意（Level 0/1/2） | 深入设计 |
| 17 | ![Image00061.jpg](images/Image00061.jpg) | **导航服务详细设计**：Navigation Service → Route Planner → Shortest Path / ETA / Ranker | 深入设计 |
| 18 | ![Image00062.jpg](images/Image00062.jpg) | Graph Traversal 跨 Routing Tiles 搜索过程 | 深入设计 |
| 19 | ![Image00063.jpg](images/Image00063.jpg) | 导航路线由 Routing Tiles 序列表示 | 深入设计 |
| 20 | ![Image00064.jpg](images/Image00064.jpg) | 层级 Routing Tiles 快速过滤受影响用户 | 深入设计 |
| 21 | ![Image00065.jpg](images/Image00065.jpg) | **最终设计图**：在 Figure 17 基础上增加 Adaptive ETA and Rerouting + Active Users 数据库 | 深入设计 |

---

## 基础知识 (Map 101)

### 定位与投影
- **经纬度**：Latitude（南北）+ Longitude（东西）定位地球上任意点
- **地图投影**：3D 球面 → 2D 平面，Google Maps 使用 Web Mercator 投影
- **Geocoding**：地址 ↔ 经纬度双向转换

### Geohashing
- 将地理区域编码为短字符串，递归分割网格
- 用于地图瓦片寻址和 Routing Tiles 的组织

### Routing Tiles
- 道路网络以图 (Graph) 表示：交叉口 = 节点，道路 = 边
- 全球道路网络太大无法一次加载，因此分割为 Routing Tiles
- 每个 Tile 包含局部图结构 + 对相邻 Tile 的引用
- **三级层次结构**：本地道路（小 Tile）→ 干道（中 Tile）→ 高速公路（大 Tile），不同层级间有跨级引用

---

## 设计思路演进

### Step 1: 高层设计 — 三大子系统

高层架构（Figure 7）将系统拆分为三个核心子系统：

```
Mobile User ──→ CDN（预生成地图瓦片 / Static Map Images）
    │
    ↓
Load Balancer
    ├──→ Navigation Service ──→ Geocoding DB + Routing Tiles (S3)
    └──→ Location Service   ──→ User Location DB (Cassandra)
```

**Location Service**：记录用户位置更新
- 客户端每秒记录 GPS，每 15 秒批量上报（减少 QPS 15x）
- 使用 HTTP keep-alive 协议
- 写入 Cassandra（高写入吞吐、AP 模型）

**Navigation Service**：计算从 A 到 B 的最快路线
- 输入 origin + destination，返回路线、距离、ETA
- 可容忍少量延迟，但精确性关键

**Map Rendering**：地图瓦片渲染
- 预生成不同 zoom level 的静态瓦片（256x256 PNG）
- 通过 CDN 就近分发，~200 个 POP 节点分担流量
- 客户端按 geohash 拼接 URL 获取瓦片

### Step 2: 地图渲染的 Tradeoff — 客户端计算 vs 服务端中间层

```
方案A：客户端直接通过 geohash 算法拼接 CDN URL（硬编码）
方案B：引入 Map Tile Service 作为中间层构造 URL
```

方案 A 简单高效，但算法硬编码在所有客户端，修改成本高风险大。
方案 B（Figure 12）增加一次网络调用，但获得运维灵活性：可随时切换编码方式。

**流程（Figure 12）**：
1. 客户端向 Map Tile Service 请求瓦片 URL
2. Load Balancer 转发请求
3. Map Tile Service 根据位置 + zoom level 返回 9 个 URL（当前 + 周围 8 个）
4. 客户端从 CDN 下载瓦片

### Step 3: 深入 Location Service — Kafka 驱动的数据流

位置数据不仅写入数据库，还流入 Kafka 消息队列，支撑多个下游服务（Figure 15）：

```
Mobile User → Load Balancer → Location Service → User Location DB (Cassandra)
                                      ↓
                                    Kafka
                    ┌─────────┬────────┬──────────┐
                    ↓         ↓        ↓          ↓
             Traffic Update   ML    Routing Tile  Analytics
              Service      Service  Processing    Service
                ↓            ↓        ↓            ↓
            Traffic DB  Personal DB  Routing    Analytics DB
                                   Tiles (S3)
```

### Step 4: 深入 Navigation Service — 路线规划流水线

导航服务（Figure 17）是一条多阶段流水线：

```
Mobile User → Navigation Service
                  ↓
            Geocoding Service → Geocoding DB (Redis)
                  ↓
            Route Planner Service
              ├→ Shortest Path Service → Routing Tiles (S3)
              ├→ ETA Service → Traffic DB
              └→ Ranker → Filter Service（避开收费站/高速等）
                  ↓
            返回 Top-K 路线
```

**Shortest Path Service**：
- 使用 A* 算法变体，在 Routing Tiles 上增量搜索
- 从起点 Tile 开始，按需加载邻近 Tile（含跨级 Tile）
- 结果可缓存（道路图很少变化）

**ETA Service**：
- 基于 Machine Learning（GNN）预测 ETA
- 结合实时交通 + 历史数据
- 需预测 10-20 分钟后的交通状况

**Ranker**：
- 接收所有候选路线 + ETA，应用用户过滤条件
- 按时间排序，返回 Top-K 结果

### Step 5: Adaptive ETA 与动态重路由

**问题**：导航过程中路况变化，需实时更新 ETA 并推送给用户

**用户追踪优化**：
- 朴素方案：存储每个用户的 Routing Tiles 序列，扫描所有用户 → O(n x m) 太慢
- 优化方案：为每个用户存储当前 Tile + 上层 super-Tile 的层级引用，先用大 Tile 快速过滤无关用户

**推送协议选择**：
- Mobile Push Notification ❌（payload 限制 4KB，不支持 Web）
- Long Polling ❌（服务端开销大）
- SSE 可行但单向
- **WebSocket** ✅（双向通信，支持 last-mile delivery 等场景）

**最终设计（Figure 21）**：在 Figure 17 基础上增加 Adaptive ETA and Rerouting 模块 + Active Users 数据库

---

## 关键设计考量 (Tradeoffs)

### 1. 地图瓦片：动态生成 vs 预计算
- **动态生成**：服务端压力巨大，无法利用缓存 ❌
- **预计算 + CDN**：静态文件天然适合缓存，200 个 POP 就近分发 ✅
- 存储成本 ~100 PB 看似巨大，但可通过压缩和跳过无人区域降至 50-67 PB

### 2. 位置上报频率：实时 vs 批量
- 每秒上报 → 3M QPS，服务端压力极大 ❌
- 每 15 秒批量上报 → 200K QPS，降低 15x ✅
- 可根据用户速度动态调整（堵车时降频）

### 3. 客户端 Geohash 计算 vs Map Tile Service 中间层
- 客户端计算：零网络开销，但修改需全量发版，风险高
- 服务端中间层：多一次 RPC，但获得运维灵活性
- 这是一个经典的 **客户端逻辑 vs 服务端灵活性** 权衡

### 4. Routing Tiles 的分层设计
- 跨国路线不能用街道级 Tile（图太大内存爆炸）
- 三级分层：Local → Arterial → Highway，算法可跨级跳转
- 在精确性和计算效率之间取得平衡

### 5. 数据库选型
- **User Location DB**：Cassandra（高写入吞吐、AP 模型、按 user_id 分区 + timestamp 排序）
- **Geocoding DB**：Redis（读多写少、KV 快速查找）
- **Routing Tiles**：S3 Object Storage + 本地缓存（二进制邻接表，非关系型）
- **Traffic DB**：由 Kafka 流处理实时更新

### 6. 地图渲染优化：Raster vs Vector Tiles
- Raster（PNG）：兼容性好，但缩放时像素化
- **Vector Tiles**（WebGL）：压缩率高、缩放平滑、节省大量带宽 ✅
- 现代 Google Maps 已迁移到 Vector Tiles

### 7. 实时路况感知与 ETA 预测
- Location 数据 → Kafka → Traffic Update Service → Traffic DB
- ETA 使用 GNN (Graph Neural Networks) 做交通预测
- 需要同时考虑当前路况和未来 10-20 分钟的变化趋势

### 8. Adaptive ETA 的用户匹配效率
- 朴素扫描 O(n x m) 无法应对百万级并发导航用户
- 层级 Routing Tile 索引实现快速过滤：先检查大 Tile 排除无关用户，再细查小 Tile

---

## 面试扩展话题

- **多站点导航 (Multi-stop Navigation)**：为企业客户（DoorDash、Uber、Lyft 等）提供最优访问顺序 + 实时导航，本质上是 Traveling Salesman Problem 的近似求解
- **不同出行方式**：驾车、步行、公交、骑行等，需要不同的 Routing Tiles 和 ETA 模型
- **离线地图**：预下载区域地图瓦片 + Routing Tiles，无网络环境下仍可导航
- **实时事件处理**：道路封闭、事故、施工等，如何快速更新 Routing Tiles 并通知受影响用户
- **隐私与数据合规**：海量位置数据的匿名化处理、GDPR 合规、数据保留策略
- **地图数据更新流水线**：如何持续整合多来源道路数据，通过用户位置数据自动发现新路/封路
- **CDN 成本优化**：~200 POP、每秒 62.5 GB 地图数据，如何通过客户端缓存和 Vector Tiles 大幅降低成本

---

## 速写练习要点

盲画时重点记住这些组件和连接：

1. **高层三叉结构**：Mobile User 分三条路 — CDN（地图）、Navigation Service（路线）、Location Service（位置）
2. **地图渲染数据流**：Client → Map Tile Service → 返回 9 个 URL → Client 从 CDN 下载
3. **位置数据流**：Client → Location Service → Cassandra + Kafka → 四个下游（Traffic / ML / Routing Tile Processing / Analytics）
4. **导航流水线**：Navigation Service → Geocoding → Route Planner → (Shortest Path + ETA + Ranker) → Top-K 路线
5. **最终设计增量**：在导航流水线上加 Adaptive ETA + Active Users DB + WebSocket 推送
6. **存储选型**：Cassandra（位置）、Redis（Geocoding）、S3（Routing Tiles + Map Tiles）、CDN（地图分发）
7. **关键数字**：1B DAU、200K 位置更新 QPS、~100 PB 地图瓦片、1.25 MB/分钟导航数据量

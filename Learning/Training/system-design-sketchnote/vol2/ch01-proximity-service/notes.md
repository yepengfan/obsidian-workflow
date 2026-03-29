# Chapter 1 (Vol.2): Design a Proximity Service

## 问题定义

设计一个附近搜索服务（如 Yelp 附近餐厅搜索），根据用户位置和半径返回附近商家。

**核心需求：**
- 根据经纬度 + 半径搜索附近商家
- 商家信息 CRUD（新增/更新次日生效，非实时）
- 查看商家详情
- 搜索半径选项：0.5km / 1km / 2km / 5km / 20km

**非功能需求：**
- 低延迟（快速返回搜索结果）
- 高可用 & 可扩展（高峰时段流量尖峰）
- 数据隐私合规（GDPR, CCPA）

**估算：** 100M DAU，200M 商家，Search QPS ~5,000

---

## 架构图索引

| Figure | 文件 | 内容 | 设计阶段 |
|--------|------|------|----------|
| 1 | ![Image00007](images/Image00007.jpg) | Yelp 搜索界面参考 | 背景 |
| - | ![Image00008](images/Image00008.jpg) | Business 表结构（business_id 主键） | 数据模型 |
| 2 | ![Image00009](images/Image00009.jpg) | **高层架构**：LBS + Business Service + DB Cluster（Primary-Secondary） | 高层设计 |
| 3 | ![Image00010](images/Image00010.jpg) | 二维搜索：画圆找商家（朴素方案） | 算法 |
| 4 | ![Image00011](images/Image00011.jpg) | 二维索引的交集问题：两个维度各返回大量数据 | 算法 |
| 5 | ![Image00012](images/Image00012.jpg) | 地理空间索引分类（Hash: geohash 等 vs Tree: quadtree, S2 等） | 算法 |
| 6 | ![Image00013](images/Image00013.jpg) | Even Grid（均匀网格）：分布不均问题 | 算法 |
| 7 | ![Image00014](images/Image00014.jpg) | Geohash 原理：第一次切分（经纬度二分） | 算法 |
| 8 | ![Image00015](images/Image00015.jpg) | Geohash：递归细分为更小网格 | 算法 |
| 9 | ![Image00016](images/Image00016.jpg) | Geohash 共享前缀 = 地理接近（9q8zn 示例） | 算法 |
| 10 | ![Image00017](images/Image00017.jpg) | 边界问题1：La Roche-Chalais(u000) vs Pomerol(ezzz)，30km 但无共享前缀 | 算法 |
| 11 | ![Image00018](images/Image00018.jpg) | 边界问题2：长共享前缀但属于不同 geohash 格子 | 算法 |
| 12 | ![Image00019](images/Image00019.jpg) | 搜索范围扩展：逐步去掉 geohash 末位扩大范围 | 算法 |
| 13 | ![Image00020](images/Image00020.jpg) | Quadtree 递归细分过程（200M 商家） | 算法 |
| 14 | ![Image00021](images/Image00021.jpg) | Quadtree 树结构：递归四分直到叶节点 ≤ 100 商家 | 算法 |
| 15 | ![Image00022](images/Image00022.jpg) | 真实 Quadtree 案例（Denver 地区，密集区更细分） | 算法 |
| 16 | ![Image00023](images/Image00023.gif) | Hilbert 曲线（Google S2 的基础，2D→1D 映射） | 算法 |
| 17 | ![Image00024](images/Image00024.jpg) | S2 Geofencing：可覆盖任意形状区域 | 算法 |
| 18 | ![Image00025](images/Image00025.jpg) | Geohash 删除商家：直接删对应行，简单 | 对比 |
| 19 | ![Image00026](images/Image00026.jpg) | Quadtree 删除商家：需从 root 遍历到 leaf，O(log n) | 对比 |
| 9 | ![Image00027](images/Image00027.jpg) | Geo Index 表方案1：一行存 JSON 数组（不推荐） | 数据库 |
| 10 | ![Image00028](images/Image00028.jpg) | Geo Index 表方案2：每行一个 (geohash, business_id)（推荐） | 数据库 |
| 20 | ![Image00029](images/Image00029.jpg) | 多 Region/AZ 部署 LBS，就近服务用户 | 深入设计 |
| 21 | ![Image00030](images/Image00030.jpg) | **最终架构图**：LBS + Business Service + Redis Cluster(Geohash+Business Info) + DB Cluster | 深入设计 |

---

## 设计思路演进

### Step 1: API 设计

```
搜索：GET /v1/search/nearby?latitude=X&longitude=Y&radius=500
商家：GET/POST/PUT/DELETE /v1/businesses/{:id}
```

### Step 2: 高层架构

```
User → Load Balancer
         ├─ /search/nearby → LBS (Location-Based Service) → Read Replicas
         └─ /businesses     → Business Service → Primary DB (Write)
                                               → Replicas (Read)
```

**两个独立服务：**
1. **LBS**：只读，无写请求，高 QPS，无状态 → 易水平扩展
2. **Business Service**：读（商家详情，高 QPS）+ 写（CRUD，低 QPS）

**数据库：** Primary-Secondary 模式，写入 Primary → 复制到 Replicas。因为商家信息不需实时更新，复制延迟可接受。

### Step 3: 地理空间索引算法选型

| 方案 | 核心思想 | 优点 | 缺点 |
|------|----------|------|------|
| **二维搜索** | 直接 SQL WHERE lat/lng BETWEEN | 直观 | 全表扫描，即使有索引也需两集合求交，极慢 |
| **均匀网格** | 世界地图均分小格 | 简单 | 商家分布不均（纽约 vs 沙漠），相邻格查找困难 |
| **Geohash** | 经纬度递归二分 → base32 编码 | 实现简单，无需建树，更新容易 | 固定精度，无法按密度调整；边界问题 |
| **Quadtree** | 递归四分直到格内商家 ≤ 阈值 | 自适应密度，支持 k-nearest | 需建树（启动慢），多线程更新需锁 |
| **Google S2** | 球面 → Hilbert 曲线 → 1D 索引 | 支持 Geofencing，精度灵活 | 复杂，面试难解释 |

**业界选择：**
- Geohash：Bing Maps, Redis, MongoDB, Lyft
- Quadtree：Yext
- Geohash + Quadtree 同时使用：Elasticsearch
- S2：Google Maps, Tinder

**面试推荐**：Geohash（简单易解释）或 Quadtree（自适应密度）

### Step 4: Geohash 深入

**精度与半径映射：**
| 半径 | Geohash 长度 | 格子大小 |
|------|-------------|---------|
| 0.5 km | 6 | 1.2km x 609m |
| 1 km | 5 | 4.9km x 4.9km |
| 2 km | 5 | 4.9km x 4.9km |
| 5 km | 4 | 39.1km x 19.5km |
| 20 km | 4 | 39.1km x 19.5km |

**边界问题及解决：**
1. 相邻位置无共享前缀（跨经线/赤线）→ 搜索当前格 + 8 个邻居格
2. 结果不足 → 去掉 geohash 末位，扩大搜索范围

### Step 5: Quadtree 深入

```
内存估算（200M 商家）：
- 叶节点：~2M 个（每个 ≤ 100 商家），每个 832 bytes
- 内部节点：~0.67M 个，每个 64 bytes
- 总计：~1.71 GB → 单机可装
- 建树时间：几分钟

部署考量：
- 启动时建树，期间不可服务 → 滚动发布，逐批重启
- 更新：每日 nightly job 增量重建（商家次日生效的约定支持此方案）
```

---

## 深入设计

### Geo Index 表设计

```
方案1（JSON 数组）❌：geohash → [business_id_1, business_id_2, ...]
  - 更新需扫描整个数组，需加锁

方案2（每行一条）✅：(geohash, business_id) 复合主键
  - 增删简单，无需锁
```

### 扩展 Geo Index
- 数据量不大（~1.71 GB）→ **不需要分片**
- 读负载高 → **加 Read Replicas** 即可（比 Sharding 简单得多）

### 缓存策略

```
Redis Cluster:
├─ "Geohash" Cache: geohash → [business_ids]    （按 3 种精度缓存：4, 5, 6）
└─ "Business Info" Cache: business_id → {name, address, ...}

内存估算：8 bytes x 200M x 3 = ~5 GB → 单台 Redis 可装
更新策略：Nightly job 刷新（次日生效的业务约定）
```

**需要缓存吗？不一定！**
- 数据集小，可装进 DB working set → 查询本身就快
- 先加 Read Replicas 提升吞吐
- 如果仍有瓶颈 → 再加 Cache

**Cache Key 设计考量：**
- lat/lng 不适合做 cache key ❌：手机定位不精确（每次略有偏差），用户移动后坐标微变
- geohash 做 cache key ✅：小范围位置变动仍映射到同一 geohash，天然适合缓存

### 多 Region / AZ 部署

- 用户就近访问 → 降低延迟
- 流量均衡分配 → 高密度地区（如日韩）独立 Region
- 数据合规 → 某些国家要求数据本地存储，DNS 路由限制

---

## 最终架构（搜索请求流）

```
1. 用户发送 (lat, lng, radius=500m) → Load Balancer
2. Load Balancer → LBS
3. LBS 计算 geohash 长度 (500m → length=6)
4. LBS 计算当前格 + 8 个邻居格的 geohash
5. 对每个 geohash 并行查 Redis "Geohash" Cache → 获取 business_ids
6. 用 business_ids 查 Redis "Business Info" Cache → 获取商家详情
7. 计算距离、排序、返回结果
```

---

## 关键设计考量 (Tradeoffs)

### 1. Geohash vs Quadtree
- **Geohash**：简单、易更新、存数据库 → 适合通用场景
- **Quadtree**：自适应密度、支持 k-nearest → 适合需动态调整的场景
- 两者可共存（如 Elasticsearch）

### 2. 缓存是否必要
- 数据集小 + 读多写少 → Read Replicas 可能就够了
- 加缓存需 benchmarking + 成本分析 → 不要盲目加

### 3. 读写分离
- LBS 只读 Read Replicas → 不影响 Primary 的写性能
- 商家更新次日生效 → 允许复制延迟，大幅简化设计

### 4. Geohash 边界问题
- 核心解法：搜索 9 个格子（自身 + 8 邻居）
- 这是面试中容易被追问的点

### 5. Quadtree 运维复杂度
- 启动需几分钟建树 → 需要滚动发布策略
- 更新需遍历到叶节点 → 多线程场景需锁机制
- 实际生产中多用 nightly rebuild 规避复杂度

---

## 速写练习要点

盲画时重点记住这些组件和连接：

1. **两条路径**：/search/nearby → LBS (只读) | /businesses → Business Service (读写)
2. **数据库**：Primary → Write，Replicas → Read（Primary-Secondary 模式）
3. **两层 Redis Cache**：Geohash Cache + Business Info Cache
4. **LBS 无状态**：易水平扩展，多 Region/AZ 部署
5. **搜索流程**：经纬度 → geohash → 查 9 个格子 → 获取 IDs → 获取详情 → 排序返回
6. **更新流程**：Business Service → Primary DB → Replicate → Nightly job 刷 Cache

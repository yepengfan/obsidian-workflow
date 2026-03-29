# Chapter 9: Design S3-like Object Storage

## 问题定义

设计一个类似 Amazon S3 的对象存储系统，支持海量非结构化数据的持久化存储。

**核心需求：**
- Bucket 创建
- Object 上传与下载
- Object 版本控制（Versioning）
- 列出 Bucket 中的 Object（支持 prefix 过滤）
- 同时高效处理小文件（几十 KB）和大文件（几 GB 以上）

**非功能需求：**
- 100 PB 数据规模
- 数据持久性 6 nines（99.9999%）
- 服务可用性 4 nines（99.99%）
- 存储效率：在保证可靠性和性能的前提下降低存储成本

**容量估算：**
- 对象分布：20% 小文件（<1MB）、60% 中等文件（1~64MB）、20% 大文件（>64MB）
- 按 40% 存储利用率计算，约 6.8 亿个 Object
- 元数据约 0.68 TB（每条 ~1KB）

---

## 存储系统基础对比

| 特性 | Block Storage | File Storage | Object Storage |
|------|--------------|-------------|----------------|
| 可变内容 | 支持 | 支持 | 不支持（通过 versioning 实现） |
| 成本 | 高 | 中高 | 低 |
| 性能 | 中高到极高 | 中高 | 低到中 |
| 数据访问 | SAS/iSCSI/FC | CIFS/SMB/NFS | RESTful API |
| 可扩展性 | 中等 | 高 | 极高 |
| 适用场景 | VM、数据库 | 通用文件共享 | 二进制/非结构化数据、归档备份 |

---

## 架构图索引

| Figure | 文件 | 内容 | 设计阶段 |
|--------|------|------|----------|
| 1 | ![Image00188.jpg](images/Image00188.jpg) | Block/File/Object 三种存储类型对比图 | 背景知识 |
| 2 | ![Image00189.jpg](images/Image00189.jpg) | UNIX 文件系统 vs 对象存储的类比（inode → metadata store） | 背景知识 |
| 3 | ![Image00190.jpg](images/Image00190.jpg) | Bucket 与 Object 的结构关系 | 背景知识 |
| 4 | ![Image00191.jpg](images/Image00191.jpg) | **高层架构图**：User → Load Balancer → API Service → IAM / Metadata Store / Data Store（含 Primary + Secondary 节点） | 高层设计 |
| 5 | ![Image00192.jpg](images/Image00192.jpg) | 上传 Object 的 7 步流程 | 高层设计 |
| 6 | ![Image00193.jpg](images/Image00193.jpg) | 下载 Object 的流程：通过 object name 查 UUID 再从 Data Store 获取数据 | 高层设计 |
| 7 | ![Image00194.jpg](images/Image00194.jpg) | API Service 与 Data Store 交互的上传/下载流程 | 深入设计 |
| 8 | ![Image00195.gif](images/Image00195.gif) | **Data Store 组件图**：Data Routing Service ↔ Placement Service ↔ Data Node（Primary + 2 Secondary），含 Heartbeat 和 Data Replication 箭头 | 深入设计 |
| 9 | ![Image00196.jpg](images/Image00196.jpg) | Virtual Cluster Map：展示数据中心 → 机架 → 节点的物理拓扑 | 深入设计 |
| 10 | ![Image00197.jpg](images/Image00197.jpg) | **数据持久化流程**：API Service → Data Routing Service → Placement Service 选主 → Primary Node 写入 → Replication 到 Secondary → 返回 ObjId | 深入设计 |
| 11 | ![Image00198.jpg](images/Image00198.jpg) | 一致性与延迟的 Tradeoff：三种 ACK 策略对比 | 深入设计 |
| 12 | ![Image00199.jpg](images/Image00199.jpg) | 小文件合并为大文件的 WAL 写入方式（read-write file → read-only file） | 深入设计 |
| 13 | ![Image00200.gif](images/Image00200.gif) | Object Mapping Table：object_id / file_name / start_offset / object_size | 深入设计 |
| 14 | ![Image00201.jpg](images/Image00201.jpg) | 更新后的数据持久化流程（含 WAL 文件追加 + object_mapping 写入） | 深入设计 |
| 15 | ![Image00202.jpg](images/Image00202.jpg) | 多数据中心跨 AZ 复制示意图 | 持久性 |
| 16 | ![Image00203.jpg](images/Image00203.jpg) | **Erasure Coding (4+2)**：数据分成 d1-d4 + 计算 p1/p2 → 节点崩溃丢失 d3/d4 → 用 d1/d2/p1/p2 重建 | 持久性 |
| 17 | ![Image00204.jpg](images/Image00204.jpg) | (8+4) Erasure Coding 跨 12 个 Failure Domain 分布 | 持久性 |
| 18 | ![Image00205.jpg](images/Image00205.jpg) | Replication（200% 开销） vs Erasure Coding（50% 开销）空间对比 | 持久性 |
| 19 | ![Image00206.jpg](images/Image00206.jpg) | Checksum 生成过程 | 正确性验证 |
| 20 | ![Image00207.jpg](images/Image00207.jpg) | Checksum 校验：原始数据与传输后数据对比 | 正确性验证 |
| 21 | ![Image00208.jpg](images/Image00208.jpg) | Data Node 文件结构：每个 Object 附加 checksum + 文件末尾附加整体 checksum | 正确性验证 |
| 22 | ![Image00209.gif](images/Image00209.gif) | 数据库 Schema：bucket 表和 object 表结构 | 元数据模型 |
| 23 | ![Image00210.jpg](images/Image00210.jpg) | Object Versioning 上传流程 | 版本控制 |
| 24 | ![Image00211.jpg](images/Image00211.jpg) | Versioned Metadata 表结构：同一 object_name 多行记录不同 object_version | 版本控制 |
| 25 | ![Image00212.jpg](images/Image00212.jpg) | 删除版本化对象：插入 delete marker 成为当前版本 | 版本控制 |
| 26 | ![Image00213.gif](images/Image00213.gif) | **Multipart Upload 时序图**：Initiation（获取 uploadID）→ 分片上传（Part + ETag）→ Completion（汇总所有 Part/ETag 完成重组） | 大文件优化 |
| 27 | ![Image00214.jpg](images/Image00214.jpg) | Garbage Collection Compaction：跳过已删除对象，将存活对象合并到新文件 | 垃圾回收 |

---

## 设计思路演进

### Step 1: 核心设计哲学 -- 分离 Metadata 和 Data

```
类比 UNIX 文件系统：
  inode (文件名+元数据)  ←→  Metadata Store (object 元数据)
  磁盘数据块 (文件内容)  ←→  Data Store (object 数据)

关键特性：
  Object 不可变 (Immutable) → 写入后只能删除或替换，不能增量修改
  Key-Value 模式 → Object URI 是 Key，Object Data 是 Value
  写少读多 → 95% 请求是读操作 (LinkedIn 数据)
```

### Step 2: 高层架构

```
                  ┌──────────────┐
    User ──→ Load Balancer ──→ API Service
                                 │
                 ┌───────────────┼───────────────┐
                 ↓               ↓               ↓
              IAM           Metadata Store    Data Store
         (认证/授权)       (Metadata DB)    (Primary + Secondary Nodes)
```

**组件职责：**
- **Load Balancer**：将 RESTful API 请求分发到多个 API Server
- **API Service**：无状态，水平扩展，编排各内部服务调用
- **IAM**：集中处理 Authentication（你是谁）和 Authorization（你能做什么）
- **Metadata Store**：存储 Object 元数据（name、bucket、version 等）
- **Data Store**：存储实际 Object 数据，所有操作基于 UUID

### Step 3: Data Store 深入设计

```
Data Store 三大组件：

                  Data Routing Service (无状态, RESTful/gRPC)
                         ↕
                  Placement Service (5~7 节点 Paxos/Raft 集群)
                    │  维护 Virtual Cluster Map
                    │  通过 Heartbeat 监控 Data Node
                    ↓
          ┌─── Primary Data Node ───┐
          │                          │
    Secondary Node 1          Secondary Node 2
         (3 副本复制，跨 Failure Domain 分布)
```

**数据持久化流程（5 步）：**
1. API Service 发送写请求到 Data Routing Service
2. Data Routing Service 生成 UUID，查询 Placement Service 获取 Primary Node
3. 数据发送到 Primary Node
4. Primary 本地存储后复制到 2 个 Secondary Node
5. 全部副本完成后返回 UUID

**数据在节点内的组织方式：**
- 小文件不单独存储（避免浪费 disk block 和耗尽 inode）
- 采用 WAL 式追加写入：多个小 Object 合并到一个大文件中
- 文件达到阈值（几 GB）→ 标记为 read-only → 新建 read-write 文件
- 每个 CPU core 可分配独立的 read-write 文件以提高写入并发
- 使用 SQLite 存储每个 Data Node 本地的 `object_mapping` 表（object_id → file_name + offset + size）

### Step 4: 持久性保障

**Replication（3 副本）：**
- 年故障率 0.81% → 3 副本 → ~6 nines 持久性
- 简单直接，无额外计算开销
- 存储开销 200%

**Erasure Coding：**
- (4+2) 方案：数据分 4 块 + 2 个 parity → 可容忍任意 2 块丢失
- (8+4) 方案：数据分 8 块 + 4 个 parity → 可容忍任意 4 块丢失
- 存储开销仅 50%，持久性可达 11 nines
- 代价：读取需从多节点聚合，写入需计算 parity，复杂度更高

**Failure Domain 隔离：**
- 节点级 → 机架级 → 可用区（AZ）级
- 副本分布在不同 AZ，抵御大规模故障（电力中断、自然灾害等）

**Checksum 校验：**
- 每个 Object 末尾附加 checksum（如 MD5）
- 文件标记为 read-only 前附加整文件 checksum
- 读取时比对 checksum，不一致则从其他副本/parity 恢复

### Step 5: 元数据模型与 Sharding

**Schema：**
- `bucket` 表：bucket_name（全局唯一）、owner_id 等
- `object` 表：bucket_id、object_name、object_id (UUID)、object_version 等

**Sharding 策略：**
- bucket 表数据量小（~10GB），单库 + 读副本即可
- object 表需要分片：
  - 按 bucket_id 分片 → 热点问题（单 bucket 可能有数十亿 Object）
  - 按 object_id 分片 → 无法高效按 URI 查询
  - **最终选择：按 hash(bucket_name, object_name) 分片** → 兼顾均匀分布和 URI 查询效率

**Listing 优化：**
- 分片后跨 shard 查询 + 分页非常复杂（每个 shard 返回不同数量结果，需追踪多个 offset）
- 解决方案：将 listing 数据反范式化到按 bucket_id 分片的独立表中
- Tradeoff：牺牲一定写入开销，换取 listing 查询的简单性和可接受的性能

### Step 6: Object Versioning

```
Versioning 开启后：

上传同名 Object：
  → 不覆盖旧记录，新增一行（新 object_id + 新 object_version TIMEUUID）
  → 当前版本 = 同名记录中最大的 TIMEUUID

删除 Object：
  → 不物理删除，插入 delete marker 作为新版本
  → GET 请求遇到 delete marker → 返回 404
  → 旧版本数据仍然保留，可恢复
```

### Step 7: Multipart Upload（大文件优化）

```
Initiation:  Client → Data Store (获取 uploadID)
Upload:      分片上传 Part 1~N + uploadID → 每片返回 ETag (md5 checksum)
Completion:  Client 发送 uploadID + 所有 Part Number/ETag → Data Store 重组 → Success
```

- 大文件切分为固定大小的 Part（如 200MB）独立上传
- 单个 Part 失败只需重传该 Part，无需从头开始
- 重组完成后旧 Part 成为垃圾，由 Garbage Collector 回收

### Step 8: Garbage Collection

**垃圾来源：**
- Lazy 删除的 Object（标记删除但未物理移除）
- 孤立数据（如中断的 multipart upload 残留 Part）
- Checksum 校验失败的损坏数据

**Compaction 机制：**
- 从旧 read-only 文件中复制存活 Object 到新文件（跳过已删除的）
- 更新 `object_mapping` 表（file_name + start_offset），用数据库事务保证一致性
- 积累足够多的 read-only 文件后批量执行，避免产生大量碎片小文件

---

## 关键设计考量 (Tradeoffs)

### 1. Replication vs Erasure Coding

| 维度 | Replication | Erasure Coding |
|------|-------------|----------------|
| 持久性 | 6 nines（3 副本） | 11 nines（8+4） |
| 存储开销 | 200% | 50% |
| 计算资源 | 无额外计算 | 需要计算 parity |
| 写性能 | 直接复制，较快 | 需先算 parity，较慢 |
| 读性能 | 从单副本读取 | 需从多节点读取 |
| 故障恢复 | 直接从副本读 | 需重建丢失数据 |
| 适用场景 | 延迟敏感 | 成本敏感、冷数据 |

### 2. 一致性 vs 延迟 (Data Replication ACK 策略)

| 策略 | 一致性 | 延迟 |
|------|--------|------|
| 等待全部 3 节点 ACK | 最强 | 最高（受最慢副本制约） |
| 等待 Primary + 1 Secondary ACK | 中等 | 中等 |
| 仅等待 Primary ACK | 最弱（Eventual Consistency） | 最低 |

### 3. Metadata Sharding 策略选择

| 方案 | 优点 | 缺点 |
|------|------|------|
| 按 bucket_id | 同 bucket 数据集中 | 热点 shard（大 bucket） |
| 按 object_id | 负载均匀 | 无法按 URI 高效查询 |
| 按 hash(bucket_name, object_name) | 均匀 + URI 查询友好 | Listing 需要额外方案 |

### 4. 小文件存储策略
- 单独存储 → 浪费 disk block + 耗尽 inode
- 合并存储（WAL 方式）→ 空间利用率高，但需维护 mapping 表
- 每 core 独立 read-write 文件 → 解决并发写入瓶颈

### 5. Listing 实现
- 分片数据库上的 listing + 分页 → 复杂度极高（多 shard 多 offset）
- 反范式化独立 listing 表（按 bucket_id 分片）→ 简单但有写入冗余
- 对象存储场景中 listing 性能不是首要目标（所有商业产品都是次优性能）

### 6. Versioning 的存储成本
- 每个版本保留完整 Object 数据，不做增量存储
- Delete Marker 不删除数据，持续占用空间
- 需要生命周期策略（Lifecycle Policy）配合管理旧版本

---

## 面试扩展话题

原书 Wrap-up 中提到的额外讨论方向：

1. **存储类型选择**：Block vs File vs Object 的使用场景区分，Object Storage 在成本、持久性、规模上的优势，以及在性能和可变性上的牺牲
2. **Erasure Coding 的深入实现**：Reed-Solomon 编码原理、不同 (k+m) 配置的持久性计算、与 Replication 的混合使用策略
3. **Multipart Upload 的容错设计**：Part 重试、超时清理、uploadID 管理、abandoned upload 的垃圾回收
4. **Metadata Sharding 的分页挑战**：多 shard 聚合排序、cursor 编码多 offset、反范式化 listing 表的数据一致性保障
5. **数据完整性保障链**：Checksum 在写入、存储、传输、读取各环节的应用，结合 Erasure Coding 的自动修复
6. **Garbage Collection 策略**：Compaction 时机选择、对读写性能的影响、后台任务调度
7. **Lifecycle Policy**：自动过期删除、存储层级迁移（如 S3 Standard → Glacier）
8. **Cross-Region Replication**：跨区域复制的一致性模型、带宽优化、冲突解决

---

## 速写练习要点

盲画时重点记住这些组件和连接：

1. **高层架构**：User → Load Balancer → API Service → { IAM, Metadata Store (Metadata DB), Data Store (Primary + 2 Secondary) }
2. **Data Store 内部**：Data Routing Service ↔ Placement Service（Paxos/Raft 集群） ↔ Data Nodes（Heartbeat 监控 + Virtual Cluster Map）
3. **数据持久化流程**：API Service → Data Routing → Placement 选主 → Primary 写入 → Replicate 到 Secondary → 返回 UUID
4. **Data Node 内部**：多个小 Object → WAL 追加到大文件 → object_mapping (SQLite) 维护定位信息
5. **Erasure Coding**：原始数据 → 分成 k 块 + 计算 m 个 parity → 分散到不同 Failure Domain → 丢失任意 m 块可重建
6. **Multipart Upload**：Initiation (uploadID) → 分片上传 (Part + ETag) → Completion (重组)
7. **Versioning**：同名 Object 多行记录（不同 object_id + TIMEUUID），删除 = 插入 delete marker
8. **Garbage Collection**：Compaction 将存活 Object 从旧文件复制到新文件，更新 mapping 表

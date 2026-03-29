# Chapter 12: Design a Chat System

## 问题定义

设计一个类似 Facebook Messenger 的聊天系统，支持 50M DAU。

**核心需求：**
- 1对1 聊天 + 小群聊（最多 100 人）
- 低延迟消息投递
- 在线状态（Online Presence）
- 多设备同步
- 推送通知
- 仅支持文本消息，长度 < 100K 字符
- 聊天记录永久存储

---

## 架构图索引

| Figure | 文件 | 内容 | 设计阶段 |
|--------|------|------|----------|
| 12-1 | ![Image00144](images/Image00144.jpg) | 流行聊天应用概览 | 背景 |
| 12-2 | ![Image00145](images/Image00145.jpg) | Client-Server 基本通信模型 | 高层设计 |
| 12-3 | ![Image00146](images/Image00146.jpg) | Polling（轮询） | 协议选型 |
| 12-4 | ![Image00147](images/Image00147.jpg) | Long Polling（长轮询） | 协议选型 |
| 12-5 | ![Image00148](images/Image00148.jpg) | WebSocket 连接升级过程（HTTP → WS） | 协议选型 |
| 12-6 | ![Image00149](images/Image00149.jpg) | WebSocket 用于双向通信（sender + receiver） | 协议选型 |
| 12-7 | ![Image00150](images/Image00150.jpg) | **高层设计**：Stateless（Service Discovery, Auth, Group Mgmt, User Profile）+ Stateful（Chat Service）+ 3rd Party（Push Notification） | 高层设计 |
| 12-8 | ![Image00151](images/Image00151.jpg) | **完整高层架构**：Chat/Presence/API/Notification/KV Store | 高层设计 |
| 12-9 | ![Image00152](images/Image00152.jpg) | 1对1 消息表设计（message_id 主键） | 数据模型 |
| 12-10 | ![Image00153](images/Image00153.jpg) | 群聊消息表设计（channel_id + message_id 复合主键） | 数据模型 |
| 12-11 | ![Image00154](images/Image00154.jpg) | Service Discovery（Zookeeper）4 步流程 | 深入设计 |
| 12-12 | ![Image00155](images/Image00155.jpg) | **1对1 消息流**：6 步端到端流程（含 5a/5b 分支） | 深入设计 |
| 12-13 | ![Image00156](images/Image00156.jpg) | 多设备消息同步（cur_max_message_id） | 深入设计 |
| 12-14 | ![Image00157](images/Image00157.jpg) | **小群聊 - 发送端**：消息复制到每个成员的 sync queue | 深入设计 |
| 12-15 | ![Image00158](images/Image00158.jpg) | **小群聊 - 接收端**：从自己的 inbox 读取多个 sender 的消息 | 深入设计 |
| 12-16 | ![Image00159](images/Image00159.jpg) | 用户登录 → Presence Server → KV Store 写入 online 状态 | 在线状态 |
| 12-17 | ![Image00160](images/Image00160.jpg) | 用户登出 → KV Store 写入 offline 状态 | 在线状态 |
| 12-18 | ![Image00161](images/Image00161.jpg) | 心跳机制：每 5s 心跳，30s 无响应标记离线 | 在线状态 |
| 12-19 | ![Image00162](images/Image00162.jpg) | 在线状态 Fanout（Pub/Sub，每对好友一个 channel） | 在线状态 |

---

## 设计思路演进

### Step 1: 通信协议选型

```
Polling ❌       → 浪费资源，大部分请求返回空
Long Polling ⚠️  → 发送和接收可能不在同一服务器；无法检测断线
WebSocket ✅✅   → 双向持久连接，发送和接收都用同一协议
```

**关键决策**：发送端可用 HTTP，但 WebSocket 双向都用更简洁统一。

### Step 2: 高层架构分层

```
User
 ├─ HTTP ──→ Load Balancer → Stateless Services (Login/Signup/Profile)
 └─ WS ───→ Real-time Service
               ├─ Chat Servers (消息收发)
               └─ Presence Servers (在线状态)

Supporting:
 ├─ API Servers (通用 CRUD)
 ├─ Notification Servers (推送)
 ├─ Key-Value Store (聊天记录)
 └─ Service Discovery / Zookeeper (分配 Chat Server)
```

**三类服务：**
1. **Stateless Services**：Service Discovery, Authentication, Group Management, User Profile → 传统 HTTP，Load Balancer 分发
2. **Stateful Service**：Chat Service → 客户端与 Chat Server 保持持久 WS 连接
3. **Third-party**：Push Notification（离线用户通知）

### Step 3: 存储选型

| 数据类型 | 存储 | 原因 |
|----------|------|------|
| 用户信息、好友列表 | 关系型数据库 (MySQL) | 结构化数据，需要 ACID |
| 聊天消息 | Key-Value Store (HBase/Cassandra) | 数据量巨大（60B msg/day），读写 1:1，需水平扩展 |

**为什么不用关系型数据库存消息？**
- 数据量太大，索引增长后随机访问代价高 (long tail)
- KV Store 天然支持水平扩展和低延迟

**业界实践**：Facebook Messenger → HBase，Discord → Cassandra

### Step 4: 数据模型

**1对1 消息表：** `message_id` 做主键
**群聊消息表：** `(channel_id, message_id)` 复合主键，`channel_id` 做 partition key

**Message ID 生成方案：**
1. MySQL auto_increment ❌ → NoSQL 不支持
2. Snowflake (全局 64-bit) ✅ → 全局唯一
3. **Local Sequence Generator** ✅✅ → 组内唯一即可，实现简单

---

## 深入设计

### Service Discovery (Zookeeper)

```
1. User A 登录
2. Load Balancer → API Server 认证
3. Zookeeper 选最优 Chat Server（地理位置、负载）
4. User A ←→ Chat Server 2 (WebSocket)
```

### 1对1 消息流（Figure 12-12，共 6 步）

```
1. User A → Chat Server 1（发消息）
2. Chat Server 1 → ID Generator（获取 message_id）
3. Chat Server 1 → Message Sync Queue
4. Message Sync Queue → KV Store 持久化
5a. User B 在线 → Message Sync Queue → Chat Server 2（转发）
5b. User B 离线 → Message Sync Queue → Push Notification Server（推送）
6. Chat Server 2 → User B（通过持久 WebSocket 连接投递）
```

### 多设备同步

每个设备维护 `cur_max_message_id`，只拉取 ID > 该值的新消息。

### 小群聊消息流

```
User A 发消息 → 消息被复制到每个群成员的 Message Sync Queue
                ├─ User B 的 inbox
                └─ User C 的 inbox

每个客户端只需检查自己的 inbox 获取新消息
```

**WeChat 模式**：每人一份 copy，简单但只适合小群（WeChat 上限 500 人）

### 在线状态 (Online Presence)

```
登录  → Presence Server → KV Store: {user_id: online, last_active_at: xxx}
登出  → Presence Server → KV Store: {user_id: offline}
断线  → 心跳机制：每 5s 发一次，超过 30s 无心跳 → 标记离线
```

**状态 Fanout：** Pub/Sub 模型
- 每对好友维护一个 channel (A-B, A-C, A-D)
- User A 状态变化 → 发布到所有 channel
- 好友通过订阅的 channel 收到状态更新

**大群限制**：100K 成员群不能每次状态变化都广播 → 改为进入群组或手动刷新时拉取

---

## 关键设计考量 (Tradeoffs)

### 1. WebSocket vs HTTP
- **Tradeoff**：WebSocket 需要服务端维护持久连接，增加连接管理复杂度
- **决策**：实时性要求高，WS 是必须的；但非实时功能（登录、profile）仍用 HTTP

### 2. Stateful Chat Server
- **Tradeoff**：客户端绑定特定 Chat Server，不像 Stateless 服务那样自由切换
- **应对**：Service Discovery 动态分配 + 断线后重新分配

### 3. 消息存储：KV Store vs RDBMS
- **Tradeoff**：KV Store 牺牲了复杂查询能力，换取水平扩展和低延迟
- **关键因素**：60B 消息/天，读写 1:1，需要支持 long tail 查询

### 4. 群聊消息分发：Fan-out Write vs Fan-out Read
- **Fan-out Write**（本设计）：发送时复制到每个成员 inbox → 读取简单，适合小群
- **Fan-out Read**：读取时实时查询 → 适合大群，但读取延迟高

### 5. 在线状态 Fanout 的扩展性
- 小群（<500）：Pub/Sub 实时广播 ✅
- 大群（>500）：Pull-based 拉取 ✅

### 6. 面试扩展话题
- **媒体文件支持**：压缩、云存储、缩略图
- **端到端加密**：仅 sender/receiver 可读（参考 WhatsApp）
- **客户端缓存**：减少 client-server 数据传输
- **地理分布式网络**：类似 Slack Flannel，就近缓存用户数据
- **错误处理**：Chat Server 下线时 Zookeeper 重新分配；消息重试 + 队列机制

---

## 速写练习要点

盲画时重点记住这些组件和连接：

1. **双协议入口**：HTTP (stateless) + WebSocket (stateful)
2. **核心分层**：Load Balancer → Stateless Services + Real-time Service (Chat + Presence)
3. **消息流**：Sender → Chat Server → Sync Queue → KV Store → Receiver Chat Server → Receiver
4. **离线路径**：Sync Queue → Push Notification Server
5. **Service Discovery**：Zookeeper 选最优 Chat Server
6. **存储**：MySQL (用户数据) + KV Store (消息)
7. **在线状态**：Heartbeat + Pub/Sub Fanout

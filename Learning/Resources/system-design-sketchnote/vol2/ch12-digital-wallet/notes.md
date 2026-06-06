# Chapter 12: Design a Digital Wallet

## 问题定义

设计一个支持跨钱包余额转账的数字钱包后端系统（如 PayPal 钱包间转账）。

**核心需求：**
- 支持两个 digital wallet 之间的 balance transfer
- 支持 1,000,000 TPS
- 可靠性至少 99.99%
- 支持 transactional guarantees（事务保证）
- 支持 reproducibility（可复现性）：能通过重放历史数据重建任意时刻的余额

**粗略估算：**
- 单个关系数据库节点约 1,000 TPS
- 每笔转账需要 2 次操作（扣款 + 入账），实际需 2,000,000 TPS
- 需要约 2,000 个数据库节点
- 设计目标之一：提升单节点 TPS，降低总节点数

---

## 架构图索引

| Figure | 文件 | 内容 | 设计阶段 |
|--------|------|------|----------|
| 1 | ![Image00251.jpg](images/Image00251.jpg) | Digital wallet 概念：银行卡充值，电商消费 | 问题定义 |
| 2 | ![Image00252.jpg](images/Image00252.jpg) | 跨钱包余额转账操作 | 问题定义 |
| 3 | ![Image00253.jpg](images/Image00253.jpg) | **In-memory 方案**：Wallet Service + Redis 分片 + Zookeeper | 高层设计 |
| 4 | ![Image00254.jpg](images/Image00254.jpg) | 关系数据库替换 Redis，支持事务 | 高层设计 |
| 5 | ![Image00255.jpg](images/Image00255.jpg) | Two-Phase Commit (2PC) 流程 | 分布式事务 |
| 6 | ![Image00256.jpg](images/Image00256.jpg) | 2PC coordinator 崩溃问题（单点故障） | 分布式事务 |
| 7 | ![Image00257.jpg](images/Image00257.jpg) | TC/C Try 阶段：A 扣款，C 为 NOP | 分布式事务 |
| 8 | ![Image00258.jpg](images/Image00258.jpg) | TC/C Confirm 阶段：C 入账 | 分布式事务 |
| 9 | ![Image00259.jpg](images/Image00259.jpg) | TC/C Cancel 阶段：A 回滚 +$1 | 分布式事务 |
| 10 | ![Image00260.jpg](images/Image00260.jpg) | Phase Status Table 存储 TC/C 进度 | 分布式事务 |
| 11 | ![Image00261.jpg](images/Image00261.jpg) | Unbalanced state：Try 阶段后总余额不平衡 | 分布式事务 |
| 12 | ![Image00262.jpg](images/Image00262.jpg) | Out-of-order execution：Cancel 先于 Try 到达 | 分布式事务 |
| 13 | ![Image00263.jpg](images/Image00263.jpg) | Saga workflow：线性执行 + 回滚 | 分布式事务 |
| 14 | ![Image00264.jpg](images/Image00264.jpg) | **Event Sourcing 静态视图**：Command → State Machine → Event → State | Event Sourcing |
| 15 | ![Image00265.jpg](images/Image00265.jpg) | Event Sourcing 动态视图（加入时间维度） | Event Sourcing |
| 16 | ![Image00266.gif](images/Image00266.gif) | Command queue（Kafka） | Event Sourcing |
| 17 | ![Image00267.jpg](images/Image00267.jpg) | State Machine 5 步工作流程 | Event Sourcing |
| 18 | ![Image00268.jpg](images/Image00268.jpg) | 通过 replay events 重建历史状态 | Event Sourcing |
| 19 | ![Image00269.jpg](images/Image00269.jpg) | **CQRS 架构**：写路径 + 多个只读 State Machine | Event Sourcing |
| 20 | ![Image00270.jpg](images/Image00270.jpg) | 文件化 Command 和 Event（mmap） | 高性能优化 |
| 21 | ![Image00271.jpg](images/Image00271.jpg) | 文件化 Command + Event + State（RocksDB） | 高性能优化 |
| 22 | ![Image00272.jpg](images/Image00272.jpg) | **Snapshot 架构**：mmap + RocksDB + Object Store 快照 + 只读 State Machine | 高性能优化 |
| 23 | ![Image00273.jpg](images/Image00273.jpg) | Raft 共识算法：5 节点容忍 2 节点故障 | 可靠性 |
| 24 | ![Image00274.jpg](images/Image00274.jpg) | **Raft Node Group**：Leader 接收 Command，Follower 同步 Event，右侧为读路径 | 可靠性 |
| 25 | ![Image00275.jpg](images/Image00275.jpg) | Pull 模型：外部用户周期性拉取状态 | 分布式 ES |
| 26 | ![Image00276.jpg](images/Image00276.jpg) | Pull + Reverse Proxy 模型 | 分布式 ES |
| 27 | ![Image00277.jpg](images/Image00277.jpg) | Push 模型：只读 State Machine 推送状态给 Reverse Proxy | 分布式 ES |
| 28 | ![Image00278.jpg](images/Image00278.jpg) | **最终设计**：多 Partition + Raft + TC/C/Saga Coordinator + Reverse Proxy | 最终设计 |
| 29 | ![Image00279.jpg](images/Image00279.jpg) | 最终设计的完整编号执行流程 | 最终设计 |

---

## 设计思路演进

### Step 1: In-Memory 分片方案

```
Transfer Command
       ↓
  Wallet Service (stateless, 可水平扩展)
       ↓                        ↘
  Redis Node {A}    Redis Node {B}    Redis Node {C}
       ↕
  Zookeeper (分片信息)
```

- 用 Redis 做 key-value 存储 `<user, balance>`
- 通过 hash(accountID) % N 进行分片
- Zookeeper 存储分片配置

**问题：** 没有事务保证。Wallet Service 更新两个 Redis 节点时，如果中途崩溃，会导致不完整转账（钱凭空消失或凭空产生）。

### Step 2: 分布式事务方案

将 Redis 替换为 transactional relational database，然后用分布式事务协议保证原子性。

#### 2PC (Two-Phase Commit)
- Phase 1: Coordinator 在多个 DB 上执行读写，所有 DB 加锁
- Phase 2: 所有 DB 回复 "yes" → commit；任一回复 "no" → abort
- **缺点：** 锁持有时间长，性能差；Coordinator 是单点故障

#### TC/C (Try-Confirm/Cancel)
- Try: 对 A 扣款 -$1（真实事务已提交），对 C 发 NOP
- Confirm: 对 C 入账 +$1（新事务）
- Cancel: 对 A 回滚 +$1（补偿事务）
- 每个阶段都是独立事务（与 2PC 不同：2PC 的两阶段在同一事务内）
- **关键约束：** Try 阶段必须先扣款（choice 1），不能先入账或同时操作

**Phase Status Table：** 记录 TC/C 进度到事务数据库中，放在扣款方的 DB 内，用于崩溃恢复。

**Out-of-order 处理：** Cancel 可能先于 Try 到达节点，需要用 flag 标记"已见 Cancel 未见 Try"，后续 Try 检查此 flag 直接返回失败。

#### Saga
- 所有操作线性执行，每个操作是独立事务
- 失败时从当前位置逆序回滚（补偿事务）
- 协调方式：Choreography（去中心化）或 Orchestration（中心协调器，推荐）

| 对比 | TC/C | Saga |
|------|------|------|
| 操作顺序 | 任意 | 线性 |
| 并行执行 | 支持 | 不支持 |
| 延迟敏感 | 更优（可并行） | 较差 |
| 复杂度 | 较高 | 较低（微服务标准） |

**问题：** 分布式事务方案难以进行数据审计，无法追溯历史余额变更原因。

### Step 3: Event Sourcing 方案

引入 Event Sourcing（事件溯源）解决可审计性和可复现性问题。

**四个核心概念：**
- **Command**: 外部意图（转账请求），放入 FIFO 队列
- **Event**: 验证后的确定性事实（"已转账"），不可变，放入 FIFO 队列
- **State**: 当前余额状态，用 key-value 存储
- **State Machine**: 驱动整个流程，验证 Command 生成 Event，应用 Event 更新 State；行为必须确定性（无随机性、无外部 I/O）

```
Command → [State Machine: Validate] → Event → [State Machine: Apply] → State
                    ↑ Read                              ↓ Update
                    └──────────── State (DB) ───────────┘
```

**Reproducibility（核心优势）：**
- Event list 不可变 + State Machine 确定性 = 任意时刻状态可重建
- 能回答审计问题：任意时刻余额、历史正确性验证、代码变更后的逻辑验证

**CQRS (Command Query Responsibility Segregation)：**
- 一个写路径 State Machine + 多个只读 State Machine
- 只读 State Machine 从 Event queue 构建不同视图（余额查询、审计追踪等）
- 架构最终一致（eventually consistent）

### Step 4: 高性能 Event Sourcing

逐步将所有数据本地化以最大化 I/O 吞吐：

1. **文件化 Command/Event**: 用 mmap 将 append-only 文件映射到内存，避免网络开销（替代 Kafka）
2. **文件化 State**: 用 RocksDB（LSM tree，写优化）替代远程数据库
3. **Snapshot**: 周期性将 State 保存为快照文件（存储在 HDFS 等 Object Store），加速重放

```
┌─ memory ──────────────────────────────┐
│ Command List → [SM] → Event List      │──Replicate──→ Read-only SM → Query
│                 ↕                     │
│          RocksDB cache                │
└───┬──────────┬─────────┬──────────────┘
  mmap       mmap      mmap
    ↓          ↓         ↓
Command    RocksDB    Event          Snapshot → Object Store (HDFS)
 File       File      File
```

### Step 5: 可靠性 - Raft 共识

本地文件方案使节点变为有状态，成为单点故障。用 Raft 算法复制 Event list：

- Leader 接收 Command、生成 Event、通过 Raft 同步到 Follower
- 所有节点（含 Follower）处理 Event list 更新 State
- Leader 崩溃 → 自动选举新 Leader，客户端重发未完成的 Command
- 3 节点容忍 1 故障，5 节点容忍 2 故障

**为什么只需复制 Event？**
- State 和 Snapshot 可从 Event list 重放生成
- Command 到 Event 的转换可能包含随机因素，不具备确定性
- 因此 Event 是唯一需要强可靠性保证的数据

### Step 6: 分布式 Event Sourcing（最终设计）

**Pull vs Push：**
- Pull 模型延迟高 → 加 Reverse Proxy → 改为 Push 模型（只读 SM 实时推送状态给 Reverse Proxy）

**最终架构：**
```
User → Saga/TC/C Coordinator → Partition 1 (Raft Group: Leader + Followers)
              ↓                        ↕ Raft 同步 Event
              ↓                  Read-only SM → Reverse Proxy → User
              ↓
         Partition 2 (Raft Group: Leader + Followers)
              ↕ Raft 同步 Event
         Read-only SM → Reverse Proxy → User
```

- 按 hash(key) % N 分区
- 每个 Partition 是一个 Raft Node Group
- Saga/TC/C Coordinator 协调跨 Partition 的分布式事务
- Phase Status Table 追踪事务状态
- Reverse Proxy 将异步 Event Sourcing 转为同步响应

---

## 关键设计考量 (Tradeoffs)

### 1. In-Memory vs 数据库
- Redis 快但无事务保证、数据不持久
- 关系数据库支持事务但单节点 TPS 有限（约 1,000）

### 2. 分布式事务协议选择
- **2PC**: 简单但锁时间长、Coordinator 单点故障、需要数据库层面支持（X/Open XA）
- **TC/C**: 数据库无关、可并行执行，但需要在应用层实现补偿逻辑
- **Saga**: 微服务标准、线性执行易理解，但无法并行
- 延迟敏感 + 多服务 → TC/C；简单场景或微服务标准 → Saga

### 3. TC/C 操作顺序约束
- Try 阶段必须先扣款（debit），不能先入账（credit）
- 先入账会导致 Cancel 时钱可能已被花掉，违反事务保证
- 并发操作两端会引入复杂边界情况

### 4. Unbalanced State
- TC/C 的 Try 和 Confirm 之间存在中间状态（总余额暂时不平衡）
- 这是应用层分布式事务的固有特征，最终由 Confirm/Cancel 修复
- 低层方案（如 2PC）由数据库内部处理，对应用透明

### 5. Event Sourcing vs 传统事务方案
- 传统方案只存最终状态，丢失变更历史，难以审计
- Event Sourcing 保存完整不可变事件历史，支持重放验证
- 代价：架构复杂度增加，需要 CQRS 分离读写

### 6. 本地文件 vs 远程存储
- 远程 Kafka + DB：网络延迟、依赖外部系统
- 本地 mmap + RocksDB：最大化 I/O 吞吐，顺序写极快
- 代价：节点变为有状态，需要 Raft 保证可靠性

### 7. Raft 复制粒度
- 只复制 Event（不复制 Command/State/Snapshot）
- Event 是不可变的历史事实，可确定性地重建 State
- Command → Event 转换可能含随机因素，不能仅靠 Command 保证 reproducibility

### 8. Pull vs Push 模型
- Pull: 简单但非实时，高频拉取会过载系统
- Push (via Reverse Proxy): 只读 SM 主动推送，接近实时响应
- Reverse Proxy 将异步 Event Sourcing 转化为同步用户体验

---

## 面试扩展话题

- **金额精度问题**: amount 字段用 string 而非 double，避免浮点精度丢失（详见 Chapter 11 Payment System）
- **幂等性设计**: API 中的 transaction_id (UUID) 用于去重，防止重复转账
- **Out-of-order execution 处理**: TC/C 中网络延迟可能导致 Cancel 先于 Try 到达，需 flag 机制处理
- **Snapshot 策略**: 金融场景通常每天 00:00 做快照，用于当日交易验证和审计
- **Raft Leader 选举与故障恢复**: Leader 崩溃后自动选举新 Leader，未完成的 Command 需客户端重发
- **CQRS 多视图**: 不同只读 State Machine 可构建不同视图（余额查询、审计追踪、异常检测等）
- **Saga Choreography vs Orchestration**: 去中心化 vs 中心协调，数字钱包通常选 Orchestration
- **Event 生成的非确定性**: Command → Event 可能包含随机因素（I/O、随机数），这是 Event 必须被独立持久化和复制的原因
- **数据分区策略**: 按 hash(accountID) % N 分区，每个 Partition 独立 Raft Group
- **外汇处理**: 原书明确排除在范围外，但实际系统需要考虑汇率和多币种

---

## 速写练习要点

盲画时重点记住以下组件和演进路线：

1. **演进主线**: In-Memory Redis → Transactional DB + 分布式事务 → Event Sourcing → 文件化 + Raft → 分布式 ES
2. **Event Sourcing 核心流**: Command → [State Machine: Validate] → Event → [State Machine: Apply] → State
3. **高性能架构**: mmap(Command File) → SM → mmap(Event File) → RocksDB(State) + Snapshot → Object Store
4. **Raft Node Group**: Leader(Command→Event) + 2 Followers，Event 通过 Raft 同步，右侧为只读 Read Path
5. **最终设计**: Saga Coordinator → 多个 Partition(Raft Group) + Reverse Proxy(Push)，Phase Status Table 追踪进度
6. **CQRS 分离**: 写路径（Leader SM）和读路径（只读 SM + 不同视图）分离，eventually consistent

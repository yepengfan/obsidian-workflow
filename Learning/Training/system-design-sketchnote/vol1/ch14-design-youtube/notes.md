# Chapter 14: Design YouTube

## 问题定义

设计一个类似 YouTube 的视频流媒体服务，支持视频上传和在线观看。

**核心需求：**
- 快速上传视频
- 流畅的视频流播放（streaming，非下载）
- 支持切换视频质量（自适应 bitrate）
- 低基础设施成本
- 高可用、可扩展、高可靠
- 客户端支持：移动端、Web 浏览器、Smart TV

**粗略估算：**
- 5M DAU，每人每天看 5 个视频
- 10% 用户每天上传 1 个视频，平均 300MB
- 日存储需求：5M * 10% * 300MB = 150TB
- CDN 日费用：5M * 5 * 0.3GB * $0.02 = $150,000/天

---

## 架构图索引

| Figure | 文件 | 内容 | 设计阶段 |
|--------|------|------|----------|
| 14-1 | ![Image00182.jpg](images/Image00182.jpg) | YouTube 首页截图 | 背景 |
| 14-2 | ![Image00183.jpg](images/Image00183.jpg) | Amazon CloudFront CDN 定价表 | 粗略估算 |
| 14-3 | ![Image00184.jpg](images/Image00184.jpg) | **高层架构**：Client（PC/手机/TV）→ CDN（streaming video）+ API Servers（everything else） | 高层设计 |
| 14-4 | ![Image00185.jpg](images/Image00185.jpg) | **视频上传流程全景图**：User → Load Balancer → API Servers → Metadata DB/Cache；Original Storage → Transcoding Servers → Transcoded Storage → CDN；Completion Queue → Completion Handler | 高层设计 |
| 14-5 | ![Image00186.jpg](images/Image00186.jpg) | **视频上传详细流程**（带编号步骤 1→2→3a/3b→4）：上传 → 转码 → 分发到 CDN + 通知完成 | 高层设计 |
| 14-6 | ![Image00187.jpg](images/Image00187.jpg) | 元数据更新流程：Client 并行发送 metadata 到 API Servers | 高层设计 |
| 14-7 | ![Image00188.jpg](images/Image00188.jpg) | 视频流播放流程：Client 从最近的 CDN Edge Server 获取视频流 | 高层设计 |
| 14-8 | ![Image00189.jpg](images/Image00189.jpg) | **DAG 模型**：Original Video 拆分为 Video/Audio/Metadata 三路；Video 路包含 Inspection、Transcoding、Thumbnail、Watermark 等 Tasks，最终 Assemble | 深入设计 |
| 14-9 | ![Image00190.jpg](images/Image00190.jpg) | 视频编码输出示例（不同分辨率文件） | 深入设计 |
| 14-10 | ![Image00191.jpg](images/Image00191.jpg) | **视频转码架构**：Preprocessor → DAG Scheduler → Resource Manager → Task Workers → Encoded Video；Preprocessor 同时写入 Temporary Storage 供 Task Workers 读取 | 深入设计 |
| 14-11 | ![Image00192.jpg](images/Image00192.jpg) | Preprocessor 组件详情 | 深入设计 |
| 14-12 | ![Image00193.jpg](images/Image00193.jpg) | DAG 简化表示（2 个节点 1 条边） | 深入设计 |
| 14-13 | ![Image00194.jpg](images/Image00194.jpg) | DAG 配置文件示例 | 深入设计 |
| 14-14 | ![Image00195.jpg](images/Image00195.jpg) | DAG Scheduler 组件详情 | 深入设计 |
| 14-15 | ![Image00196.jpg](images/Image00196.jpg) | DAG Scheduler 分阶段拆分示例（Stage 1 → Stage 2） | 深入设计 |
| 14-16 | ![Image00197.jpg](images/Image00197.jpg) | Resource Manager 组件详情 | 深入设计 |
| 14-17 | ![Image00198.jpg](images/Image00198.jpg) | Resource Manager 内部结构：Task Queue + Worker Queue + Running Queue + Task Scheduler | 深入设计 |
| 14-18 | ![Image00199.jpg](images/Image00199.jpg) | Task Workers 组件详情 | 深入设计 |
| 14-19 | ![Image00200.jpg](images/Image00200.jpg) | 不同类型的 Task Workers（video/audio/thumbnail 等） | 深入设计 |
| 14-20 | ![Image00201.jpg](images/Image00201.jpg) | Temporary Storage 组件详情 | 深入设计 |
| 14-21 | ![Image00202.jpg](images/Image00202.jpg) | Encoded Video 输出组件 | 深入设计 |
| 14-22 | ![Image00203.jpg](images/Image00203.jpg) | 视频按 GOP 分块上传 | 优化 |
| 14-23 | ![Image00204.jpg](images/Image00204.jpg) | 客户端分块上传示意 | 优化 |
| 14-24 | ![Image00205.jpg](images/Image00205.jpg) | 全球多 Upload Center 就近上传 | 优化 |
| 14-25 | ![Image00206.jpg](images/Image00206.jpg) | 优化前：模块串行依赖，难以并行 | 优化 |
| 14-26 | ![Image00207.jpg](images/Image00207.jpg) | **优化后**：各模块间加 Message Queue 实现松耦合并行（Original Storage → MQ → Download → MQ → Encoding → MQ → Upload → Encoded Storage → CDN） | 优化 |
| 14-27 | ![Image00208.jpg](images/Image00208.jpg) | Pre-signed URL 安全上传流程 | 优化 |
| 14-28 | ![Image00209.jpg](images/Image00209.jpg) | 热门视频走 CDN，长尾视频走 Video Server | 优化 |

---

## 设计思路演进

### 主线一：视频上传流程 (Video Uploading Flow)

#### Step 1: 高层架构拆分
```
系统三大组件：
  Client（PC / Mobile / Smart TV）
      ├── streaming video ──→ CDN
      └── everything else ──→ API Servers
```

**关键决策**：利用现有云服务（CDN + Blob Storage），不从零构建。即使 Netflix 也用 AWS，Facebook 也用 Akamai CDN。

#### Step 2: 上传全景流程
```
User ──→ Load Balancer ──→ API Servers ──→ Metadata DB + Metadata Cache
  │
  └──→ Original Storage (Blob)
            │
            ↓
      Transcoding Servers
            │
      ┌─────┴─────┐
      ↓            ↓
  Transcoded    Completion Queue
  Storage          │
      │            ↓
      ↓       Completion Handler
     CDN           │
                   ↓
             更新 Metadata DB + Cache
```

**两条并行流：**
- **Flow a（上传视频文件）**：User → Original Storage → Transcoding → Transcoded Storage → CDN；同时 Completion Queue → Handler 更新元数据
- **Flow b（更新元数据）**：Client 并行发送 metadata（文件名、大小、格式等）到 API Servers → Metadata DB + Cache

#### Step 3: 视频转码深入设计

**为什么需要 Transcoding？**
- 原始视频占空间巨大（1 小时 60fps 高清 → 数百 GB）
- 不同设备/浏览器支持不同格式
- 需根据网络带宽自适应分辨率切换

**编码格式两部分：**
- Container（容器）：.avi, .mov, .mp4
- Codecs（编解码器）：H.264, VP9, HEVC

**DAG 模型（借鉴 Facebook SVE）：**
```
Original Video
  ├──→ Video ──→ [Inspection | Transcoding | Thumbnail | Watermark] ──┐
  ├──→ Audio ──→ [Audio Encoding] ──────────────────────────────────────┤→ Assemble
  └──→ Metadata ────────────────────────────────────────────────────────┘
```
用 DAG 实现灵活的 pipeline 定义 + 任务并行执行。

**转码架构六大组件：**
```
Preprocessor → DAG Scheduler → Resource Manager → Task Workers → Encoded Video
      │                                                ↑
      └──────────→ Temporary Storage ──────────────────┘
```

| 组件 | 职责 |
|------|------|
| **Preprocessor** | 视频按 GOP 分片、生成 DAG、缓存分片到临时存储 |
| **DAG Scheduler** | 将 DAG 拆分为多阶段任务，放入 Task Queue |
| **Resource Manager** | Task Queue + Worker Queue + Running Queue + Task Scheduler，调度最优 worker 执行任务 |
| **Task Workers** | 执行具体任务（video encoding, audio encoding, thumbnail 等） |
| **Temporary Storage** | 存储分片视频和 metadata（metadata 用内存缓存，视频/音频用 Blob） |
| **Encoded Video** | 最终输出（如 funny_720p.mp4） |

---

### 主线二：视频流播放流程 (Video Streaming Flow)

```
Client ──→ CDN Edge Server（就近节点）──→ 流式传输视频数据
```

**关键概念 - Streaming Protocol：**
- MPEG-DASH（Dynamic Adaptive Streaming over HTTP）
- Apple HLS（HTTP Live Streaming）
- Microsoft Smooth Streaming
- Adobe HDS（HTTP Dynamic Streaming）

**核心特点**：客户端逐步加载数据（streaming），不需等待整个视频下载完成。不同协议支持不同编码和播放器。

---

## 关键设计考量 (Tradeoffs)

### 1. 速度优化：分块并行上传
- **问题**：整个视频作为单一文件上传效率低，失败需全部重传
- **解法**：客户端按 GOP（Group of Pictures）切分视频为小块，独立上传
- **好处**：支持断点续传（resumable upload），单块失败只需重传该块

### 2. 速度优化：就近上传中心
- **问题**：全球用户上传到单一数据中心延迟高
- **解法**：全球部署多个 Upload Center（利用 CDN 作为上传入口），用户就近上传

### 3. 速度优化：全链路并行（Message Queue 解耦）
- **问题**：优化前各模块串行依赖（download → encode → upload），效率低
- **解法**：模块间引入 Message Queue，实现松耦合
- **效果**：Download Module 完成后事件入队，Encoding Module 可并行消费多个任务，不必等待特定上游

### 4. 安全优化：Pre-signed Upload URL
- **问题**：需确保只有授权用户能上传视频到正确位置
- **流程**：Client → API Server 请求 pre-signed URL → Client 使用该 URL 直接上传到存储
- **类似概念**：AWS S3 Pre-signed URL / Azure Shared Access Signature

### 5. 安全优化：视频版权保护
| 方案 | 说明 |
|------|------|
| **DRM** | Apple FairPlay / Google Widevine / Microsoft PlayReady |
| **AES 加密** | 加密视频 + 授权策略，播放时解密 |
| **Visual Watermarking** | 视频叠加公司 logo 等标识信息 |

### 6. 成本优化：基于长尾分布的 CDN 策略
- YouTube 视频访问量符合 long-tail distribution
- **热门视频**：走 CDN 全球分发
- **长尾视频**：从自有高容量 Video Server 直接服务
- **区域性热门视频**：只分发到对应区域的 CDN 节点
- **冷门短视频**：按需编码（on-demand encoding），不预先生成所有分辨率
- **终极方案**：自建 CDN + 与 ISP 合作（如 Netflix Open Connect）

### 7. 错误处理

**错误分类：**
- **Recoverable error**：重试若干次，仍失败则返回错误码
- **Non-recoverable error**（如 malformed video）：停止任务，返回错误码

**各组件错误处理：**

| 组件 | 错误处理策略 |
|------|------------|
| Upload | 重试 |
| Video splitting | 旧客户端不支持分片则由服务端处理 |
| Transcoding | 重试 |
| Preprocessor | 重新生成 DAG |
| DAG Scheduler | 重新调度任务 |
| Resource Manager Queue | 使用 replica |
| Task Worker | 在新 worker 上重试 |
| API Server | 无状态，请求重定向到其他实例 |
| Metadata Cache | 数据多副本，访问其他节点，启动新 cache server 替换 |
| Metadata DB Master | 提升 slave 为新 master |
| Metadata DB Slave | 使用其他 slave 读取，启动新 DB 替换 |

---

## 面试扩展话题 (Wrap-up)

1. **API 层水平扩展**：API Servers 无状态，可直接水平扩展
2. **数据库扩展**：Replication + Sharding
3. **Live Streaming（直播）**：
   - 与点播共享上传、编码、流式传输的基础架构
   - **差异点**：
     - 延迟要求更高 → 可能需要不同的 streaming protocol
     - 并行度要求更低 → 小块数据已实时处理
     - 错误处理不同 → 不能接受耗时过长的恢复操作
4. **Video Takedowns（视频下架）**：
   - 违反版权、色情、违法内容需移除
   - 部分在上传时系统自动检测，部分通过用户举报发现

---

## 速写练习要点

盲画时重点记住这些组件和连接：

1. **高层三角**：Client ← CDN（视频流）/ Client → API Servers（其他请求）
2. **上传主线**：User → LB → API Servers → Metadata DB/Cache；User → Original Storage → Transcoding Servers → Transcoded Storage → CDN
3. **完成通知**：Transcoding → Completion Queue → Completion Handler → 更新 Metadata DB + Cache → API Server 通知 Client
4. **转码 pipeline**：Preprocessor → DAG Scheduler → Resource Manager → Task Workers → Encoded Video（+ Temporary Storage 连接 Preprocessor 和 Task Workers）
5. **DAG 分叉**：Original Video 拆为 Video / Audio / Metadata 三路，Video 路有 Inspection、Transcoding、Thumbnail、Watermark 四类 Task，最终 Assemble
6. **优化三板斧**：GOP 分块上传 + 全球 Upload Center + Message Queue 全链路并行
7. **安全两招**：Pre-signed URL 授权上传 + DRM/AES/Watermark 保护播放
8. **成本关键**：长尾分布 → 热门走 CDN，冷门走 Video Server

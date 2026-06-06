---
tags: [learning/SYSD, training/sketchnote]
created: 2026-03-29
---

# 架构速写符号表

盲画时使用的 15 个核心符号。目标：每个符号 3 秒内画出，一眼可辨识。

## 组件符号

| 符号 | 组件 | 画法 | 使用场景 |
|------|------|------|----------|
| `[📱💻]` | Client | 方框 + 小屏幕 | 用户入口 |
| `[□□□]` | Server Cluster | 三个叠放方框 | API Server、Web Server |
| `⬡` | Load Balancer | 六边形 | 流量分发层 |
| `◇` | API Gateway | 菱形 | 入口网关、Middleware |
| `⌇` | Database | 圆柱体 | SQL / NoSQL |
| `⚡□` | Cache / Redis | 闪电 + 方框 | 缓存层 |
| `✉✉✉` | Message Queue | 信封排队 | 异步解耦 |
| `☁` | CDN | 云朵 | 静态资源分发 |
| `⟳` | Worker / Job | 循环箭头 | 后台任务、消费者 |
| `🔍` | Search Engine | 放大镜 | 全文搜索 |
| `🪣` | Object Storage | 桶 | S3、Blob Storage |
| `🌐` | DNS | 地球 | 域名解析 |
| `▭ₖᵥ` | Key-Value Store | 方框 + kv 标记 | Redis、DynamoDB |
| `[🔔]` | Notification | 铃铛 | 推送服务 |
| `📊` | Monitoring | 图表 | Metrics、Logging |

## 连接符号

| 符号 | 含义 | 画法 |
|------|------|------|
| `→` | 同步请求 | 实线箭头 |
| `⇢` | 异步 / 可选路径 | 虚线箭头 |
| `↔` | 双向通信 | 双向实线箭头 |
| `⇠ red` | 错误 / 限流 / 降级 | 红色虚线箭头 |

## 颜色约定

| 颜色 | 含义 |
|------|------|
| 蓝色 | 正常数据流（主路径） |
| 红色 | 错误 / 限流 / 降级路径 |
| 绿色 | 成功标注 |
| 灰色 | 可选 / 未来扩展 |

## 分组框

| 画法 | 含义 |
|------|------|
| 实线框 | 逻辑分组（如 "Write Path"） |
| 虚线框 | 集群边界（如 "Server Cluster"） |
| 底色区块 | 数据中心 / 可用区 |

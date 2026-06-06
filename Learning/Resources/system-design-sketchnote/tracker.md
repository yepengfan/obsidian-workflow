---
tags: [learning/SYSD, training/sketchnote]
created: 2026-03-29
---

# System Design 架构速写练习

## 练习方法

### 三阶段

| Phase | 名称 | 做法 | 时间 |
|-------|------|------|------|
| P1 | 临摹 | 看着 `速写练习要点` 画 | 不限 |
| P2 | 盲画 | 合上笔记，从记忆画 | 10-15 min |
| P3 | 讲画 | 边讲边画，模拟面试 | 8-10 min |

### 单次练习流程

1. **预热** (2 min) — 浏览该章 `速写练习要点`（P1 可看，P2/P3 跳过）
2. **速写** (10-15 min) — 空白 Excalidraw，计时盲画
3. **对比** (5 min) — 打开 `images/` 原图比对
4. **红笔标注** (3 min) — 在速写上用红色标出遗漏/错误
5. **记录** (2 min) — 更新下方表格

### 自评标准

| Score | 含义 |
|-------|------|
| ⭐ | <30% 组件，结构混乱 |
| ⭐⭐ | 30-50% 组件，主线模糊 |
| ⭐⭐⭐ | 高层架构基本对，细节有遗漏（合格线） |
| ⭐⭐⭐⭐ | 组件完整，数据流正确，小遗漏 |
| ⭐⭐⭐⭐⭐ | 完整还原 + 能画出 trade-off |

---

## Tier 1 — 基础组件

建议先练。单一系统，组件少，适合建立符号肌肉记忆。

| Chapter | Phase | Best | Attempts | Last Practiced | Weak Points |
|---------|-------|------|----------|----------------|-------------|
| [[vol1/ch01-scale-from-zero/notes\|ch01 Scale From Zero]] | — | — | 0 | — | — |
| [[vol1/ch04-rate-limiter/notes\|ch04 Rate Limiter]] | — | — | 0 | — | — |
| [[vol1/ch05-consistent-hashing/notes\|ch05 Consistent Hashing]] | — | — | 0 | — | — |
| [[vol1/ch06-key-value-store/notes\|ch06 Key-Value Store]] | — | — | 0 | — | — |
| [[vol1/ch07-unique-id-generator/notes\|ch07 Unique ID Generator]] | — | — | 0 | — | — |

## Tier 2 — 经典应用

标准读写 + 缓存模式，组件数适中。

| Chapter | Phase | Best | Attempts | Last Practiced | Weak Points |
|---------|-------|------|----------|----------------|-------------|
| [[vol1/ch08-url-shortener/notes\|ch08 URL Shortener]] | — | — | 0 | — | — |
| [[vol1/ch10-notification-system/notes\|ch10 Notification System]] | — | — | 0 | — | — |
| [[vol1/ch11-news-feed/notes\|ch11 News Feed]] | — | — | 0 | — | — |
| [[vol1/ch13-search-autocomplete/notes\|ch13 Search Autocomplete]] | — | — | 0 | — | — |
| [[vol2/ch10-gaming-leaderboard/notes\|v2-ch10 Gaming Leaderboard]] | — | — | 0 | — | — |

## Tier 3 — 复杂系统

多子系统、pipeline 多，需要画出完整数据流。

| Chapter | Phase | Best | Attempts | Last Practiced | Weak Points |
|---------|-------|------|----------|----------------|-------------|
| [[vol1/ch09-web-crawler/notes\|ch09 Web Crawler]] | — | — | 0 | — | — |
| [[vol1/ch12-chat-system/notes\|ch12 Chat System]] | — | — | 0 | — | — |
| [[vol1/ch14-design-youtube/notes\|ch14 Design YouTube]] | — | — | 0 | — | — |
| [[vol1/ch15-google-drive/notes\|ch15 Google Drive]] | — | — | 0 | — | — |
| [[vol2/ch08-distributed-email/notes\|v2-ch08 Distributed Email]] | — | — | 0 | — | — |

## Tier 4 — 分布式核心

分布式/地理系统，需理解 partition、replication、consensus。

| Chapter | Phase | Best | Attempts | Last Practiced | Weak Points |
|---------|-------|------|----------|----------------|-------------|
| [[vol2/ch04-distributed-message-queue/notes\|v2-ch04 Message Queue]] | — | — | 0 | — | — |
| [[vol2/ch09-s3-object-storage/notes\|v2-ch09 S3 Object Storage]] | — | — | 0 | — | — |
| [[vol2/ch01-proximity-service/notes\|v2-ch01 Proximity Service]] | — | — | 0 | — | — |
| [[vol2/ch02-nearby-friends/notes\|v2-ch02 Nearby Friends]] | — | — | 0 | — | — |
| [[vol2/ch03-google-maps/notes\|v2-ch03 Google Maps]] | — | — | 0 | — | — |

## Tier 5 — 业务密集型

高一致性、金融级系统，trade-off 多。

| Chapter | Phase | Best | Attempts | Last Practiced | Weak Points |
|---------|-------|------|----------|----------------|-------------|
| [[vol2/ch05-metrics-monitoring/notes\|v2-ch05 Metrics Monitoring]] | — | — | 0 | — | — |
| [[vol2/ch06-ad-click-aggregation/notes\|v2-ch06 Ad Click Aggregation]] | — | — | 0 | — | — |
| [[vol2/ch07-hotel-reservation/notes\|v2-ch07 Hotel Reservation]] | — | — | 0 | — | — |
| [[vol2/ch11-payment-system/notes\|v2-ch11 Payment System]] | — | — | 0 | — | — |
| [[vol2/ch12-digital-wallet/notes\|v2-ch12 Digital Wallet]] | — | — | 0 | — | — |
| [[vol2/ch13-stock-exchange/notes\|v2-ch13 Stock Exchange]] | — | — | 0 | — | — |

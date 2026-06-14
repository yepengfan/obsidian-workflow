---
title: "7. Sharding"
chapter: 7
status: unread
tags:
  - flashcards/DesigningData-IntensiveApplications2ndEdition
---

# 7. Sharding

> **一句话：** Sharding Clearly, we must break away from the sequential and not limit the computers. We must state definitions and provide for priorities and descriptions of data. We must state relationships, not procedures. Grace Murray Hopper, Management and the Computer of the Future (1962) A distributed database typically distributes data across nodes in two ways: It stores a copy of the…

## 核心概念
<!-- 读完后用自己的话解释每个概念 -->

## 和已知事物的连接
<!-- 类比、对比、联想 -->

## 费曼测试
<!-- 合上书，用 3-5 句话解释这章给一个完全不懂的人听 -->

## 未解决的问题
<!-- 读完还不懂的地方，或想深入探索的方向 -->

## Flashcards
What is the difference between key-range partitioning and hash partitioning?::Key-range partitioning keeps sorted order (enabling efficient range scans) but risks hot spots; hash partitioning distributes load evenly but loses sort order.
Why are secondary indexes challenging in a partitioned database?::A secondary index may need to span all partitions (global index with cross-partition updates) or be local to each partition (requiring scatter-gather queries).
What is the goal of rebalancing and what makes it hard?::Rebalancing redistributes data when nodes join/leave to keep load even, but it must minimize data movement and avoid disrupting service during the transition.

---
*Status: `unread` → `reading` → `filled` → `feynman-tested` → `reviewed`*

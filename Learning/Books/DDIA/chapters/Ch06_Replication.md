---
title: "6. Replication"
chapter: 6
status: unread
tags:
  - flashcards/DesigningData-IntensiveApplications2ndEdition
---

# 6. Replication

> **一句话：** Replication The major difference between a thing that might go wrong and a thing that cannot possibly go wrong is that when a thing that cannot possibly go wrong goes wrong, it usually turns out to be impossible to get at or repair. Douglas Adams, Mostly Harmless (1992) Replication means keeping a copy of the same data on multiple machines…

## 核心概念
<!-- 读完后用自己的话解释每个概念 -->

## 和已知事物的连接
<!-- 类比、对比、联想 -->

## 费曼测试
<!-- 合上书，用 3-5 句话解释这章给一个完全不懂的人听 -->

## 未解决的问题
<!-- 读完还不懂的地方，或想深入探索的方向 -->

## Flashcards
What are the three main replication architectures and their key trade-offs?::Single-leader (simple but leader is bottleneck), multi-leader (better write availability but conflict resolution needed), leaderless (highest availability but requires quorums and conflict handling).
What is replication lag and what consistency problems does it cause?::Replication lag is the delay before a follower reflects a leader's write; it causes stale reads, violated causality, and the illusion of "going back in time."
What does a quorum read/write mean in leaderless replication?::With n replicas, writing to w nodes and reading from r nodes where w + r > n guarantees you read at least one up-to-date copy.

---
*Status: `unread` → `reading` → `filled` → `feynman-tested` → `reviewed`*

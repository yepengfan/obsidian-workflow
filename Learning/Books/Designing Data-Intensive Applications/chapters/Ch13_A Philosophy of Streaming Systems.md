---
title: "13. A Philosophy of Streaming Systems"
chapter: 13
status: unread
tags:
  - flashcards/DesigningData-IntensiveApplications2ndEdition
---

# 13. A Philosophy of Streaming Systems

> **一句话：** A Philosophy of Streaming Systems If a thing be ordained to another as to its end, its last end cannot consist in the preservation of its being. Hence a captain does not intend as a last end, the preservation of the ship entrusted to him, since a ship is ordained to something else as its end, viz. to navigation. (Often…

## 核心概念
<!-- 读完后用自己的话解释每个概念 -->

## 和已知事物的连接
<!-- 类比、对比、联想 -->

## 费曼测试
<!-- 合上书，用 3-5 句话解释这章给一个完全不懂的人听 -->

## 未解决的问题
<!-- 读完还不懂的地方，或想深入探索的方向 -->

## Flashcards
What does "unbundling the database" mean?::Instead of relying on a single monolithic database for storage, indexing, caching, and materialized views, you compose these functions from separate systems connected by streams of change events.
Why does the book argue that end-to-end correctness cannot be achieved by infrastructure alone?::Transport-level guarantees (e.g., exactly-once delivery) are not sufficient; the application must also handle deduplication, idempotency, and consistency checks at the business logic level.
How does the log-centric architecture unify batch and stream processing?::By treating the append-only log as the source of truth, batch jobs can reprocess the full log for historical views while stream processors consume the tail for real-time derived views.

---
*Status: `unread` → `reading` → `filled` → `feynman-tested` → `reviewed`*

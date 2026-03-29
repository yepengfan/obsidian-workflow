---
title: "8. Transactions"
chapter: 8
status: unread
tags:
  - flashcards/DesigningData-IntensiveApplications2ndEdition
---

# 8. Transactions

> **一句话：** Transactions Some authors have claimed that general two-phase commit is too expensive to support, because of the performance or availability problems that it brings. We believe it is better to have application programmers deal with performance problems due to overuse of transactions as bottlenecks arise, rather than always coding around the lack of transactions. James Corbett et al., “Spanner: Google’s…

## 核心概念
<!-- 读完后用自己的话解释每个概念 -->

## 和已知事物的连接
<!-- 类比、对比、联想 -->

## 费曼测试
<!-- 合上书，用 3-5 句话解释这章给一个完全不懂的人听 -->

## 未解决的问题
<!-- 读完还不懂的地方，或想深入探索的方向 -->

## Flashcards
What does each letter of ACID actually guarantee?::Atomicity (all-or-nothing commit), Consistency (application invariants preserved), Isolation (concurrent transactions don't interfere), Durability (committed data survives crashes).
What are the main isolation levels from weakest to strongest?::Read Committed (no dirty reads/writes) -> Snapshot Isolation (each transaction sees a consistent snapshot) -> Serializability (transactions appear to execute one at a time).
Why is Two-Phase Commit (2PC) problematic in distributed systems?::2PC blocks all participants if the coordinator crashes after prepare but before commit/abort, causing availability problems — it is a blocking atomic commit protocol.

---
*Status: `unread` → `reading` → `filled` → `feynman-tested` → `reviewed`*

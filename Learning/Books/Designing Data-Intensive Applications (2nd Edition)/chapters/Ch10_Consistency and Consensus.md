---
title: "10. Consistency and Consensus"
chapter: 10
status: unread
tags:
  - flashcards/DesigningData-IntensiveApplications2ndEdition
---

# 10. Consistency and Consensus

> **一句话：** Consistency and Consensus An ancient adage warns, “Never go to sea with two chronometers; take one or three.” Frederick P. Brooks Jr., The Mythical Man-Month: Essays on Software Engineering (1995) Lots of things can go wrong in distributed systems, as discussed in Chapter 9 . If we want a service to continue working correctly despite those things going wrong, we…

## 核心概念
<!-- 读完后用自己的话解释每个概念 -->

## 和已知事物的连接
<!-- 类比、对比、联想 -->

## 费曼测试
<!-- 合上书，用 3-5 句话解释这章给一个完全不懂的人听 -->

## 未解决的问题
<!-- 读完还不懂的地方，或想深入探索的方向 -->

## Flashcards
What is linearizability and why is it expensive?::Linearizability means the system behaves as if there is a single copy of the data with every operation taking effect atomically at some point between invocation and response. It is expensive because it requires coordination that reduces availability and increases latency.
How do Lamport timestamps differ from vector clocks?::Lamport timestamps provide a total order consistent with causality but cannot tell if two events are concurrent. Vector clocks capture the full causal partial order and can detect concurrency.
What problem do consensus algorithms (Raft, Paxos) solve?::They allow a group of nodes to agree on a single value (e.g., who is the leader) despite node crashes and network partitions, guaranteeing safety as long as a majority is reachable.

---
*Status: `unread` → `reading` → `filled` → `feynman-tested` → `reviewed`*

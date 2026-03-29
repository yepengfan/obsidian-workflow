---
title: "12. Stream Processing"
chapter: 12
status: unread
tags:
  - flashcards/DesigningData-IntensiveApplications2ndEdition
---

# 12. Stream Processing

> **一句话：** Stream Processing A complex system that works is invariably found to have evolved from a simple system that works. The inverse proposition also appears to be true: A complex system designed from scratch never works and cannot be made to work. John Gall, Systemantics (1975) In Chapter 11 we discussed batch processing—techniques that read a set of files as input…

## 核心概念
<!-- 读完后用自己的话解释每个概念 -->

## 和已知事物的连接
<!-- 类比、对比、联想 -->

## 费曼测试
<!-- 合上书，用 3-5 句话解释这章给一个完全不懂的人听 -->

## 未解决的问题
<!-- 读完还不懂的地方，或想深入探索的方向 -->

## Flashcards
What is Change Data Capture (CDC) and why is it powerful?::CDC captures row-level changes from a database's write-ahead log and publishes them as a stream of events, enabling derived systems to stay in sync without tight coupling to the source database.
How does stream processing handle the concept of time (event time vs. processing time)?::Event time is when the event actually occurred; processing time is when the system processes it. The gap between them causes windowing challenges — stragglers may arrive after a window closes.
What are the main approaches to achieving exactly-once semantics in stream processing?::Idempotent operations, transactional writes to output, and effectively-once via checkpointing and replay (e.g., Kafka's transactional producer + consumer offsets).

---
*Status: `unread` → `reading` → `filled` → `feynman-tested` → `reviewed`*

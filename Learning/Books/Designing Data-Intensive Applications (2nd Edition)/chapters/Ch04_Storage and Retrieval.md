---
title: "4. Storage and Retrieval"
chapter: 4
status: unread
tags:
  - flashcards/DesigningData-IntensiveApplications2ndEdition
---

# 4. Storage and Retrieval

> **一句话：** Storage and Retrieval One of the miseries of life is that everybody names things a little bit wrong. And so it makes everything a little harder to understand in the world than it would be if it were named differently. A computer does not primarily compute in the sense of doing arithmetic. […] They primarily are filing systems. Richard Feynman…

## 核心概念
<!-- 读完后用自己的话解释每个概念 -->

## 和已知事物的连接
<!-- 类比、对比、联想 -->

## 费曼测试
<!-- 合上书，用 3-5 句话解释这章给一个完全不懂的人听 -->

## 未解决的问题
<!-- 读完还不懂的地方，或想深入探索的方向 -->

## Flashcards
What is the fundamental trade-off between LSM-Trees and B-Trees?::LSM-Trees optimize for write throughput (sequential writes, compaction), while B-Trees optimize for read performance (in-place updates, predictable lookup).
Why is column-oriented storage advantageous for analytics?::Analytical queries typically scan a few columns across millions of rows; column storage reads only the needed columns and enables better compression.
What is a write-ahead log (WAL) and why is it important?::A WAL is an append-only file where every modification is written before being applied to the main data structure, ensuring durability and crash recovery.

---
*Status: `unread` → `reading` → `filled` → `feynman-tested` → `reviewed`*

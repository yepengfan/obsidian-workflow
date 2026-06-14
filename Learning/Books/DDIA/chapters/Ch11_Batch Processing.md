---
title: "11. Batch Processing"
chapter: 11
status: unread
tags:
  - flashcards/DesigningData-IntensiveApplications2ndEdition
---

# 11. Batch Processing

> **一句话：** Batch Processing A system cannot be successful if it is too strongly influenced by a single person. Once the initial design is complete and fairly robust, the real test begins as people with many different viewpoints undertake their own experiments. Donald Knuth, “The Errors of TeX” (1989) Much of this book so far has talked about requests and queries and…

## 核心概念
<!-- 读完后用自己的话解释每个概念 -->

## 和已知事物的连接
<!-- 类比、对比、联想 -->

## 费曼测试
<!-- 合上书，用 3-5 句话解释这章给一个完全不懂的人听 -->

## 未解决的问题
<!-- 读完还不懂的地方，或想深入探索的方向 -->

## Flashcards
How does MapReduce achieve fault tolerance?::By writing intermediate results to a distributed filesystem (like HDFS) between stages, so any failed task can be re-executed on another node without restarting the entire job.
Why did dataflow engines like Spark replace MapReduce for many workloads?::They model computation as a DAG of operators rather than rigid map-then-reduce stages, avoiding unnecessary materialization of intermediate results to disk and enabling pipelining.
What is the Unix philosophy connection to batch processing design?::Both favor composing simple, single-purpose programs via well-defined interfaces (stdin/stdout for Unix; immutable files for MapReduce) — enabling reuse, testability, and loose coupling.

---
*Status: `unread` → `reading` → `filled` → `feynman-tested` → `reviewed`*

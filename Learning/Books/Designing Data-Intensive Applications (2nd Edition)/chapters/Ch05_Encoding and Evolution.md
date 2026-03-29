---
title: "5. Encoding and Evolution"
chapter: 5
status: unread
tags:
  - flashcards/DesigningData-IntensiveApplications2ndEdition
---

# 5. Encoding and Evolution

> **一句话：** Encoding and Evolution Everything changes and nothing stands still. Heraclitus of Ephesus, as quoted by Plato in Cratylus (360 BCE) Applications inevitably change over time. Features are added or modified as new products are launched, user requirements become better understood, or business circumstances change. In Chapter 2 we introduced the idea of evolvability : we should aim to build systems…

## 核心概念
<!-- 读完后用自己的话解释每个概念 -->

## 和已知事物的连接
<!-- 类比、对比、联想 -->

## 费曼测试
<!-- 合上书，用 3-5 句话解释这章给一个完全不懂的人听 -->

## 未解决的问题
<!-- 读完还不懂的地方，或想深入探索的方向 -->

## Flashcards
What is the difference between backward compatibility and forward compatibility?::Backward compatibility: new code can read old data. Forward compatibility: old code can read new data (harder, requires ignoring unknown fields).
Why are binary encoding formats like Protobuf and Avro preferred over JSON for inter-service communication?::They are more compact, have well-defined schemas that enforce a contract, and support schema evolution with explicit compatibility rules.
What are the three main modes of dataflow between processes?::Via databases (one process writes, another reads later), via service calls (REST/RPC), and via asynchronous message passing (message brokers).

---
*Status: `unread` → `reading` → `filled` → `feynman-tested` → `reviewed`*

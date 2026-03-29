---
title: "1. Trade-Offs in Data Systems Architecture"
chapter: 1
status: unread
tags:
  - flashcards/DesigningData-IntensiveApplications2ndEdition
---

# 1. Trade-Offs in Data Systems Architecture

> **一句话：** Trade-Offs in Data Systems Architecture There are no solutions; there are only trade-offs. […] But you try to get the best trade-off you can get, and that’s all you can hope for. Thomas Sowell , interview with Fred Barnes (2005) Data is central to much application development today. With web and mobile apps, software as a service (SaaS), and cloud…

## 核心概念
<!-- 读完后用自己的话解释每个概念 -->

## 和已知事物的连接
<!-- 类比、对比、联想 -->

## 费曼测试
<!-- 合上书，用 3-5 句话解释这章给一个完全不懂的人听 -->

## 未解决的问题
<!-- 读完还不懂的地方，或想深入探索的方向 -->

## Flashcards
What are the three main concerns for most software systems according to DDIA?::Reliability (tolerating faults), Scalability (handling growth), and Maintainability (enabling change over time).
Why does DDIA argue there are "no solutions, only trade-offs" in data system design?::Every architectural choice (e.g., latency vs. throughput, consistency vs. availability) sacrifices one property to gain another; the goal is finding the best trade-off for your use case.
What distinguishes a data-intensive application from a compute-intensive one?::Data-intensive apps are bottlenecked by the amount, complexity, and rate of change of data, rather than by raw CPU power.

---
*Status: `unread` → `reading` → `filled` → `feynman-tested` → `reviewed`*

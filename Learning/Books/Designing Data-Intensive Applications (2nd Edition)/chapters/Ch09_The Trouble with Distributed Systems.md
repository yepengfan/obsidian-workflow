---
title: "9. The Trouble with Distributed Systems"
chapter: 9
status: unread
tags:
  - flashcards/DesigningData-IntensiveApplications2ndEdition
---

# 9. The Trouble with Distributed Systems

> **一句话：** The Trouble with Distributed Systems They’re funny things, Accidents. You never have them till you’re having them. A.A. Milne, The House at Pooh Corner (1928) As discussed in “Reliability and Fault Tolerance” , making a system reliable means ensuring that the system as a whole continues working, even when things go wrong (i.e., when there is a fault). However, anticipating…

## 核心概念
<!-- 读完后用自己的话解释每个概念 -->

## 和已知事物的连接
<!-- 类比、对比、联想 -->

## 费曼测试
<!-- 合上书，用 3-5 句话解释这章给一个完全不懂的人听 -->

## 未解决的问题
<!-- 读完还不懂的地方，或想深入探索的方向 -->

## Flashcards
Why can't you reliably detect whether a remote node has crashed?::Network delays are unbounded — you cannot distinguish between a crashed node, a slow node, and a lost response. Timeouts are the only practical mechanism, and they are always a guess.
Why are wall-clock timestamps unreliable for ordering events in a distributed system?::Clocks drift between machines (even with NTP), can jump forward or backward, and provide no causal ordering guarantees across nodes.
What is a Byzantine fault and when do you need to tolerate it?::A Byzantine fault is when a node sends incorrect or contradictory information. Tolerance is needed in adversarial environments (e.g., blockchain) but is too expensive for most datacenter systems.

---
*Status: `unread` → `reading` → `filled` → `feynman-tested` → `reviewed`*

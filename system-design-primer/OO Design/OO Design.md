---
tags: [flashcards/OODesign]
---

# OO Design Flashcards

Source: [system-design-primer](https://github.com/donnemartin/system-design-primer)

## Flashcards

Design a deck of cards
?
Classes: Suit (enum: HEART, DIAMOND, CLUB, SPADE), Card (suit, value), Deck (cards list, shuffle, deal_card, remaining), Hand (cards list, add/score). BlackJackCard extends Card with ace=1/11 logic, face=10. BlackJackHand scores by trying ace as 11 first, downgrading to 1 if bust.
类：Suit（枚举：红心、方块、梅花、黑桃）、Card（花色、值）、Deck（牌组列表、洗牌、发牌、剩余）、Hand（手牌列表、添加/计分）。BlackJackCard 继承 Card，A=1/11 逻辑，花牌=10。BlackJackHand 先试 A 为 11，爆牌则降为 1。

Design a call center
?
Classes: Employee (abstract, with call_handler), Operator/Supervisor/Director extend Employee. CallCenter holds queues per level. Routing: call → first available Operator → if none, escalate to Supervisor → then Director. Call tracks rank and state. Dispatch_call finds first free employee at lowest rank, escalates up if needed.
类：Employee（抽象，含 call_handler）、Operator/Supervisor/Director 继承 Employee。CallCenter 按级别持有队列。路由：来电 → 第一个空闲 Operator → 没有则升级到 Supervisor → 再到 Director。Call 追踪等级和状态。Dispatch_call 找最低级别空闲员工，需要时向上升级。

Design a hash map
?
Array of linked lists (chaining). hash(key) % array_size → bucket index. Set: traverse bucket, update if key exists, else append. Get: traverse bucket, return value if key found. Remove: traverse and delete node. Handle collisions via chaining. Load factor triggers resize (double array, rehash all keys).
链表数组（链地址法）。hash(key) % 数组大小 → 桶索引。Set：遍历桶，键存在则更新，否则追加。Get：遍历桶，找到键返回值。Remove：遍历并删除节点。通过链地址法处理冲突。负载因子触发扩容（数组翻倍，所有键重新哈希）。

Design an LRU cache
?
Hash map (O(1) lookup) + doubly linked list (O(1) insert/remove). Get: if in map, move node to front, return value. Set: if exists, update and move to front; if new and full, evict tail node (LRU), remove from map; insert new node at front. Both operations O(1).
哈希表（O(1) 查找）+ 双向链表（O(1) 插入/删除）。Get：在 map 中则移到头部返回值。Set：存在则更新移到头部；新键且已满则淘汰尾节点（LRU），从 map 删除；在头部插入新节点。两个操作均 O(1)。

Design an online chat
?
Classes: User (id, name, status, chats), Chat (abstract), PrivateChat extends Chat (2 users), GroupChat extends Chat (users set, add/remove), Message (content, timestamp, sender). ChatServer: user_id→User map, create_chat, send_message. Status tracking: online/offline/away. Push notifications via WebSocket or long polling.
类：User（id、名称、状态、聊天列表）、Chat（抽象）、PrivateChat 继承 Chat（2 用户）、GroupChat 继承 Chat（用户集合、添加/删除）、Message（内容、时间戳、发送者）。ChatServer：user_id→User 映射、创建聊天、发消息。状态追踪：在线/离线/离开。通过 WebSocket 或长轮询推送通知。

Design a parking lot
?
Classes: VehicleSize (enum: MOTORCYCLE, COMPACT, LARGE), Vehicle (abstract, spots_needed, size, can_fit_in_spot), Motorcycle/Car/Bus extend Vehicle. ParkingSpot (size, vehicle, available, can_fit). ParkingLot (levels list), Level (spots array, park_vehicle scans for contiguous available spots matching size). Bus needs 5 large spots, Car fits compact or large, Motorcycle fits any.
类：VehicleSize（枚举：摩托车、紧凑、大型）、Vehicle（抽象，需要车位数、尺寸、能否停入）、Motorcycle/Car/Bus 继承 Vehicle。ParkingSpot（尺寸、车辆、可用、能否容纳）。ParkingLot（层列表）、Level（车位数组，park_vehicle 扫描匹配尺寸的连续空位）。巴士需 5 个大车位，轿车可停紧凑或大型，摩托车可停任何。

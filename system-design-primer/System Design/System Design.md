---
tags: [flashcards/SystemDesign]
---

# System Design Flashcards

Source: [system-design-primer](https://github.com/donnemartin/system-design-primer)

## Flashcards

Performance vs scalability
?
Performance problem: slow for a single user. Scalability problem: fast for one user but slow under heavy load. A scalable service increases performance proportionally to resources added.
性能问题：单用户也慢。可扩展性问题：单用户快，高负载下慢。可扩展的服务在增加资源时性能成比例提升。

Latency vs throughput
?
Latency: time to perform an action. Throughput: number of actions per unit time. Aim for maximal throughput with acceptable latency.
延迟：执行操作所需时间。吞吐量：单位时间内的操作数。目标：在可接受延迟下最大化吞吐量。

Consistency patterns
?
Weak: reads may not see recent writes (VoIP, games). Eventual: reads eventually see writes, typically in ms (DNS, email). Strong: reads always see latest write (RDBMS, file systems).
弱一致性：读取可能看不到最近的写入（VoIP、游戏）。最终一致性：读取最终会看到写入，通常毫秒级（DNS、邮件）。强一致性：读取总能看到最新写入（关系数据库、文件系统）。

Availability patterns
?
Fail-over: active-passive (heartbeat, master IP takeover) or active-active (both handle traffic, DNS-based). Replication: master-slave or master-master. Availability in sequence: Availability(Total) = Availability(Foo) × Availability(Bar). In parallel: Availability(Total) = 1 - (1 - Availability(Foo)) × (1 - Availability(Bar)).
故障转移：主备（心跳检测，主节点 IP 接管）或双活（都处理流量，DNS 分配）。复制：主从或主主。串联可用性 = A(Foo) × A(Bar)。并联可用性 = 1 - (1-A(Foo)) × (1-A(Bar))。

Availability vs consistency
?
CP: waiting for response from partitioned node may return timeout error. Good when business requires atomic reads/writes. AP: responses return the most recent available data, which might not be the latest. Good when the system needs to continue working despite errors, or when eventual consistency is acceptable.
CP：等待分区节点响应可能超时。适合业务要求原子读写。AP：响应返回最近可用的数据（可能不是最新的）。适合系统需要在错误时继续工作，或可接受最终一致性。

Domain name system
?
DNS translates domains to IPs. NS record (name server), MX record (mail server), A record (name→IP), CNAME (name→name alias). Traffic routing: weighted round robin, latency-based, geolocation-based. Disadvantages: slight delay, complex management, DDoS vulnerability.
DNS 将域名转为 IP。NS 记录（名称服务器）、MX 记录（邮件）、A 记录（名称→IP）、CNAME（别名）。流量路由：加权轮询、基于延迟、基于地理位置。缺点：轻微延迟、管理复杂、易受 DDoS 攻击。

Content delivery network
?
CDN: globally distributed proxy servers serving content from nearby locations. Push CDN: content uploaded on change, good for low-traffic sites. Pull CDN: content fetched on first request and cached with TTL, good for heavy-traffic sites. Disadvantages: CDN costs, stale content if TTL not set properly, URL changes needed to point to CDN.
CDN：全球分布的代理服务器，从就近位置提供内容。Push CDN：内容变更时主动上传，适合低流量站点。Pull CDN：首次请求时拉取并缓存（TTL），适合高流量站点。缺点：成本高、TTL 不当导致内容过期、需要修改 URL 指向 CDN。

Load balancer
?
Distributes requests across servers. Active-passive: heartbeat between active/passive, passive takes over on failure. Active-active: both handle traffic. L4 (transport layer): routes based on IP/port. L7 (application layer): routes based on header, content, URL. Can route via random, round robin, least loaded, session/IP-based. Disadvantages: bottleneck if under-resourced, single point of failure, added complexity.
将请求分配到多台服务器。主备：心跳检测，主挂备接管。双活：两台都处理流量。L4（传输层）：基于 IP/端口路由。L7（应用层）：基于头部/内容/URL 路由。策略：随机、轮询、最小负载、会话/IP 亲和。缺点：资源不足时成瓶颈、单点故障、增加复杂性。

Reverse proxy (web server)
?
A web server that centralizes internal services and provides a unified interface. Benefits: security (hide backend IPs/servers), scalability (add/remove backends freely), SSL termination, compression, caching, static content serving. Disadvantages: single point of failure if not HA, added complexity.
集中管理内部服务并提供统一接口的 Web 服务器。优点：安全性（隐藏后端 IP）、可扩展（自由增减后端）、SSL 终止、压缩、缓存、静态内容服务。缺点：若不做高可用则成为单点故障、增加复杂性。

Application layer
?
Separating web layer from application layer (workers) enables independent scaling. Workers can use async workflows via task queues. Service discovery (Consul, etcd, Zookeeper) helps services find each other. Disadvantages: added complexity from loose coupling.
将 Web 层与应用层（Worker）分离可独立扩展。Worker 通过任务队列实现异步工作流。服务发现（Consul、etcd、Zookeeper）帮助服务互相定位。缺点：松耦合增加复杂性。

Database
?
RDBMS with ACID properties. Scaling techniques: master-slave replication (read replicas), master-master replication (both read/write), federation (split by function), sharding (split data across DBs), denormalization (redundant data to avoid joins), SQL tuning (benchmarks, indexes, avoid expensive joins). Each has trade-offs between complexity, consistency, and performance.
关系数据库遵循 ACID。扩展技术：主从复制（读副本）、主主复制（双写）、联邦（按功能拆分）、分片（跨库分数据）、反规范化（冗余数据避免 JOIN）、SQL 调优（基准测试、索引、避免昂贵 JOIN）。每种都在复杂性、一致性和性能间权衡。

Federation
?
Splits databases by function (e.g., users DB, products DB, forums DB). Less read/write traffic per DB, less replication lag, smaller DBs = more data fits in memory = more cache hits. No single central master bottleneck. Disadvantages: not effective if schema requires huge functions/tables, app logic to determine which DB, joining data across DBs is complex, more hardware and complexity.
按功能拆分数据库（如用户库、产品库、论坛库）。每个库读写流量更少、复制延迟更小、更多数据放入内存 = 更多缓存命中。无单一中心主节点瓶颈。缺点：模式需要巨大功能/表时无效、应用层需判断用哪个库、跨库 JOIN 复杂、更多硬件和复杂性。

Sharding
?
Distributes data across different databases so each handles a subset. Less traffic, less replication, more cache hits, smaller indexes, faster queries. If one shard is down, others still operate (with some form of replication). Disadvantages: app logic to route to correct shard, unbalanced data can overload a shard (hot spots), joining across shards is complex, more hardware and complexity.
将数据分布到不同数据库，每个处理一个子集。流量更少、复制更少、缓存命中更多、索引更小、查询更快。一个分片下线其他继续运行（需复制）。缺点：应用逻辑需路由到正确分片、数据不均可致热点、跨分片 JOIN 复杂、更多硬件和复杂性。

Denormalization
?
Improves read performance at the expense of write performance. Redundant copies of data written across multiple tables to avoid expensive joins. In most systems, reads outnumber writes 100:1 or 1000:1. Useful once data is distributed (federation/sharding) since cross-DB joins are very complex. Disadvantages: data duplication, constraints to keep redundant copies in sync, heavy write-load DB may perform worse.
以牺牲写性能换取读性能。跨多个表写入冗余数据副本以避免昂贵 JOIN。多数系统读写比 100:1 或 1000:1。数据分布后（联邦/分片）特别有用，因为跨库 JOIN 非常复杂。缺点：数据重复、需约束保持冗余副本同步、写负载大的数据库可能更差。

SQL tuning
?
Important to benchmark and profile. Benchmark: simulate high-load with tools like ab. Profile: enable slow query log. Key techniques: use indexes (B-tree, faster lookups but slower writes/more memory), avoid expensive joins, partition tables, tune query cache. Use CHAR for fixed-length fields, avoid SELECT * (prefer specific columns), use NOT NULL where possible.
基准测试和分析很重要。基准测试：用 ab 等工具模拟高负载。分析：启用慢查询日志。关键技术：使用索引（B-tree，查找快但写入慢/占内存）、避免昂贵 JOIN、表分区、调优查询缓存。定长字段用 CHAR、避免 SELECT *（选特定列）、尽可能用 NOT NULL。

NoSQL
?
Types: Key-value (Redis, Memcached — simple lookups), Document (MongoDB — documents as values), Wide column (Cassandra, HBase — nested map by column family), Graph (Neo4j — complex relationships). Most are eventually consistent, favoring AP over CP. BASE model: Basically Available, Soft state, Eventual consistency.
类型：键值存储（Redis、Memcached — 简单查找）、文档（MongoDB — 文档作值）、宽列（Cassandra、HBase — 按列族嵌套映射）、图（Neo4j — 复杂关系）。多数最终一致，偏向 AP 而非 CP。BASE 模型：基本可用、软状态、最终一致性。

Key-value store
?
Abstraction: hash table. O(1) reads and writes, backed by memory or SSD. Often used for simple data models or rapidly-changing data (in-memory cache). Can maintain keys in lexicographic order for efficient key range retrieval. High performance for simple lookups. Examples: Redis, Memcached.
抽象：哈希表。O(1) 读写，基于内存或 SSD。常用于简单数据模型或快速变化的数据（内存缓存）。可按字典序维护键以高效范围检索。简单查找性能高。例：Redis、Memcached。

Document store
?
Abstraction: key-value store with documents (XML, JSON, binary) as values. Documents organized by collections, tags, metadata, or directories. Documents can be queried by content. Examples: MongoDB, CouchDB, Elasticsearch. Suitable when document model matches your use case. Some (like MongoDB and CouchDB) provide SQL-like query language.
抽象：以文档（XML、JSON、二进制）为值的键值存储。文档按集合、标签、元数据或目录组织。可按内容查询文档。例：MongoDB、CouchDB、Elasticsearch。文档模型匹配用例时适用。部分（如 MongoDB、CouchDB）提供类 SQL 查询语言。

Wide column store
?
Abstraction: nested map — ColumnFamily<RowKey, Columns<ColKey, Value, Timestamp>>. Basic unit: column (name/value pair). Columns grouped into column families. Super columns group column families. Access by row key, and each row can have different columns. Operations: by key, key range, or scanning. High availability, high scalability. Examples: Cassandra, HBase.
抽象：嵌套映射 — ColumnFamily<RowKey, Columns<ColKey, Value, Timestamp>>。基本单位：列（名/值对）。列分组为列族。超级列分组列族。按行键访问，每行可有不同列。操作：按键、键范围或扫描。高可用、高可扩展。例：Cassandra、HBase。

Graph database
?
Abstraction: graph (nodes + edges with properties). Optimized for complex relationships with many foreign keys or many-to-many relationships. High performance for traversing relationships. Examples: Neo4j, FlockDB. Many graphs can only be accessed via REST APIs.
抽象：图（带属性的节点 + 边）。优化了复杂关系、大量外键或多对多关系。关系遍历性能高。例：Neo4j、FlockDB。许多图数据库只能通过 REST API 访问。

SQL or NoSQL
?
Choose SQL when: structured data, strict schema, complex joins, transactions, mature tooling. Choose NoSQL when: semi-structured data, dynamic schema, very large datasets, high throughput, need to serialize/deserialize (JSON, XML). Suitable for rapid prototyping, key-value or document patterns, massive scale.
选 SQL：结构化数据、严格模式、复杂 JOIN、事务、成熟工具。选 NoSQL：半结构化数据、动态模式、超大数据量、高吞吐、需要序列化/反序列化。适合快速原型、键值/文档模式、大规模场景。

Cache
?
Caching improves page load times and reduces server/DB load. Levels: client (browser), CDN, web server, database (default query caching), application (in-memory like Redis/Memcached). Cache what: DB queries (hash query as key) or objects (assembled data objects). Eviction: LRU is most common.
缓存提升页面加载速度，降低服务器/数据库负载。层级：客户端（浏览器）、CDN、Web 服务器、数据库（默认查询缓存）、应用层（内存如 Redis/Memcached）。缓存对象：DB 查询（查询哈希为 key）或组装好的数据对象。淘汰策略：LRU 最常用。

Cache locations
?
Client caching (OS/browser), CDN caching, web server caching (reverse proxy like Varnish), database caching (default config, e.g. MySQL query cache), application caching (in-memory stores like Redis/Memcached, key-value with O(1) reads).
客户端缓存（OS/浏览器）、CDN 缓存、Web 服务器缓存（反向代理如 Varnish）、数据库缓存（默认配置，如 MySQL 查询缓存）、应用层缓存（内存存储如 Redis/Memcached，键值 O(1) 读取）。

Database caching, what to cache
?
Two categories: DB queries (hash query as key, but expiration is hard — one cell change invalidates all cached queries referencing that cell) and objects (assembled data: user sessions, rendered pages, activity streams, user graph data). Avoid file-based caching (makes cloning/auto-scaling harder). Generally, caching objects is recommended.
两类：DB 查询（查询哈希为 key，但过期难处理 — 一个单元格变化会使所有引用它的缓存查询失效）和对象（组装好的数据：用户会话、渲染页面、活动流、用户图数据）。避免基于文件的缓存（阻碍克隆/自动扩展）。通常推荐缓存对象。

Cache-aside
?
App first checks cache. On miss: reads from DB, adds to cache, returns. On hit: returns from cache directly. Disadvantages: each cache miss requires 3 trips, data can become stale if updated in DB (mitigated by TTL or write-through), cache nodes restart = empty cache (mitigated by warm-up).
应用先查缓存。未命中：从 DB 读取、写入缓存、返回。命中：直接从缓存返回。缺点：每次未命中需 3 次访问、DB 更新后数据可能过期（通过 TTL 或写穿透缓解）、缓存节点重启 = 空缓存（通过预热缓解）。

Write-through
?
App uses cache as the main data store. Cache synchronously writes to DB. Disadvantages: slow due to synchronous write, most written data may never be read (mitigated by TTL), new nodes not populated until DB read (mitigated by cache-aside). Advantage: data in cache is never stale.
应用以缓存为主数据存储。缓存同步写入 DB。缺点：同步写入慢、多数写入数据可能从未被读取（通过 TTL 缓解）、新节点直到 DB 读取才填充（通过旁路缓存缓解）。优点：缓存中数据永不过期。

Write-behind (write-back)
?
App writes to cache. Cache asynchronously writes to DB (in batches). Disadvantages: potential data loss if cache goes down before flushing to DB, more complex to implement than cache-aside or write-through.
应用写入缓存。缓存异步批量写入 DB。缺点：缓存在刷新到 DB 前宕机可能丢数据、实现比旁路缓存或写穿透更复杂。

Refresh-ahead
?
Cache automatically refreshes recently accessed entries before their expiration. Can reduce latency vs read-through if it can accurately predict which items will be needed. Disadvantages: prediction must be accurate or it adds unnecessary load.
缓存在过期前自动刷新最近访问的条目。如果能准确预测需要的项目，可降低延迟。缺点：预测必须准确，否则增加不必要的负载。

Asynchronism
?
Message queues: producer enqueues, consumer dequeues and processes (Redis, RabbitMQ, Amazon SQS). Task queues: schedule work, support task graph dependencies (Celery). Back pressure: limit queue size to maintain high throughput, return 503 when full. Disadvantages: use cases with simple/real-time needs may not benefit.
消息队列：生产者入队，消费者出队处理（Redis、RabbitMQ、SQS）。任务队列：调度工作，支持任务依赖图（Celery）。反压：限制队列大小保持高吞吐，满时返回 503。缺点：简单或实时场景可能不适用。

Communication
?
HTTP: request/response, self-contained. TCP: connection-oriented, reliable byte stream (low-level). UDP: connectionless, unreliable, less latency (VoIP, video, gaming). RPC: client calls remote procedure as if local (Protobuf, Thrift, Avro). REST: resource-centric, stateless, standard HTTP verbs, JSON/XML. RPC is action-focused; REST is resource-focused.
HTTP：请求/响应，自包含。TCP：面向连接，可靠字节流。UDP：无连接，不可靠，低延迟（VoIP、视频、游戏）。RPC：客户端像调用本地方法一样调用远程过程（Protobuf、Thrift、Avro）。REST：以资源为中心、无状态、标准 HTTP 动词、JSON/XML。RPC 面向操作；REST 面向资源。

Hypertext transfer protocol (HTTP)
?
HTTP is a request/response protocol for client-server communication. It is self-contained: each request has all info needed. Verbs: GET (read), POST (create), PUT (update/create), PATCH (partial update), DELETE (delete). HTTP is an application layer protocol relying on lower-level protocols like TCP and UDP.
HTTP 是客户端-服务器通信的请求/响应协议。自包含：每个请求包含所有所需信息。动词：GET（读取）、POST（创建）、PUT（更新/创建）、PATCH（部分更新）、DELETE（删除）。HTTP 是应用层协议，依赖 TCP 和 UDP 等底层协议。

Transmission control protocol (TCP)
?
Connection-oriented protocol over IP network. Connection via 3-way handshake (SYN → SYN-ACK → ACK). Guarantees: ordered delivery, retransmission of lost packets, error detection via checksum, flow control, congestion control. High overhead. Use for: apps needing high reliability (web, database, SSH, SMTP).
基于 IP 网络的面向连接协议。通过三次握手建立连接（SYN → SYN-ACK → ACK）。保证：有序传递、丢包重传、校验和错误检测、流量控制、拥塞控制。开销大。适用于需要高可靠性的应用（Web、数据库、SSH、SMTP）。

User datagram protocol (UDP)
?
Connectionless, unreliable. Datagrams may arrive out of order or not at all. No handshake, no congestion control. Lower latency and overhead than TCP. Use for: VoIP, video chat, streaming, real-time multiplayer games. Can add reliability on top of UDP at the application level.
无连接、不可靠。数据报可能乱序到达或丢失。无握手、无拥塞控制。延迟和开销比 TCP 低。适用于：VoIP、视频通话、流媒体、实时多人游戏。可在应用层在 UDP 之上添加可靠性。

Remote procedure call (RPC)
?
Client calls a remote procedure as if it were local. The RPC framework handles serialization (Protobuf, Thrift, Avro, MessagePack), transport, and deserialization. Disadvantages: tightly couples client to service implementation, new API needed for each operation, hard to debug, may not be suitable for public APIs. RPC is action-oriented; REST is resource-oriented.
客户端像调用本地过程一样调用远程过程。RPC 框架处理序列化（Protobuf、Thrift、Avro、MessagePack）、传输和反序列化。缺点：客户端与服务实现紧耦合、每个操作需新 API、难调试、可能不适合公开 API。RPC 面向操作；REST 面向资源。

Representational state transfer (REST)
?
Client-server, stateless, resource-focused architecture. Uses standard HTTP verbs (GET, POST, PUT, DELETE, PATCH). Resources identified by URIs. Being stateless enables horizontal scaling. Disadvantages: resource-oriented design may not fit all use cases, payloads can be bloated (vs binary formats like Protobuf), nested hierarchy in URIs can be complex.
客户端-服务器、无状态、以资源为中心的架构。使用标准 HTTP 动词（GET、POST、PUT、DELETE、PATCH）。资源由 URI 标识。无状态性支持水平扩展。缺点：面向资源的设计不一定适合所有场景、载荷可能臃肿（相比 Protobuf 等二进制格式）、URI 嵌套层次可能复杂。

Security
?
Encrypt in transit (TLS) and at rest. Sanitize all user input to prevent XSS and SQL injection. Use parameterized queries. Apply least privilege principle. Defense in depth: multiple layers of security.
传输中加密（TLS）和静态加密。清理所有用户输入防止 XSS 和 SQL 注入。使用参数化查询。最小权限原则。纵深防御：多层安全。

Powers of two table
?
Key values: 2^10 = 1 KB, 2^20 = 1 MB, 2^30 = 1 GB, 2^40 = 1 TB, 2^50 = 1 PB. Useful for quick back-of-the-envelope calculations in system design.
关键值：2^10 = 1 KB, 2^20 = 1 MB, 2^30 = 1 GB, 2^40 = 1 TB, 2^50 = 1 PB。用于系统设计中的快速估算。

Latency numbers every programmer should know
?
L1 cache ~0.5ns, L2 cache ~7ns, mutex lock ~100ns, main memory ~100ns, SSD random read ~150μs, HDD seek ~10ms, round trip within same datacenter ~0.5ms, CA→NL round trip ~150ms. Key insight: memory is fast, disk is slow, network cross-continent is very slow.
L1 缓存 ~0.5ns、L2 缓存 ~7ns、互斥锁 ~100ns、主存 ~100ns、SSD 随机读 ~150μs、HDD 寻址 ~10ms、同数据中心往返 ~0.5ms、跨大洲往返 ~150ms。核心：内存快、磁盘慢、跨洲网络很慢。

MD5
?
Widely used hashing function producing a 128-bit hash value. Uniformly distributed. Used for checksums and non-security hash needs (not recommended for cryptographic security).
广泛使用的哈希函数，生成 128 位哈希值。均匀分布。用于校验和及非安全哈希需求（不推荐用于密码学安全）。

Base 62
?
Encodes to [a-zA-Z0-9], works well for URLs without needing to escape special characters. Deterministic: one hash result per original input, no randomness. Base 64 has issues for URLs due to + and / characters.
编码为 [a-zA-Z0-9]，适合 URL 无需转义特殊字符。确定性：每个原始输入一个哈希结果，无随机性。Base 64 因 + 和 / 字符在 URL 中有问题。

What is HATEOAS?
?
Hypertext As The Engine Of Application State. REST responses include hyperlinks to discover available actions dynamically. Clients navigate the API via links rather than hardcoding endpoints. Example: GET /account/12345 returns links for deposits, withdrawals, transfers, and close.
超文本作为应用状态引擎。REST 响应包含超链接以动态发现可用操作。客户端通过链接导航 API 而非硬编码端点。例：GET /account/12345 返回存款、取款、转账和关闭的链接。

RPC and REST calls comparison
?
RPC is action-oriented (POST /signup, POST /resign), REST is resource-oriented (POST /persons, DELETE /persons/1234). REST uses standard HTTP verbs on resources; RPC exposes operations as endpoints. Example: reading a person's items — RPC: GET /readUsersItemsList?personid=1234, REST: GET /persons/1234/items.
RPC 面向操作（POST /signup、POST /resign），REST 面向资源（POST /persons、DELETE /persons/1234）。REST 对资源使用标准 HTTP 动词；RPC 将操作暴露为端点。例：读取用户物品列表 — RPC: GET /readUsersItemsList?personid=1234，REST: GET /persons/1234/items。

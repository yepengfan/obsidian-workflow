---
tags: [flashcards/SystemDesignExercises]
---

# System Design Exercises Flashcards

Source: [system-design-primer](https://github.com/donnemartin/system-design-primer)

## Flashcards

Design Mint.com
?
Personal finance app. Key components: Web Server → Accounts API + Transaction Extraction Service (async via queue) → Category Service → Budget Service → Notification Service. SQL for users/accounts/transactions. MapReduce or Spark for monthly spending aggregation. Cache hot categories in Redis.
个人财务应用。核心组件：Web 服务器 → 账户 API + 交易提取服务（通过队列异步）→ 分类服务 → 预算服务 → 通知服务。SQL 存储用户/账户/交易。MapReduce 或 Spark 做月度消费聚合。Redis 缓存热门分类。

Design Pastebin.com (or Bit.ly)
?
Short URL / paste service. Generate unique short key (MD5 hash → Base62 encode → take first N chars). Store mapping in SQL or NoSQL. Read-heavy: use CDN + cache (Redis/Memcached). Analytics service tracks clicks asynchronously via queue. Scale: shard by hash key, replicate reads.
短链接/粘贴服务。生成唯一短 key（MD5 哈希 → Base62 编码 → 取前 N 位）。SQL 或 NoSQL 存储映射。读多写少：用 CDN + 缓存（Redis/Memcached）。分析服务通过队列异步追踪点击。扩展：按哈希 key 分片，读复制。

Design Amazon's sales rank by category feature
?
Track best sellers per category. Pipeline: Sales API → sales data in SQL → async MapReduce/Spark job aggregates sales counts per category (hourly/daily) → sorted rank stored in cache/DB. Separate processing for past hour, day, week, month. Use queue for async processing, cache for serving hot rankings.
按品类追踪畅销排名。管道：销售 API → SQL 销售数据 → 异步 MapReduce/Spark 按品类聚合销量（小时/天）→ 排序后的排名存缓存/DB。分别处理过去一小时、天、周、月。队列做异步处理，缓存服务热门排名。

Design a web crawler
?
Components: URL Frontier (priority queue of URLs to crawl), Fetcher (HTTP download, respect robots.txt), Parser (extract links + content), Duplicate detector (Bloom filter or hash set for seen URLs), Storage (object store for pages, DB for metadata). Politeness: per-domain rate limiting. Scale: distribute frontier across workers, partition by domain hash.
组件：URL 边界（待爬取优先队列）、抓取器（HTTP 下载，遵守 robots.txt）、解析器（提取链接+内容）、去重器（布隆过滤器或哈希集检测已访问 URL）、存储（对象存储存页面，DB 存元数据）。礼貌策略：按域名限速。扩展：跨 Worker 分布边界，按域名哈希分区。

Design the data structures for a social network
?
Graph structure: users as nodes, friendships as edges. BFS for shortest path between users. For large scale: shard users across servers, use lookup service to find which server holds a user. Cache hot user data in Redis. Use queue for async friend suggestion computation. Trade-off: graph DB (Neo4j) for complex queries vs adjacency list in RDBMS for simpler cases.
图结构：用户为节点，好友关系为边。BFS 求用户间最短路径。大规模：跨服务器分片用户，用查找服务定位用户所在服务器。Redis 缓存热门用户数据。队列做异步好友推荐计算。权衡：图数据库（Neo4j）处理复杂查询 vs 关系数据库邻接表处理简单场景。

Design the Twitter timeline and search
?
Fan-out approaches: Fan-out on write (push tweets to all followers' timelines at write time — fast reads, slow writes for high-follower users) vs Fan-out on read (pull and merge at read time — slow reads, fast writes). Hybrid: fan-out on write for normal users, fan-out on read for celebrities. Search: inverted index on keywords. Timeline stored in Redis sorted sets. Media on object store + CDN.
扇出策略：写时扇出（发推时推送到所有粉丝时间线 — 读快写慢，大 V 写入慢）vs 读时扇出（读取时拉取合并 — 读慢写快）。混合：普通用户写扇出，大 V 读扇出。搜索：关键词倒排索引。时间线存 Redis 有序集合。媒体存对象存储 + CDN。

Design a key-value cache to save the results of the most recent web server queries
?
LRU cache using hash map + doubly linked list. On query: check cache first → hit: move to front, return; miss: query DB, store in cache, evict LRU if full. Scale: consistent hashing to distribute keys across cache nodes. Replication for HA. Memory-based (Redis/Memcached). TTL for expiration. Cache invalidation on writes.
LRU 缓存使用哈希表 + 双向链表。查询时：先查缓存 → 命中：移到头部返回；未命中：查 DB，存入缓存，满时淘汰 LRU。扩展：一致性哈希分布键到缓存节点。复制实现高可用。基于内存（Redis/Memcached）。TTL 过期。写入时缓存失效。

Design a system that scales to millions of users on AWS
?
Evolution: single server → separate DB → add load balancer + multiple web servers → read replicas + cache (ElastiCache) → CDN for static assets → split into microservices → add message queues for async → auto-scaling groups → multi-AZ for HA → database sharding. Key AWS services: ELB, EC2 Auto Scaling, RDS (Multi-AZ), ElastiCache, CloudFront, S3, SQS, Route 53.
演进：单服务器 → 分离 DB → 添加负载均衡器 + 多 Web 服务器 → 读副本 + 缓存（ElastiCache）→ CDN 处理静态资源 → 拆分为微服务 → 添加消息队列做异步 → 自动扩展组 → 多 AZ 实现高可用 → 数据库分片。关键 AWS 服务：ELB、EC2 Auto Scaling、RDS（Multi-AZ）、ElastiCache、CloudFront、S3、SQS、Route 53。

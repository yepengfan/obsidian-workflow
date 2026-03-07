# Zettelkasten 实施计划

## 背景

当前 vault 有 375 篇笔记，但知识只进不出：
- 245 篇文献材料（WeRead 223 + Matter 13 + Instapaper 9）停在各自文件夹里，没有加工
- Books/ 的费曼测试产出留在书的上下文里，不跨书流动
- 没有 fleeting notes 收集箱，没有 permanent notes 存放处
- 文件夹之间几乎没有 `[[wikilinks]]` 互联

## 目标

建立 **输入 → 加工 → 永久知识网络** 的管道，覆盖三个知识来源：

1. **阅读**（Books、WeRead、文章） — 读书和文章中的洞察
2. **工作**（Work） — 技术决策、架构模式、项目复盘、踩过的坑
3. **个人成长**（Training、生活技能） — 学习新技能、习惯养成、方法论实践

所有来源的知识都流入同一个 `Zettelkasten/`，通过 `[[wikilinks]]` 互联，让跨领域的洞察自然浮现。

---

## Phase 1: 基础设施

### 1.1 创建 `Inbox/` 文件夹

快速捕捉闪念的收集箱，不限来源。规则：
- 随时往里扔想法，不需要格式
- 来源可以是：读书时的灵感、工作中的想法、生活中的观察、学习新技能时的感悟
- 每周清理一次：加工成 permanent note，或删除
- 不是长期存放处

### 1.2 创建 `Zettelkasten/` 文件夹

Permanent notes 的家。每条笔记：
- 一个原子化想法（3-8 句话）
- 用自己的话写，不是摘抄
- 带 `Related:` 链接到其他 zettel
- 标注来源（哪本书/哪篇文章/哪次经历）

### 1.3 创建笔记模板

**`Templates/Inbox.md`**
```yaml
---
created: {{date}}
source: ""
---

```

**`Templates/Zettel.md`**
```yaml
---
tags: [zettel]
created: {{date}}
source: ""
domain: ""
---

# {{title}}

（用自己的话写一个想法）

---

Related::
```

`domain` 字段用于标记知识领域，例如：
- `reading` — 阅读产出
- `work` — 工作经验（架构决策、排障经验、流程改进等）
- `skill` — 个人技能（跑步、理财、健康、效率方法等）
- `meta` — 关于学习/思考本身的方法论

不做强制分类，一条 zettel 可以不填 domain，也可以跨领域。Dataview 查询可以按 domain 聚合。

### 1.4 更新 Home.md

在 Reading 区域下方新增 Zettelkasten 区域：
- Inbox 待处理数量
- 最近创建的 zettel（5 条）
- 连接最多的 zettel（5 条）

### 1.5 更新 CLAUDE.md

在 Folder Structure 和 Conventions 中补充：
- `Inbox/` 和 `Zettelkasten/` 的用途和规则
- Zettel 的命名和链接约定

---

## Phase 2: 工作流集成

### 2.1 读书 → Zettel

在 `Books/CLAUDE.md` 的 FEYNMAN workflow 末尾，费曼测试结束后新增：
```
6. 提取永久笔记：
   - 从本次费曼测试中识别 1-3 个独立洞察
   - 每个洞察写成一条 zettel（原子化、用自己的话）
   - 链接回章节笔记，同时链接到已有的相关 zettel
   - 问用户：要创建这些永久笔记吗？
```

在 FINAL workflow（读完一本书）中，synthesis 之前：
```
- 回顾所有章节产出的 zettel
- 识别还没提取的跨章节洞察
- 生成建议的新 zettel 列表
```

### 2.2 工作 → Zettel

新增 Claude command: `/retro`（`.claude/commands/retro.md`）

从 Work daily notes 或 project 页面提取工作经验：
- 读取指定的 daily note 或 project 页面
- 识别值得沉淀的技术决策、踩坑经验、流程改进
- 草拟 zettel（domain: work），链接回源笔记
- 确认后创建

触发场景举例：
- 项目上线后复盘："帮我从 IFM 项目里提取经验"
- 周末回顾本周 daily notes："帮我看看这周有什么值得记下来的"
- 解决了一个棘手 bug：随手记到 Inbox，之后加工

### 2.3 个人成长 → Zettel

不需要专门的 workflow，通过 Inbox 收集即可：
- 学跑步时发现的训练原则 → Inbox → Zettel（domain: skill）
- 理财实践中验证的策略 → Inbox → Zettel（domain: skill）
- 培训课程中的关键概念 → Inbox → Zettel（domain: work/skill）

关键是**降低门槛**：Inbox 不要求格式，想到就写，每周集中加工。

### 2.4 通用 command: `/zettel`

`.claude/commands/zettel.md` — 从任意来源提取永久笔记：
- 读取来源内容（书、文章、daily note、project、Inbox 条目）
- 识别可提取的原子化洞察
- 为每个洞察草拟 zettel 内容，自动填写 domain
- 搜索已有 zettel 找到相关链接
- 确认后创建文件

---

## Phase 3: 存量处理

### 3.1 不做大规模迁移

现有的 WeRead/、Matter/、Instapaper Notes/ 保持原样。不需要一次性处理 245 篇笔记。

### 3.2 渐进式提取

- 日常阅读时，遇到有价值的旧高亮，随手提取成 zettel
- 工作中遇到值得记录的决策/经验，先扔 Inbox，周末加工
- `/zettel` command 可以指向任何来源笔记（书、文章、daily note、project）
- Books 系统在费曼测试时自然触发提取

---

## 不做的事

- **不重组现有文件夹** — WeRead、Matter、Work 等结构不变
- **不批量处理旧笔记** — 避免为了形式而做无效劳动
- **不引入复杂编号系统** — Obsidian 的 wikilinks 比 Luhmann 的编号更好
- **不新增插件** — 现有的 Dataview + Spaced Repetition 足够

---

## 实施清单

完成后打勾：

- [x] 创建 `Inbox/` 文件夹（放一个 `.gitkeep`）
- [x] 创建 `Zettelkasten/` 文件夹（放一个 `.gitkeep`）
- [x] 创建 `Templates/Inbox.md`
- [x] 创建 `Templates/Zettel.md`
- [x] 更新 `Home.md` — 新增 Zettelkasten 区域
- [x] 更新 `CLAUDE.md` — 补充 Inbox 和 Zettelkasten 说明
- [x] 更新 `Books/CLAUDE.md` — FEYNMAN 和 FINAL workflow 加入提取步骤
- [x] 创建 `.claude/commands/zettel.md` — 通用知识提取
- [x] 创建 `.claude/commands/retro.md` — 工作经验提取

---

请审阅后告诉我是否可以开始实施，或者有需要调整的地方。

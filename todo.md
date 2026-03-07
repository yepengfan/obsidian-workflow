# Zettelkasten TODO

## 2. Inbox 处理流程

**目标：** 设计周回顾工作流，把 inbox 笔记高效转化为 zettel 或删除。

### 待讨论
- [ ] 周回顾触发方式：手动 `/zettel` 命令 vs 专门的 `/inbox-review` 命令
- [ ] 处理单条 inbox 的流程：读内容 → 判断是否值得保留 → 起草 zettel → 确认创建 → 删除原始 inbox 笔记
- [ ] 批量处理：一次性处理所有 inbox 笔记，还是逐条处理？
- [ ] inbox 笔记处理后如何标记（直接删除 vs 移动到 archive）

### 可能的实现
- 新建 `.claude/commands/inbox-review.md` — 读取 Inbox/ 所有笔记，逐条展示，引导用户决定每条去留

---

## 3. Zettel 质量提升

**目标：** 把现有 seedling zettel 逐步升级，补充跨书目连接。

### 待做
- [ ] 补充 Related 连接：找主题相近但来自不同书的 zettel，手动或半自动建立双向链接
- [ ] Status 升级标准：
  - `seedling` → `growing`：有 2+ Related 连接，内容经过自己重新思考
  - `growing` → `evergreen`：跨多个领域有连接，内容经过多次修订
- [ ] 优先升级连接密度高的主题簇（如：习惯、决策、系统思维）

# Grammar Module — Claude Code Instructions

> 继承 vault root CLAUDE.md 的通用约定。

## Directory Configuration

| Path | Purpose |
|------|---------|
| `Learning/Practice/Grammar/Structures/` | Structure card 文件（一个语法结构一个 .md） |
| `Learning/Practice/Grammar/Log/` | 每日练习记录 |
| `Learning/Practice/Grammar/files/` | 参考书 PDF + 学习计划 MOC |
| `Learning/Practice/Grammar/00_index.md` | Dataview dashboard |
| `Templates/Grammar Structure.md` | 新 card 模板 |
| `Templates/Grammar Log.md` | 新 log 模板 |

## Reference Books

- **Practical English Usage (Swan)** — lookup reference，遇到措辞疑问时查阅，不通读
- **Advanced Grammar in Use (Hewings)** — selective workbook，挑高杠杆 unit 做 card

## Practice Flow

### Phase 1 — Pick & Study

1. 用户指定 structure（如 `/grammar/practice cleft sentences`）
2. 如果 structure card 已存在 → 快速回顾 card 上的 "What it does"
3. 如果不存在 → 引导用户理解该结构的功能和用法，必要时参考 Hewings 相关 unit

### Phase 2 — Rewrite Exercise（Socratic 引导）

用户提供一个自己近期写过的 **plain/flat 句子**。引导重写：

```
[Step 1] 这句话的 main point 是什么？什么是 background/context？
[Step 2] 用目标 structure 重写，把 hierarchy / emphasis / certainty 显式化
[Step 3] 尝试 2-3 个变体（不同 emphasis / 不同 structure shape）
[Step 4] 对比：哪个版本最准确地表达了你的意思？为什么？
```

**引导原则:**
- **不给 "标准答案"** — 引导用户自己生成多个版本，讨论 trade-offs
- 像写作 workshop，不像考试
- 用 Socratic 提问推动，不用陈述句直接告知
- 标注当前步骤（如 `[Step 2/4 重写]`），让用户知道进度

### Phase 3 — Card Update / Create

1. **判断 structure 归属**:
   - 用 `Glob("Learning/Practice/Grammar/Structures/*.md")` 列出所有文件名
   - 判断该练习属于哪个已有 structure card
   - 告诉用户归类结果，确认后继续

2. **已有 structure → 更新**:
   - 追加新的 `> [!example]` section（新的 before→after 重写对）
   - 更新 frontmatter `examples_count` +1
   - 更新 frontmatter `updated` 为今天
   - 如果发现新的 common trap → 追加到 Warning section
   - 如果有新的 variation → 追加到 "Variations worth trying"

3. **新 structure → 创建**:
   - 用 `Templates/Grammar Structure.md` 模板
   - `id`: 读取所有现有 card 的 id，取最大值 +1
   - 填充: title, structure slug, source, before→after, tip, variations, warning
   - `difficulty`: 基于结构掌握难度评估
   - `examples_count`: 1

### Phase 4 — Log

1. 检查 `Learning/Practice/Grammar/Log/YYYY-MM-DD.md` 是否存在
2. 不存在 → 用 `Templates/Grammar Log.md` 创建，填充第一条
3. 已存在 → 追加新 `##` section，更新 frontmatter `structures_practiced` 数组
4. 包含: structure wikilink、before→after 摘要、insight

## Structure Card Rules

- **归类前必须先查已有 structure**: 用 `Glob("Learning/Practice/Grammar/Structures/*.md")` 列出所有文件名。扫描文件名判断是否有匹配的 structure。**绝不跳过此步直接新建。**
- `difficulty` 指 structure 掌握难度，非单次练习难度
- 文件名 = structure title（去掉文件系统非法字符 `/ \ : * ? " < > |`）
- `tags` 格式: `[grammar/expressive, english]`
- `examples_count` 与正文中 `> [!example]` block 数量保持一致

## Log Rules

- 每次练习一个 `##` section
- 包含 structure wikilink `[[structure name]]`、before→after 摘要、insight
- frontmatter `structures_practiced` 数组与正文 sections 保持一致
- 文件名: `YYYY-MM-DD.md`
- 如果当天 log 已存在，追加新 section（不覆盖）

## Language

- 引导讨论默认英文（这是英语练习模块）
- 用户用中文提问则中文回复
- 练习句子始终英文

## Do NOT

- 不要直接给 "最佳重写" — 引导用户自己生成
- 不要删除或修改 files/ 下的 PDF 参考书
- 不要把 error-correction 当作练习目标 — 焦点是 expressive range

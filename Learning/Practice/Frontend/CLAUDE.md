# Frontend Module — Claude Code Instructions

> 继承 vault root CLAUDE.md 的通用约定。

## Directory Configuration

| Path | Purpose |
|------|---------|
| `Learning/Practice/Frontend/Patterns/` | Pattern card 文件（一个 pattern 一个 .md） |
| `Learning/Practice/Frontend/Log/` | 每日练习记录 |
| `Learning/Practice/Frontend/Attachments/` | 效果截图、GIF |
| `Learning/Practice/Frontend/sandbox/` | Next.js 练习项目（可运行代码） |
| `Learning/Practice/Frontend/00_index.md` | Dataview dashboard |
| `Templates/Frontend Pattern.md` | 新 card 模板 |
| `Templates/Frontend Log.md` | 新 log 模板 |

## Sandbox Project

`sandbox/` 是一个 Next.js 15 (App Router) + TypeScript + Tailwind CSS 项目。

- **UI Component 题**: `sandbox/app/challenges/<name>/page.tsx`（每题一个 route，`npm run dev` 后访问 `/challenges/<name>`）
- **JS Utility 题**: `sandbox/challenges/<name>.ts` + `sandbox/challenges/<name>.test.ts`
- **Frontend System Design 题**: `sandbox/app/challenges/<name>/` 多文件

### Sandbox 操作约定

- 新建 challenge 时自动创建骨架文件（见 Solving Flow Phase 0）
- `code_path` 字段记录相对于 `sandbox/` 的路径（如 `app/challenges/accordion` 或 `challenges/debounce.ts`）
- `node_modules/` 和 `.next/` 已加入 Obsidian ignore（不被索引）

## Challenge Types

GFE 三种题型对应不同的引导侧重：

| Type | 关键词 | 引导侧重 |
|------|--------|---------|
| `ui-component` | Accordion, Tabs, Modal, Autocomplete | 组件拆分、状态管理、a11y、事件处理 |
| `js-utility` | debounce, deepClone, Promise.all | 底层实现、edge cases、类型处理 |
| `frontend-system-design` | News Feed, Image Carousel, Chat Widget | 架构设计、性能、数据流、扩展性 |

## Solving Flow

### Phase 0 — 初始化 Challenge

1. 从 `$ARGUMENTS` 提取题目名称，确定 challenge type（`ui-component` / `js-utility` / `frontend-system-design`）
2. 检查 `sandbox/app/challenges/<name>/page.tsx`（UI）或 `sandbox/challenges/<name>.ts`（JS Utility）是否已存在:
   - **已存在** → 询问是否继续未完成的练习还是重新开始
   - **不存在** → 创建骨架文件（见下方）
3. **创建骨架**:
   - **UI Component**: 创建 `sandbox/app/challenges/<name>/page.tsx`，包含空组件 + 基本 props interface
   - **JS Utility**: 创建 `sandbox/challenges/<name>.ts`（空函数签名）+ `sandbox/challenges/<name>.test.ts`（基本测试骨架）
   - **Frontend System Design**: 创建 `sandbox/app/challenges/<name>/page.tsx` + 按需子组件文件
4. 告诉用户骨架已创建，可以 `npm run dev` 预览

### Phase 1 — 引导实现（渐进 3 层）

用户提供了题目。按以下层级 **逐层推进**，每层用 Socratic 提问引导，不要跳层。

#### L1 — 需求分析 & 组件拆分
- 确认功能需求、交互细节、edge cases
- 问: "这个组件拆成几个部分？哪些是 state，哪些是 props？"
- UI 题额外问: "键盘交互呢？ARIA 属性需要哪些？"
- JS Utility 题额外问: "输入类型有哪些 edge case？返回值语义是什么？"
- 用户能描述出组件结构/函数签名后 → 进入 L2

#### L2 — 实现策略引导
- 给出关键 pattern hint，但 **不说具体实现**（如 "这里需要一个 cleanup pattern" 而非 "用 useEffect return"）
- 引导状态管理方案选择（local state vs context vs URL state）
- 引导性能考量（"列表很长时会怎样？"）
- 用户识别出正确方案后 → 进入 L3

#### L3 — 骨架代码（最后手段）
- **仅在以下情况给出**: 用户明确说 "给我看代码" / "我卡住了" / 卡在 L2 超过 3 轮
- 给出前先问: "需要我给骨架代码吗？还是再想想？"
- 给出组件骨架 / 函数签名 + 关键逻辑注释，不给完整实现

**引导原则:**
- 每层用 1-2 个 Socratic 提问
- 标注当前层级（如 `[L1/3 需求分析]`）
- 只在用户说 "show me the code" / "给我看代码" / "我放弃" 时给完整代码

### Phase 2 — Code Review

1. 用户完成实现（贴代码或指向 sandbox 文件）
2. 审核以下方面:
   - **功能正确性**: 是否满足所有需求
   - **React Best Practices**: hooks 规则、re-render 优化、key 使用、受控 vs 非受控
   - **TypeScript**: 类型是否准确、是否滥用 `any`
   - **可访问性 (a11y)**: ARIA 属性、键盘导航、焦点管理、语义 HTML
   - **响应式**: 是否适配不同屏幕尺寸
   - **性能**: 不必要的 re-render、大列表优化、事件监听清理
   - **Edge Cases**: 空状态、loading 状态、错误处理
3. 如果有问题 → 指出具体行和原因，**不重写**（targeted fix only）
4. 代码通过后进入 Phase 3

### Phase 3 — 沉淀

1. **判断 pattern 归属**:
   - 用 `Glob("Learning/Practice/Frontend/Patterns/*.md")` 列出所有文件名
   - 判断该题涉及哪些已有 pattern
   - 告诉用户归类结果，确认后继续

2. **已有 pattern → 更新**:
   - 在 frontmatter `problems` 数组末尾加题名
   - 在正文 Problems 表格加一行（题名、type、难度、今天日期）
   - 更新 frontmatter `updated` 为今天
   - 如果有新的 Gotcha 发现，追加到 Gotchas section

3. **新 pattern → 创建**:
   - 用 `Templates/Frontend Pattern.md` 模板
   - `id`: 读取所有现有 card 的 id，取最大值 +1
   - 填充: title, category, tags, problems, Key Insight, When to Reach For, Code Example, Gotchas
   - `difficulty`: 基于 pattern 复杂度评估

4. **写 Log**:
   - 检查 `Learning/Practice/Frontend/Log/YYYY-MM-DD.md` 是否存在
   - 不存在 → 用 `Templates/Frontend Log.md` 创建，填充第一条
   - 已存在 → 追加新 `##` section，更新 frontmatter `challenges_completed` 数组
   - 包含: pattern wikilink、type、difficulty、result emoji、code_path、notes

## Pattern Card Rules

- **归类前必须先查已有 pattern**: 用 `Glob("Learning/Practice/Frontend/Patterns/*.md")` 列出所有文件名。扫描文件名判断是否有匹配的 pattern，有疑问时读 frontmatter 确认。**绝不跳过此步直接新建。**
- **已有 pattern**: 加题名到 frontmatter `problems[]` + 正文 Problems 表格加一行 + 更新 `updated` 日期
- **新 pattern**: 创建新文件（用 `Templates/Frontend Pattern.md`），id 取当前最大值 +1，填充所有字段
- `difficulty` 指 pattern 理解难度，非单题难度
- 文件名 = pattern title（去掉文件系统非法字符 `/ \ : * ? " < > |`）
- `tags` 格式: `[frontend/pattern, frontend/{category-slug}]`

## Log Rules

- 每道题一个 `##` section
- 包含 pattern wikilink `[[pattern name]]`、type、difficulty、result emoji、code_path、notes
- frontmatter `challenges_completed` 数组与正文 sections 保持一致
- 文件名: `YYYY-MM-DD.md`
- 如果当天 log 已存在，追加新 section（不覆盖）

## Category Values

合法 category 值（与 Dataview 分组键一致）:

- Component Patterns
- Hooks
- State Management
- Performance
- Data Fetching
- Routing & Navigation
- Server Components & Actions
- Styling & Layout
- Accessibility
- Form Handling

新 category 可按需添加，但优先归入已有类别。

## Language

- 技术讨论默认英文，用户用中文则中文回复
- 代码始终 TypeScript + React (TSX)，clean and readable
- 中英混排时遵循 vault 现有风格

## Do NOT

- 不要主动给完整代码（除非用户明确要求）
- 不要重写用户代码（targeted fix only）
- 不要修改 sandbox 的配置文件（package.json, tsconfig 等）除非用户要求
- 不要在 sandbox 之外创建 .ts/.tsx 文件

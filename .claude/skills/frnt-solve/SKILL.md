---
name: frnt-solve
description: >-
  Frontend challenge workflow — sandbox setup, guided implementation, code review, pattern card logging. Use for GreatFrontEnd-style challenges or /frnt/solve.
disable-model-invocation: true
---

<!-- module: frontend -->
> [!GUARD] Read `system/modules/frontend/module.md`. If `enabled: false` → reply "⛔ Module **frontend** is disabled. Enable it via `/module-toggle frontend`." and STOP. Do NOT proceed.

Solve Frontend challenge: $ARGUMENTS

Read `Learning/Practice/Frontend/CLAUDE.md` for module instructions.

## Phase 0 — 初始化 Challenge

1. 从 `$ARGUMENTS` 提取题目名称，转为 kebab-case slug（如 "Accordion" → "accordion", "Star Rating" → "star-rating"）
2. 判断 challenge type（按优先级从高到低匹配，更具体的规则优先）:
   - 含 "design" / "system" → `frontend-system-design`
   - 含 JS API 名（debounce, throttle, Promise, curry, deepClone, flatten, classNames, etc.） → `js-utility`
   - 含常见 UI 组件名（Accordion, Tabs, Modal, Autocomplete, etc.）或 "build" / "component" → `ui-component`
   - 不确定 → 问用户
3. 检查是否已存在:
   - **UI Component / FE System Design**: 检查 `Learning/Practice/Frontend/sandbox/app/challenges/<slug>/page.tsx`
   - **JS Utility**: 检查 `Learning/Practice/Frontend/sandbox/challenges/<slug>.ts`
   - 已存在 → 询问是否继续或重新开始
4. **创建骨架**:
   - **UI Component**:
     ```
     sandbox/app/challenges/<slug>/page.tsx
     ```
     内容: 空 React 组件 + 基本 props interface + "use client" 指令
   - **JS Utility**:
     ```
     sandbox/challenges/<slug>.ts
     sandbox/challenges/<slug>.test.ts
     ```
     内容: 空函数签名 + 基本测试骨架
   - **Frontend System Design**:
     ```
     sandbox/app/challenges/<slug>/page.tsx
     sandbox/app/challenges/<slug>/components/  (按需)
     ```
5. 告诉用户骨架已创建，可以 `cd Learning/Practice/Frontend/sandbox && npm run dev` 后访问 `/challenges/<slug>` 预览

## Phase 1 — 引导实现（渐进 3 层）

用户提供了题目。按以下层级 **逐层推进**，每层用 Socratic 提问引导，不要跳层。

引导方向时参考 `Learning/Practice/Frontend/CLAUDE.md` 的「心法」——React 思维模型（UI=f(state)、单向数据流、组合优于继承、副作用隔离）。

### L1 — 需求分析 & 组件拆分
- 确认功能需求、交互细节、edge cases
- 问: "这个组件拆成几个部分？哪些需要 state？"
- UI 题额外问: "键盘交互呢？ARIA 属性需要哪些？"
- JS Utility 题额外问: "输入类型有哪些 edge case？返回值语义是什么？"
- 用户能描述出组件结构/函数签名后 → 进入 L2

### L2 — 实现策略引导
- 给出关键 pattern hint，但 **不说具体实现**
- 引导 hooks 选择（"这个副作用什么时候需要清理？"）
- 引导性能考量（"列表很长时会怎样？"）
- 用户识别出正确方案后 → 进入 L3

### L3 — 骨架代码（最后手段）
- **仅在以下情况给出**: 用户明确说 "给我看代码" / "我卡住了" / 卡在 L2 超过 3 轮
- 给出前先问: "需要我给骨架代码吗？还是再想想？"
- 给出组件骨架 / 函数签名 + 关键逻辑注释，不给完整实现

**引导原则:**
- 每层用 1-2 个 Socratic 提问
- 标注当前层级（如 `[L1/3 需求分析]`）
- 只在用户说 "show me the code" / "给我看代码" / "我放弃" 时给完整代码

## Phase 2 — Code Review

1. 用户完成实现（贴代码或说 "review my code"）
2. 如果代码在 sandbox 文件中，Read 对应文件
3. 审核以下方面:
   - **功能正确性**: 是否满足所有需求
   - **React Best Practices**: hooks 规则、re-render 优化、key 使用、受控 vs 非受控
   - **TypeScript**: 类型准确性、避免 `any`
   - **可访问性 (a11y)**: ARIA 属性、键盘导航、焦点管理、语义 HTML
   - **响应式**: 是否适配不同屏幕尺寸
   - **性能**: 不必要的 re-render、事件监听清理、memo 使用
   - **Edge Cases**: 空状态、loading、错误处理
4. 如果有问题 → 指出具体行和原因，**不重写**
5. 代码通过后进入 Phase 3

## Phase 3 — 沉淀

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

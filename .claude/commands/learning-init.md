Create a new Learning Plan for: $ARGUMENTS

## Steps

1. **Parse the plan name** from $ARGUMENTS (e.g. "AI-SA", "System-Design"). If no argument provided, ask the user.

2. **Assign a short code**: Suggest a 4-5 letter uppercase code derived from the plan name (e.g. "AI-SA" → "AISA", "System-Design" → "SYSD"). Confirm with the user before proceeding.

3. **Create the folder structure** in `Learning/<CODE>/`:
   ```
   Learning/<CODE>/
     Weeks/
     Courses/
     Projects/
     Attachments/
   ```

4. **Create `Learning/<CODE>/00_plan.md`**:
   ```markdown
   ---
   plan: <CODE>
   code: <CODE>
   status: active
   phase: 1
   started: <today's date>
   target:
   tags: [learning/<CODE>]
   ---

   # <Plan Name> — Learning Plan

   ## 目标

   成为 <role>，能够 <capability>。

   **时间预算**: 每周 X 小时
   **总时间线**: ~N 个月（YYYY.MM - YYYY.MM）
   **原则**: 可行性第一 — 宁可多花 1 个月，不交半成品

   ---

   ## 阶段划分

   ### Phase 1 — <Focus>（Month 1-N，约 YYYY.MM - YYYY.MM）

   **目标**: <What you can do by the end of this phase>

   | 模块 | 内容 | 状态 |
   |------|------|------|
   | MOD-1 | <Description> | ⏳ 待开始 |

   **阶段 1 关键产出**:
   - [ ] <Deliverable 1>
   - [ ] <Deliverable 2>

   ---

   ### Phase 2 — <Focus>（Month N-M，约 YYYY.MM - YYYY.MM）

   **目标**: <What you can do by the end of this phase>

   | 模块 | 内容 | 状态 |
   |------|------|------|
   | MOD-2 | <Description> | ⏳ 待开始 |

   **阶段 2 关键产出**:
   - [ ] <Deliverable 1>
   - [ ] <Deliverable 2>

   ---

   ## 每周时间预算

   | 线路 | 周时间 | 说明 |
   |------|--------|------|
   | 主线 | Xh | <Description> |
   | **合计** | **Xh** | |

   ---

   ## 完成标准

   - [ ] <Criterion 1>
   - [ ] <Criterion 2>

   ---

   ## 资源

   ### 认证
   -

   ### 课程
   -

   ### 书籍
   -

   ### 工具
   -
   ```

5. **Create `Learning/<CODE>/00_map.md`**:
   ```markdown
   ---
   plan: <CODE>
   code: <CODE>
   tags: [learning/<CODE>]
   ---

   # <Plan Name> — Concept Map

   > Add key concepts and their connections as you learn. Link to zettel when concepts are internalized.

   ## Core Concepts

   ## Connections to Existing Knowledge

   ## Technology Radar

   > Rate each tool/framework as you learn it. Consolidate into a full radar in Phase 4.

   | Tool / Framework | Category | Rating | Notes |
   |------------------|----------|--------|-------|
   ```

6. **Confirm** what was created and prompt the user to fill in `00_plan.md` (goals, phases, weekly budget, completion criteria).

## Rules

- Use the confirmed code as the folder name (e.g. `Learning/AISA/`)
- If `Learning/<CODE>/` already exists, ask before overwriting any files
- Do not pre-create course or project subfolders — those are created on demand

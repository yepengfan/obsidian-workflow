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

   ## 阶段划分

   ### Phase 1

   ## 每周时间预算

   ## 完成标准

   - [ ]

   ## 资源

   - Courses:
   - Books:
   - Projects:
   ```

5. **Create `Learning/<CODE>/00_map.md`**:
   ```markdown
   ---
   plan: <CODE>
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

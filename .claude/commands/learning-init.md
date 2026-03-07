Create a new Learning Plan for: $ARGUMENTS

## Steps

1. **Parse the plan name** from $ARGUMENTS (e.g. "AI-SA", "System-Design"). If no argument provided, ask the user.

2. **Create the folder structure** in `Learning/<plan-name>/`:
   ```
   Learning/<plan-name>/
     Weeks/
     Courses/
     Projects/
   ```

3. **Create `Learning/<plan-name>/00_plan.md`**:
   ```markdown
   ---
   plan: <plan-name>
   status: active
   started: <today's date>
   target:
   tags: [learning/<plan-name>]
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

4. **Create `Learning/<plan-name>/00_map.md`**:
   ```markdown
   ---
   plan: <plan-name>
   tags: [learning/<plan-name>]
   ---

   # <Plan Name> — Concept Map

   > Add key concepts and their connections as you learn. Link to zettel when concepts are internalized.

   ## Core Concepts

   ## Connections to Existing Knowledge
   ```

5. **Confirm** what was created and prompt the user to fill in `00_plan.md` (goals, phases, weekly budget, completion criteria).

## Rules

- Use the exact plan name as the folder name
- If `Learning/<plan-name>/` already exists, ask before overwriting any files
- Do not pre-create course or project subfolders — those are created on demand

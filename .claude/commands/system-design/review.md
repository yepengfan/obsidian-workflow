<!-- module: system-design -->
> [!GUARD] Read `system/modules/system-design/module.md`. If `enabled: false` → reply "⛔ Module **system-design** is disabled. Enable it via `/module-toggle system-design`." and STOP. Do NOT proceed.

Review system design patterns for revision.

Read `Learning/System-Design/CLAUDE.md` for module instructions.

## Steps

1. **Scan all patterns**: Read frontmatter of all files in `Learning/System-Design/Patterns/`

2. **Sort by priority**:
   - `updated` ascending (oldest first — 最久未复习优先)

3. **Present review table**:

   Display a markdown table with columns:
   | Pattern | Category | Problems | Last Updated |
   |---------|----------|----------|-------------|
   Show all patterns, sorted by `updated` ascending.

4. **Offer drill-down**: Ask if user wants to:
   - 复习某个具体 pattern（打开对应 card）
   - 做一道该 pattern 的题（转到 `/system-design/solve`）

5. **Stats summary**:
   - 总 pattern 数
   - 最久未更新的 3 个 patterns
   - 本周/本月通过 Log 统计的做题数

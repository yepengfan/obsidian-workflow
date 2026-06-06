<!-- module: algorithm -->
> [!GUARD] Read `system/modules/algorithm/module.md`. If `enabled: false` → reply "⛔ Module **algorithm** is disabled. Enable it via `/module-toggle algorithm`." and STOP. Do NOT proceed.

Review algorithm patterns for revision.

Read `Learning/Practice/Algorithm/CLAUDE.md` for module instructions.

## Steps

1. **Scan all patterns**: Read frontmatter of all files in `Learning/Practice/Algorithm/Patterns/`

2. **Sort by priority**:
   - `updated` ascending (oldest first — 最久未复习优先)

3. **Present review table**:

   Display a markdown table with columns:
   | Pattern | Category | Problems | Last Updated |
   |---------|----------|----------|-------------|
   Show all patterns, sorted by `updated` ascending.

4. **Offer drill-down**: Ask if user wants to:
   - 复习某个具体 pattern（打开对应 card）
   - 做一道该 pattern 的新题（转到 `/algorithm/solve`）
   - 重做该 pattern 的旧题验证掌握程度（转到 `/algorithm/solve`）

5. **Stats summary**:
   - 总 pattern 数
   - 最久未更新的 3 个 patterns
   - 本周/本月通过 Log 统计的做题数

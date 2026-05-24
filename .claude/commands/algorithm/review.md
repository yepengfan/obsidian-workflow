<!-- module: algorithm -->
> [!GUARD] Read `system/modules/algorithm/module.md`. If `enabled: false` → reply "⛔ Module **algorithm** is disabled. Enable it via `/module-toggle algorithm`." and STOP. Do NOT proceed.

Review algorithm patterns for revision.

Read `Learning/Algorithm/CLAUDE.md` for module instructions.

## Steps

1. **Scan all patterns**: Read frontmatter of all files in `Learning/Algorithm/Patterns/`

2. **Sort by priority**:
   - Primary: `confidence` ascending (weakest first)
   - Secondary: `updated` ascending (oldest first)

3. **Present review table**:

   Display a markdown table with columns:
   | Pattern | Category | Problems | Confidence | Last Updated |
   |---------|----------|----------|------------|-------------|
   Show all patterns, sorted by priority above. Confidence uses stars: 1=⭐, 2=⭐⭐, etc.

4. **Highlight action items**:
   - 🔴 `confidence ≤ 2`: "需要重点复习"
   - 🟡 `confidence = 3`: "建议巩固"
   - 🟢 `confidence ≥ 4`: "掌握良好"

5. **Offer drill-down**: Ask if user wants to:
   - 复习某个具体 pattern（打开对应 card）
   - 做一道该 pattern 的新题（转到 `/algorithm/solve`，做完后 confidence 会自动更新）

6. **Stats summary**:
   - 总 pattern 数
   - 各 confidence 等级分布
   - 最久未更新的 3 个 patterns
   - 本周/本月通过 Log 统计的做题数

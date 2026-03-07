Sync Book Summaries with the latest WeRead highlights.

## Steps

1. **Detect changes** by running the sync check script:
   ```
   python3 ".claude/scripts/sync-check.py"
   ```

2. **If output is `ALL_SYNCED`**: Report that all book summaries are up to date. Done.

3. **If there are results**, parse the output:
   - `NEEDS_UPDATE:<weread_source>|<summary_file>` — the WeRead file has been modified since the summary was last generated. Regenerate the summary.
   - `NEW_BOOK:<weread_source>` — a new WeRead book with highlights but no summary yet. Create a new summary.

4. **Process each book** that needs updating:
   - Read the WeRead source file
   - For `NEEDS_UPDATE`: Read the existing summary too, then regenerate it with all current highlights. Keep the same filename. Update `date_summarized` to today's date.
   - For `NEW_BOOK`: Create a new summary file following the standard template (see below). Add appropriate aliases (short Chinese title + full title).

5. **Use parallel agents** if there are more than 3 books to process (batch into groups of ~10).

6. **Report** what was updated and what was created.

## Summary Template

Every summary must follow this exact structure:

```markdown
---
title: "[Original Chinese title]"
aliases: ["[Short Chinese title]", "[Full Chinese title if different]"]
author: "[Author name]"
source: "[[WeRead/path/to/source]]"
date_summarized: [today's date]
tags: book-summary
---

# [English Title]

> [!info] Book Info
> - **Author**: [Author name]
> - **Progress**: [from WeRead metadata]
> - **Reading Time**: [from WeRead metadata]

## Key Themes

### [Theme Name]

[2-3 sentence thematic synthesis — do NOT just list highlights, synthesize them into insight]

> "[Representative quote from the highlights]"

[Repeat for 3-7 themes depending on highlight volume]

## Core Takeaways

- [5-8 bullet points distilling the most important insights]

---

## 中文摘要

### 主题总结

#### [Chinese theme name — mirrors English themes]

[Chinese synthesis of the theme]

> "[Original Chinese quote from WeRead — never back-translate from English]"

### 核心要点

- [Chinese bullet points mirroring English takeaways]

## Source

- Original highlights: [[WeRead/path/to/source]]
```

## Rules

- NEVER modify anything in the `WeRead/` folder
- Use original Chinese quotes from the WeRead source — do not translate English back to Chinese
- The English section should be a thematic synthesis, not a chapter-by-chapter summary
- Keep aliases useful for Quick Switcher search (include short Chinese title)

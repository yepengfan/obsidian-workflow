Extract permanent notes (zettel) from: $ARGUMENTS

Workflow:
1. Read the source note/file specified by the user (can be a book chapter, article, daily note, Inbox item, or any other note)
2. Identify atomic, standalone insights worth keeping long-term — each should make sense on its own, outside the original context
3. For each insight, draft a zettel:
   - **Title**: a descriptive statement (not a topic word — e.g., "Caching trades consistency for latency" not "Caching")
   - **Content**: 3-8 sentences in the user's own words, not copy-paste from source
   - **source**: wikilink to the original note
   - **domain**: one of `reading`, `work`, `skill`, `meta`
   - **Related**: search existing `Zettelkasten/` notes for thematic connections, add wikilinks
   - **Original quote**: use a `> [!quote]` callout with an `![[source#^block-id]]` embed linking to the exact highlight in the source file. Include the chapter/section name in the callout title (e.g., `> [!quote] 原文 — 第三章 学习幸福`). If the source has block IDs (like WeRead highlights), always use block embeds instead of copying text.
4. Present all drafted zettel to the user for review
5. On confirmation, create each as a separate file in `Zettelkasten/` using the `Templates/Zettel.md` format
6. Filename: use the title in lowercase with spaces replaced by hyphens (e.g., `caching-trades-consistency-for-latency.md`)

Rules:
- Never create zettel without user confirmation
- Each zettel must be atomic — one idea only
- Write in whatever language the user uses
- Always search existing zettel for connections before creating new ones
- Always link to source highlights via block embed, never copy-paste original text

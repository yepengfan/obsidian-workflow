---
name: vault-ops-research
description: >-
  Research a topic and capture findings in the vault. Use for /vault-ops-research.
disable-model-invocation: true
---

<!-- module: vault-ops -->
> [!GUARD] Read `system/modules/vault-ops/module.md`. If `enabled: false` → reply "⛔ Module **vault-ops** is disabled. Enable it via `/module-toggle vault-ops`." and STOP. Do NOT proceed.

---

Research the topic I specify using web search, then create a well-structured note in `Inbox/`.

File name: Use a concise, descriptive name in the same language as the topic.

Structure:
```
---
date: <today's date>
tags: research
---
```

- `## Summary` — 3-5 sentence overview
- `## Key Points` — bullet points of the most important findings
- `## Details` — deeper exploration organized by subtopic
- `## Sources` — list URLs used
- `## Related` — wikilinks to any existing notes in the vault that relate to this topic (search the vault first, exclude WeRead/)

Use the same language as the topic I provide. If the topic is in Chinese, write the note in Chinese. If in English, write in English.

Topic: $ARGUMENTS

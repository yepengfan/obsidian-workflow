---
name: vault-ops-organize
description: >-
  Organize vault files and folders. Use for /vault-ops/organize.
disable-model-invocation: true
---

<!-- module: vault-ops -->
> [!GUARD] Read `system/modules/vault-ops/module.md`. If `enabled: false` → reply "⛔ Module **vault-ops** is disabled. Enable it via `/module-toggle vault-ops`." and STOP. Do NOT proceed.

---

Review notes in the folder I specify (or the vault root if none given) and help organize them:

1. Identify notes that might be in the wrong folder
2. Find orphan notes with no links to or from other notes
3. Suggest notes that could be merged or split
4. Look for missing wikilinks between related notes
5. Check for notes missing frontmatter

Present your findings as a report. Do NOT make any changes without my approval. Do NOT touch anything in `WeRead/`.

$ARGUMENTS

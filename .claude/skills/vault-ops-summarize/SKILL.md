---
name: vault-ops-summarize
description: >-
  Summarize notes or documents in the vault. Use for /vault-ops/summarize.
disable-model-invocation: true
---

<!-- module: vault-ops -->
> [!GUARD] Read `system/modules/vault-ops/module.md`. If `enabled: false` → reply "⛔ Module **vault-ops** is disabled. Enable it via `/module-toggle vault-ops`." and STOP. Do NOT proceed.

---

Read the note or folder I specify and create a concise summary.

- If given a single note: summarize its key points in 3-5 bullets
- If given a folder: list all notes with a one-line summary of each
- If given a WeRead book folder: read the highlights and produce a structured book summary with key takeaways, organized by theme rather than chapter order

Output the summary directly in the chat. If I ask you to save it, create a note in `Inbox/` with appropriate frontmatter.

Do NOT modify any files in `WeRead/`.

$ARGUMENTS

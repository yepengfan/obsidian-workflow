---
name: brownbag
description: >-
  Create a brownbag session plan from Templates/Brownbag Session.md. Use when planning a brownbag talk or /brownbag/brownbag.
disable-model-invocation: true
---

<!-- module: brownbag -->
> [!GUARD] Read `system/modules/brownbag/module.md`. If `enabled: false` → reply "⛔ Module **brownbag** is disabled. Enable it via `/module-toggle brownbag`." and STOP. Do NOT proceed.

---

Create a new brownbag session note at `Work/Brownbag Sessions/$ARGUMENTS/$ARGUMENTS.md` using the `Templates/Brownbag Session.md` template.

Each session lives in its own subfolder under `Work/Brownbag Sessions/`. The subfolder name matches the session topic.

1. First, scan all existing notes in `Work/Brownbag Sessions/` (recursively) and find the highest `id` value (format: `BB-N`). The new session gets `BB-(N+1)`. If no sessions exist yet, start with `BB-1`.
2. Create the subfolder `Work/Brownbag Sessions/$ARGUMENTS/` if it doesn't exist.
3. Replace `{{id}}` with the next number, `{{title}}` with the session topic provided, and `{{date}}` with today's date (YYYY-MM-DD).
4. If the session note already exists, tell me instead of overwriting it.

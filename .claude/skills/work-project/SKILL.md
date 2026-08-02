---
name: work-project
description: >-
  Create or update a work project page from template. Use for /work/project.
disable-model-invocation: true
---

<!-- module: work -->
> [!GUARD] Read `system/modules/work/module.md`. If `enabled: false` → reply "⛔ Module **work** is disabled. Enable it via `/module-toggle work`." and STOP. Do NOT proceed.

---

Create a new project page at `Work/Projects/$ARGUMENTS.md` using the `Templates/Work Project.md` template. Replace `{{title}}` with the project name provided. If the project page already exists, tell me instead of overwriting it.

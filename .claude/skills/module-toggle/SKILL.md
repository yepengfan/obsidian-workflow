---
name: module-toggle
description: >-
  List or toggle vault module enabled state in system/modules/. Use for /module-toggle.
disable-model-invocation: true
---

Toggle a module's enabled state.

**Usage**: `/module-toggle <module-name>` or `/module-toggle` (to list all modules)

## Steps

### If no argument provided — list all modules with their current state:

1. Read all `system/modules/*/module.md` files
2. Display a table:
   | Module | Enabled | Type | Commands |
   |--------|---------|------|----------|
   | zettelkasten | ✅ | knowledge | zettel, retro, backlink, inbox-review, project-retro |
   | ... | ... | ... | ... |
3. Ask which module to toggle (or stop if user just wanted to see the list)

### If argument provided — toggle that module:

1. Verify the module exists: check if `system/modules/$ARGUMENTS/module.md` exists
   - If not found, list available modules and stop

2. Read `system/modules/$ARGUMENTS/module.md` frontmatter
   - Get current `enabled` value (true or false)

3. **Dependency check** before disabling:
   - If toggling from `enabled: true` → `enabled: false`:
     - Read ALL other module.md files
     - Check if any module's `depends_on` includes this module name
     - If yes, WARN: "⚠️ The following modules depend on **$ARGUMENTS**: [list]. Disabling may affect them."
     - Ask for confirmation before proceeding

4. **Prerequisite check** before enabling:
   - If toggling from `enabled: false` → `enabled: true`:
     - Read the module's `requires` field from frontmatter
     - Check each prerequisite category and report status:

     **a. `requires.cli`** — CLI tools (e.g. `claude`, `git`):
     ```bash
     command -v <tool> >/dev/null 2>&1
     ```
     - ✅ found → show version if possible
     - ❌ not found → flag as missing

     **b. `requires.python`** — Python version:
     ```bash
     python3 --version
     ```
     - ✅ meets minimum → show version
     - ❌ not found or below minimum → flag as missing

     **c. `requires.pip`** — Python packages:
     - Check if the module has a `.venv/` directory under its scripts path (from `scripts` field)
     - If `.venv/` exists, check packages inside it: `<venv>/bin/pip show <package>`
     - If no `.venv/`, check system: `python3 -c "import <package>"`
     - ✅ importable → show
     - ❌ not found → flag as missing

     **d. `requires.plugins`** — Obsidian plugins:
     - Check `.obsidian/plugins/<plugin-id>/manifest.json` exists
     - ✅ found → show
     - ⚠️ not found → warn (cannot auto-install, user must install from Obsidian)

     **e. `requires.env`** — Environment variables:
     ```bash
     echo "${<VAR_NAME>:+set}"
     ```
     - Check the description string for `(required)` or `(optional)` prefix:
       - `(required)`: ✅ set → show (masked), ❌ not set → hard failure
       - `(optional)` or no prefix: ✅ set → show (masked), ⚠️ not set → soft warning

     **f. `depends_on`** — Module dependencies:
     - Read each dependency's module.md
     - ✅ `enabled: true` → ok
     - ❌ `enabled: false` → flag: "Dependency **<name>** is disabled. Enable it first."

     **Display results** as a checklist:
     ```
     ## 前置条件检查 — <module-name>

     ✅ CLI: claude (v1.x.x), git (v2.x.x)
     ✅ Python: 3.13.1 (>= 3.13)
     ✅ Packages: aiohttp
     ✅ Plugins: dataview, obsidian-shellcommands
     ⚠️ Env: GITHUB_TOKEN not set — (optional) Higher API rate limit
     ✅ Modules: dashboard (enabled)
     ```

     **If any ❌ (hard failures) exist**: Show the full report, then STOP. Do NOT toggle.
     Say: "❌ Cannot enable — fix the items above first."

     **If only ⚠️ (warnings) exist**: Show the report, ask for confirmation.
     Say: "⚠️ Some optional prerequisites are missing. Enable anyway?"

     **If all ✅**: Proceed to toggle.

5. **Toggle** the `enabled` field:
   - `enabled: true` → `enabled: false`
   - `enabled: false` → `enabled: true`
   - Use the Edit tool to make the change

6. **Report** what changed:
   - State change: `enabled: true → false` or `enabled: false → true`
   - Affected commands: list all commands from the module's `commands` field
   - Affected scripts: list from `scripts` field
   - Affected hooks: list from `hooks` field
   - If disabling: "These commands will refuse to run until re-enabled."
   - If enabling: "These commands are now active."
   - If enabling: Show the module's `## Quick Start` section as a hint for how to get started

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

4. **Toggle** the `enabled` field:
   - `enabled: true` → `enabled: false`
   - `enabled: false` → `enabled: true`
   - Use the Edit tool to make the change

5. **Report** what changed:
   - State change: `enabled: true → false` or `enabled: false → true`
   - Affected commands: list all commands from the module's `commands` field
   - Affected scripts: list from `scripts` field
   - Affected hooks: list from `hooks` field
   - If disabling: "These commands will refuse to run until re-enabled."
   - If enabling: "These commands are now active."

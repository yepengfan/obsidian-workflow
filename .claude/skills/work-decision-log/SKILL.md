---
name: work-decision-log
description: >-
  Record a structured decision log entry for a work project. Use for /work/decision-log.
disable-model-invocation: true
---

<!-- module: work -->
> [!GUARD] Read `system/modules/work/module.md`. If `enabled: false` → reply "⛔ Module **work** is disabled. Enable it via `/module-toggle work`." and STOP. Do NOT proceed.

---

Record a decision for: $ARGUMENTS

## Steps

1. Create a new note in `Work/<current year>/` named `Decision - [Short Title].md`.

2. Use this template:

```markdown
---
date: [today's date]
tags: [decision-log]
status: accepted
project:
---

# Decision: [Title]

> [!summary] TL;DR
> [One-sentence summary of the decision]

## Context

[What is the problem or situation that requires a decision?]

## Options Considered

### Option A: [Name]
- **Pros**:
- **Cons**:

### Option B: [Name]
- **Pros**:
- **Cons**:

## Decision

**Chosen option**: [Option X]

**Rationale**: [Why this option was selected]

## Consequences

- [Expected outcomes and trade-offs]

## Related

- [[link to relevant project notes]]
```

3. If the arguments include context about the decision, pre-fill the Context, Options, and Decision sections based on what's provided.

4. Report the file path so the user can open it in Obsidian.

## Rules
- Match language to the user's input
- Link to existing Work/ notes where relevant
- Keep the decision framing neutral and factual
- NEVER modify WeRead/

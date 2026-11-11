---
name: practice-review-add
description: >-
  Register a specific algorithm problem, system design exercise, or behavioral
  interview question in the spaced practice review queue.
disable-model-invocation: true
---

<!-- module: practice-review -->
> [!GUARD] Read `system/modules/practice-review/module.md`. If `enabled: false`, tell the user the module is disabled and how to enable it with `/module-toggle practice-review`, then stop.

Register the item identified by `$ARGUMENTS`. For example, `/practice-review-add algorithm 1071`.

1. Read `Learning/Practice/Review/AGENTS.md` and the chosen domain's `Content/<domain>.md`. Resolve the domain and object from the request and conversation. Clarify an ambiguous object before saving it.
2. Prepare the stable ID and a neutral prompt from the user's material or the problem source. Put solution clues and known pitfalls in `review_focus`. Link existing records only when they refer to this object. Prior exposure alone supplies no attempt result or personal reflection.
3. Write `id`, `domain`, `title`, `prompt`, and any `source` and `review_focus` to a temporary JSON file. Run `python3 scripts/practice-review/review.py add --item-file <path>`. Use the returned `created` flag to distinguish a new entry from one already in the queue. Remove the temporary file when the operation is done.
4. Give the item ID and its status. A new item waits for its first recorded attempt. If the user also asked to start, continue through the selected-item procedure in `.agents/skills/practice-review-today/SKILL.md`.

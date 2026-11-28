# SD Blocks Review Content

## Create an item

- Use one building block from `Learning/Practice/System-Design/Blocks.md`. Use `sdb-<block>`, such as `sdb-dealing-with-contention`, where `<block>` is the block's id in the map.
- Use the block's title and the prompt `Review the <title> building block in a fresh scenario.` Each review writes its own scenario, so the item's prompt stays generic.
- The block's points live in `Blocks.md`, not in the item. Each recorded review lists the points it examined and how each was answered, which decides the points the next review examines.
- `practice_finish_round` creates the item with the first recorded attempt, so triage registers nothing before then.

## Reflect after the attempt

Choose one question about this review and ask the learner to answer in English.

- Which point did the scenario hinge on? What made it hard or easy to apply here?
- Which part of your drawing would fail first under more load or a component failure?
- What will you look for in the article before the next review of this block?

## Example

`sdb-dealing-with-contention` points to `[[Design Patterns/Dealing with Contention]]`. One review gives an auction scenario that examines optimistic concurrency control and the high-contention fallback, then asks what changes when retries overload the database.

# System Design Review Content

## Create an item

- Use one design problem that can be reconstructed in a single round. Use `sysd-<slug>`, such as `sysd-url-shortener`. Reuse its original ID across designs for the same problem.
- Put the problem, given scenario, and agreed requirements or scale constraints in `prompt`. Leave architecture choices open.
- Use `review_focus` for requirements, capacity assumptions, key decisions, tradeoffs, or a previously difficult data path. Open previous designs and review focus only after the attempt ends. The `source` may point to the original prompt or related records.

## Reflect after the attempt

Choose one question from this round's design and ask the learner to describe their judgment in English.

- Which requirement or scale assumption drove a key decision? How did it affect the design?
- Which request path hit a bottleneck first? What cost, failure mode, or consistency requirement did you overlook?
- Which assumption most needs validation next round? What numbers, scenario, or diagram would test it?

## Example

The `sysd-url-shortener` prompt asks for a service that creates short links and redirects requests using them. Its `review_focus` can check short-code collisions, the redirect read path, and key capacity assumptions. Preserve references to each design for comparison after the attempt.

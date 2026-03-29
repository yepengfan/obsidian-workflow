## Metadata
* URL: [https://openai.com/index/harness-engineering/](https://openai.com/index/harness-engineering/)
* Author: Ryan Lopopolo
* Publisher: ChatGPT for Education
* Published Date: 2026-02-04
* Tags: 

## Highlights
* Over the past five months, our team has been running an experiment: building and shipping an internal beta of a software product with 0 lines of manually-written code.
* Humans steer. Agents execute.
* To do that, we needed to understand what changes when a software engineering team’s primary job is no longer to write code, but to design environments, specify intent, and build feedback loops that allow Codex agents to do reliable work.
* The lack of hands-on human coding introduced a different kind of engineering work, focused on systems, scaffolding, and leverage.
* When something failed, the fix was almost never “try harder.” Because the only way to make progress was to get Codex to do the work, human engineers always stepped into the task and asked: “what capability is missing, and how do we make it both legible and enforceable for the agent?”
* To drive a PR to completion, we instruct Codex to review its own changes locally, request additional specific agent reviews both locally and in the cloud, respond to any human or agent given feedback, and iterate in a loop until all agent reviewers are satisfied (effectively this is a Ralph Wiggum Loop⁠(opens in a new window)).
* As code throughput increased, our bottleneck became human QA capacity. Because the fixed constraint has been human time and attention, we’ve worked to add more capabilities to the agent by making things like the application UI, logs, and app metrics themselves directly legible to Codex.
* we made the app bootable per git worktree, so Codex could launch and drive one instance per change.
* Context management is one of the biggest challenges in making agents effective at large and complex tasks. One of the earliest lessons we learned was simple: give Codex a map, not a 1,000-page instruction manual.
* AGENTS.md as the encyclopedia, we treat it as the table of contents.
* Architecture documentation⁠(opens in a new window) provides a top-level map of domains and package layering.
* A quality document grades each product domain and architectural layer, tracking gaps over time.
* This enables progressive disclosure: agents start with a small, stable entry point and are taught where to look next, rather than being overwhelmed up front.
* our human engineers’ goal was making it possible for an agent to reason about the full business domain directly from the repository itself.
* From the agent’s point of view, anything it can’t access in-context while running effectively doesn’t exist. Knowledge that lives in Google Docs, chat threads, or people’s heads are not accessible to the system. Repository-local, versioned artifacts (e.g., code, markdown, schemas, executable plans) are all it can see.
* By enforcing invariants, not micromanaging implementations, we let agents ship fast without undermining the foundation. For example, we require Codex to parse data shapes at the boundary⁠(opens in a new window), but are not prescriptive on how that happens (the model seems to like Zod, but we didn’t specify that specific library).
  * **Note**: 边界需要进行数据校验

Next.js 侧用 Zod
Lambda（Python）侧用 Pydantic
数据库侧用 migration + 约束

在 PR 和 CI/CD 里面检查 lint
* The diagram below shows the rule: within each business domain (e.g. App Settings), code can only depend “forward” through a fixed set of layers (Types → Config → Repo → Service → Runtime → UI). Cross-cutting concerns (auth, connectors, telemetry, feature flags) enter through a single explicit interface: Providers. Anything else is disallowed and enforced mechanically.
  * **Note**: 需要实现 一个 importlinter 来检查依赖的顺序，或者看看有什么现成的库在做这件事。
* In practice, we enforce these rules with custom linters and structural tests, plus a small set of “taste invariants.” For example, we statically enforce structured logging, naming conventions for schemas and types, file size limits, and platform-specific reliability requirements with custom lints. Because the lints are custom, we write the error messages to inject remediation instructions into agent context.
* This resembles leading a large engineering platform organization: enforce boundaries centrally, allow autonomy locally.
* You care deeply about boundaries, correctness, and reproducibility. Within those boundaries, you allow teams—or agents—significant freedom in how solutions are expressed.
* Instead, we started encoding what we call “golden principles” directly into the repository and built a recurring cleanup process. These principles are opinionated, mechanical rules that keep the codebase legible and consistent for future agent runs.
* On a regular cadence, we have a set of background Codex tasks that scan for deviations, update quality grades, and open targeted refactoring pull requests.
* This functions like garbage collection. Technical debt is like a high-interest loan: it’s almost always better to pay it down continuously in small increments than to let it compound and tackle it in painful bursts.
* What’s become clear: building software still demands discipline, but the discipline shows up more in the scaffolding rather than the code. The tooling, abstractions, and feedback loops that keep the codebase coherent are increasingly important.
* Our most difficult challenges now center on designing environments, feedback loops, and control systems that help agents accomplish our goal: build and maintain complex, reliable software at scale.

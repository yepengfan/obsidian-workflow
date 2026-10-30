---
name: algo-solve
description: >-
  Algorithm coaching focused on recognizing patterns and matching each pattern
  to suitable solution tools. Guide LeetCode practice,
  review code, and optionally save pattern cards and learning evidence.
disable-model-invocation: true
---

<!-- module: algorithm -->
> [!GUARD] Read `system/modules/algorithm/module.md`. If `enabled: false` → reply "⛔ Module **algorithm** is disabled. Enable it via `/module-toggle algorithm`." and STOP. Do NOT proceed.

Practice problem: $ARGUMENTS

Read `Learning/Practice/Algorithm/AGENTS.md` for storage conventions, guiding heuristics, Python pitfalls, and verification rules. This skill owns the coaching workflow; the module file owns note maintenance.

## Training objective

The two core skills are **recognizing patterns** and **matching those patterns to suitable solution tools**. Problem decomposition and bottleneck analysis support recognition; implementation and review test the match.

Practice this connection through **decompose a problem → recognize a pattern → match its solution tools → implement**. Correct recognition moves the session forward; mistakes and genuine sticking points determine what needs teaching. Do not require the learner to explain a correct choice as proof of understanding.

The default solving path is **brute force → bottleneck and property analysis → pattern recognition → tool selection → optimized solution**. The coach checks whether the proposed pattern and tools fit the problem and its constraints. A concise correct identification is sufficient to proceed; verbal justification, mechanism recitation, and transfer exercises are not prerequisites.

For example: recomputing adjacent range sums → the ranges overlap → maintain the sum by removing and adding the changed elements → fixed-size sliding window. Use this connection to design hints when recognition is missing or incorrect, not as an explanation the learner must supply after a correct answer.

## Adapt to the learner's knowledge

- Establish a viable solution direction privately before designing hints. Confirm the problem and relevant constraints; resolve ambiguous problem identifiers rather than guessing.
- Infer familiarity from the learner's proposed approach, code, and relevant previous practice, not from whether this exact problem has been solved before. A new problem may combine familiar mechanisms, and familiarity may differ across its parts.
- Discover cards and logs with `rg --files --no-ignore` under `Learning/Practice/Algorithm/`. Read only relevant cards' recognition/mechanism sections and relevant log entries. A card's existence or a solved problem is evidence of exposure, not proof of mastery. Missing history is not proof that the tool is unknown.
- Use current conversation evidence first. If familiarity is unclear and changes the next teaching step, ask a short question about that mechanism; do not introduce a mandatory intake questionnaire, ability score, or fixed learner level.
- **Unfamiliar mechanism**: Teach the necessary concept and demonstrate a small example, then ask the learner to apply it to this problem. Not knowing an unseen technique is normal; do not make them guess knowledge they have not learned.
- **Familiar mechanism, missing connection**: Leave decomposition and matching to the learner. Point to the concrete bottleneck, relationship, or required operation before naming the tool.
- **Correct recognition and tool match**: Check applicability privately, briefly confirm, and invite implementation. Do not ask why the choice works, demand a walkthrough or proof, or supply unsolicited scaffolding. Skip baseline and derivation steps already resolved by the valid approach. If code is provided, enter code review.
- **Incorrect recognition or unsuitable tool**: Identify the specific mismatch and show the condition or a small counterexample that breaks it. Guide the learner toward the missing structure or capability. Diagnose this actual error rather than testing unrelated knowledge.
- **Ambiguous proposal**: Ask only the detail needed to judge applicability. A broad label such as "two pointers" may need an operational clarification; do not use ambiguity as a reason to demand justification for an otherwise clear, correct approach.
- **Correct pattern, implementation bug**: Keep the recognition result intact. Diagnose pointer movement, boundaries, state updates, or other implementation errors separately; do not reopen pattern recognition unless the bug exposes an actual conceptual mismatch.
- When prior logs show a connection that previously needed help, give the learner an opportunity to make it independently this time. Do not reveal the recorded hint or target pattern before that attempt. Treat historical observations as provisional and adapt to today's response.

## Guide the solution

### Establish a correct baseline

Use this baseline route when the learner has not already identified a viable approach. Translate the story into concrete objects, relations, constraints, and operations. Ask the learner for the most direct correct enumeration and how each candidate is evaluated. A verbal explanation and small walkthrough suffice; brute-force code is optional.

Check correctness and derive complexity from both the candidate count and per-candidate work. If the learner cannot construct a baseline, demonstrate one candidate on a tiny input and let them continue. Use constraints to assess feasibility, not to choose an algorithm from input size alone. If the direct solution is appropriate, explain why without forcing an optimization.

### Recognize structure and match tools

When recognition or tool matching is missing or incorrect, start from a specific baseline operation and help the learner identify repeated work, reusable information, eliminable candidates, or subproblem structure. Address one conceptual connection at a time:

- What relationship or operation remains after decomposing the problem or fixing one variable?
- What capability is needed, such as historical lookup, range aggregation, or combining child results?
- Which known tool provides it, and which problem properties justify using it?

Use these as coaching decisions, not a questionnaire to recite. For composite solutions, let the learner decompose familiar parts and teach unfamiliar parts as needed. Validate other correct approaches rather than forcing the coach's initial choice. For an invalid approach, supply a concrete failure condition or counterexample.

Once the learner correctly identifies the pattern and suitable tools, briefly confirm and move to implementation. Do not require exact terminology when their description is clear. When the mechanism is unfamiliar or the learner requests direction, name and explain it directly. Avoid testing terminology or presenting a menu of algorithms. Compare a nearby pattern only when it resolves a real ambiguity, such as why negative values invalidate a sum-based sliding-window elimination rule.

### Derive and verify the optimized solution

Use guided derivation only when the learner is stuck, has made a relevant error, or requests help. Guide the current gap in state meaning, invariants, updates, or answer extraction. Explain local mechanisms when needed; do not expect the learner to derive an entire algorithm from its name.

Check correctness and boundaries yourself. Use examples and comparisons with brute force to resolve the demonstrated gap; do not turn them into a mandatory learner explanation before implementation.

### Keep hints responsive

During active guidance, acknowledge or correct the specific gap and ask one focused question, then wait. After a correct identification, a brief confirmation and invitation to implement is enough; not every turn needs a question. A useful progression is **point to an operation → expose its structure with an example → connect to a known mechanism → explain directly when needed**. This is not a fixed hint ladder or turn quota; skip to teaching when a prerequisite is missing.

For a learner familiar with hash tables but missing the connection in Two Sum:

> With the current number x fixed, what value would we need to find among earlier numbers?

If they identify `target - x`, let them connect that lookup to a tool. If hash tables are unfamiliar, explain membership lookup and demonstrate a small example before asking them to apply it. If they already describe a correct hash-based solution, verify it and proceed.

When the learner is confused, summarize what is established, explain the missing connection concretely, then ask a smaller application question. If a concrete hint does not resolve the gap, teach the mechanism rather than rephrasing the same question. Avoid vague prompts such as "Can this be optimized?" or "Think of a data structure."

Complete pseudocode requires an explicit request or acceptance of an offer. Complete code requires an explicit request or the learner saying they give up. Do not ask again after such a request. "I'm stuck" calls for concrete explanation first, not an automatic full solution.

## Review code and diagnose errors

When code is provided, review correctness, relevant edge cases, complexity, and Python style using the module's pitfalls and verification rules. For a bug, identify the specific line, reproduce the failure with a concrete input when possible, and explain a targeted correction; do not rewrite the solution. Compare with an optimal approach conceptually, providing code only when requested.

After the solution is correct, report the review result and complexity, then proceed to the optional saving step. Do not add a default recap quiz, ask the learner to explain why a correct tool works, or require a variation to prove transfer. Explain further when the learner requests it or a demonstrated error remains unresolved.

Record whether recognition was correct independently, corrected after feedback, or reached through hints/teaching. Keep implementation errors separate. Absence of a verbal explanation is not evidence of a recognition gap; do not withhold credit for a correct identification because the learner did not justify it. If recognition was not observed (for example, only code was supplied), record that without demanding a retrospective explanation.

### Example: correct recognition followed by an implementation error

For Swap Nodes in Pairs, the learner says "reverse every two nodes." This is a correct operational identification. Respond briefly, for example: "对，每两个节点做局部反转。按这个思路实现吧。" Do not first require them to explain dummy nodes or draw every pointer change.

If their implementation later increments a counter without advancing the pointer, show the failing input and the mismatched counter/pointer positions. Treat it as an implementation bug, not failed pattern recognition. Once corrected, confirm the fix and finish review without a recognition quiz.

## Save learning evidence after one confirmation

After review passes, classify before asking whether to save:

1. Summarize the actual solution pattern and recognition cues, grounded in the learner's proposed approach and code.
2. Scan existing pattern titles and relevant frontmatter, `Key Insight`, and `Composed Of` sections to decide whether to update a card or create one. Follow the module's Pattern Card Rules; do not force a new card merely because the problem is new.
3. Name the proposed card and briefly explain the classification. Ask once whether to save that classification to the card and daily log, explicitly stating when a new card will be created.

Confirmation (including "go" or its equivalent) authorizes classification and saving together. If the learner already explicitly requested saving, state the classification and proceed without asking again. Resolve a requested classification change before writing. A refusal ends the session without vault writes.

When saving, follow the module's Pattern, Atom, and Log Rules:

- Use the session date as the solve date unless the learner already specified another date. Note `created` / `updated` dates refer to the saving session.
- Reuse the classification scan. Read the selected card in full before updating, or create it from `Templates/Algorithm Pattern.md` with the next ID.
- Keep general knowledge in cards: recognition cues, the required capability, the tool's mechanism, and applicability limits. Add only insights this session contributes, not a transcript or personal ability judgment.
- Keep personal learning evidence in the daily log: the recognition outcome, any actual recognition/tool-selection error, any separate implementation error, and the feedback that resolved it. Record follow-up practice only for an observed gap. Do not invent a missing explanation or require reflection to fill log fields. Use "none observed" or "not observed" as appropriate. The result emoji describes the solution outcome, not a permanent ability rating.
- Append the problem to the card and daily log using existing metadata conventions. Use `Templates/Algorithm Log.md` for new logs. Preserve existing entries and avoid duplicate problem records when updating the same session.
- Check for reusable atoms using the module's granularity criteria. Keep taxonomy work out of the coaching conversation unless it affects the learner's understanding or requires a classification decision.

Preserve the existing pattern/atom/log organization and dashboard metadata. Add relevant sections as needed to cards touched by the session; do not bulk-migrate historical notes or leave template guidance/placeholders in finished notes.

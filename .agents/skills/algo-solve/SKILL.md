---
name: algo-solve
description: >-
  Pattern-oriented LeetCode coaching: connect problem features to reusable
  solution patterns, review code, and optionally save pattern cards and logs.
  Use when the user wants to solve a LeetCode problem, practice algorithms,
  or says /algo-solve.
disable-model-invocation: true
---

<!-- module: algorithm -->
> [!GUARD] Read `system/modules/algorithm/module.md`. If `enabled: false` → reply "⛔ Module **algorithm** is disabled. Enable it via `/module-toggle algorithm`." and STOP. Do NOT proceed.

Solve LeetCode problem: $ARGUMENTS

Read `Learning/Practice/Algorithm/CLAUDE.md` for module instructions.

## Phase 1 - Recognize solution patterns from the problem

Default flow: **Brute-force solution → Analyze bottlenecks and problem properties → Identify the pattern → Derive an optimized solution**. Help the learner understand how a pattern follows from a straightforward solution so they can recognize the same structure next time. Pattern names organize knowledge: guessing a name does not demonstrate understanding, and naming a pattern does not reveal the complete solution.

### Establish a direction before coaching

- Confirm the problem and its key constraints. Resolve missing information rather than guessing from an ambiguous problem number.
- Identify a viable target pattern and why it applies before designing the next question. Each hint should connect the learner's existing understanding to that mechanism; do not use generic questions to explore a direction you have not established yourself.
- Refer to the module's Guiding Heuristics. When connecting to existing knowledge, use `rg --files --no-ignore Learning/Practice/Algorithm/Patterns` to find cards and read only the relevant `Key Insight` / `Trigger` sections. Do not preload every template or expose solutions. Use cards for consistent terminology and analogies, without forcing a problem into an existing category.
- Start new problems with brute force by default, without naming the optimization pattern immediately. Do not repeat work the learner has already provided: analyze bottlenecks if they have a baseline, check the connection to brute force if they have an optimized approach, and enter Phase 2 if they paste code.

### A. Establish a brute-force baseline

- Translate the story into concrete objects and operations, such as counting index pairs satisfying a relation, repeatedly querying contiguous range sums, or combining information from child subtrees. Ask only about unresolved details that affect the solution.
- Ask the learner to describe the most direct correct approach: which candidates to enumerate, how to check or evaluate each candidate, and how to obtain the answer. A verbal explanation and a small walkthrough are sufficient; writing brute-force code is not required.
- Analyze time and space complexity from the actual operations. Distinguish the number of candidates from the cost of processing each candidate. Establish correctness before optimizing.
- If the learner cannot find a brute-force approach, demonstrate how to enumerate one candidate on a tiny input, then let them continue. First establish a baseline they can understand.

### B. Analyze bottlenecks and problem properties to identify a pattern

- Find optimization opportunities in specific brute-force operations: repeated scans, recomputed information, or candidates that might not need enumeration. Use overlap, ordering, monotonicity, relationships, or subproblem structure to explain what can be reused or eliminated and why.
- Use constraints to assess whether the baseline is feasible, not to choose an algorithm from `n` alone. If the direct solution is already appropriate, explain why rather than inventing an optimization to fit a pattern.
- Address one conceptual connection per turn. Starting from the current bottleneck, state the capability needed and ask a concrete, answerable question. For example: "With the current number x fixed, we only need to know whether target-x appeared earlier. What kind of query do we need to support?"
- You may name the pattern directly, explaining in one or two sentences **which problem property matches it and which repeated work it removes**. If the pattern is unfamiliar, the learner explicitly asks for direction, or they are confused, explain this connection directly and then let them apply it. Do not keep testing terminology.
- Once the learner recognizes the core mechanism, name and summarize the pattern before applying it to the problem. Do not withhold its name until the complete solution or code review.
- Pair names with mechanisms. Do not stop at "this is DP" or "try a monotonic stack"; explain which subproblems can be reused or which candidates can be permanently discarded. For composite solutions, identify the main bottleneck first and introduce additional techniques one at a time.
- Check applicability: contiguous ranges do not automatically imply sliding windows, and optimization objectives do not automatically imply greedy algorithms. When confusion is likely, compare one nearby pattern using problem conditions or a small counterexample. Avoid presenting a menu of algorithms.
- If the learner proposes another viable approach, validate that approach. Do not reject a correct solution to force the predetermined pattern. For an invalid approach, give a specific failure condition or counterexample, then connect it to the missing capability.

### C. Derive an optimized solution using the pattern

- Address the current gap by guiding the learner to define state semantics, invariants, updates or transitions, and how the answer is produced. Resolve one point at a time instead of presenting the entire checklist.
- You may explain a local mechanism, provide a key relationship, or demonstrate one state change before asking the learner to derive the next step. Do not merely name an algorithm and expect them to produce all its steps unaided.
- Once the learner can explain the solution and why it works, verify it with a boundary case or small example. Compare it with brute force: explain which work was removed, why no solutions are missed, and how complexity changes. Then enter Phase 2.
- Close with two or three sentences connecting the recognition cues, the pattern's mechanism, and its applicability limits. Establish the pattern during problem solving, rather than revealing it only when saving notes.

### Turn structure and handling confusion

- Usually confirm or correct a specific part of the learner's response, state the next small objective, and ask one focused question. Wait for their answer. Describe the current focus naturally rather than mechanically labeling hint levels.
- Questions should practice knowledge the learner already has or has just been taught. Direct explanation is allowed. Avoid vague prompts such as "Can this be optimized?", "Can we trade space for time?", or "Think of a data structure" without a concrete object or direction. Do not hide the answer in a chain of rhetorical questions.
- When the learner says they are confused, do not understand, or do not know, immediately become more concrete: summarize what is established, identify the missing connection, explain the concept or demonstrate a small example, then ask a smaller application question. Do not rephrase the same hint or ask them to keep guessing.
- If one concrete hint does not resolve a connection, explicitly explain the mechanism and how it relates to the problem. If confusion persists, check prerequisites and simplify the example instead of waiting for a fixed three-turn threshold.
- Provide complete pseudocode only when explicitly requested or when the learner accepts an offer. Do not ask for confirmation again after an explicit request. Saying "I'm stuck" first triggers the explanation above. Provide complete code only when the learner explicitly asks for it or says they give up.

### Hint examples (illustrating scope, not fixed scripts)

**Starting a maximum-sum problem with fixed-length ranges:**
"Let's start with the direct approach: if you check every contiguous range of length k, how would you calculate each range's sum and obtain the answer from those results?"
Wait for their explanation, then analyze the number of ranges and the cost of each sum before examining the bottleneck below.

**The learner proposes recomputing the sum of each range:**
"Your enumeration covers all ranges; the repeated work is in summation. Compare two adjacent ranges of length 3: `[2, 1, 5]` and `[1, 5, 3]`. Given that the first sum is 8, how could you obtain the next sum by processing only the elements that change?"

**The learner still does not understand:**
"Both ranges retain 1 and 5; only 2 leaves and 3 enters, so the next sum is `8 - 2 + 3`. This is a fixed-size sliding window: reuse the aggregate over the overlapping portion. If the current range has indices `[l, r]`, which indices leave and enter when it moves one position to the right?"

**The learner suggests sliding windows because the problem involves contiguous subarrays, but negative numbers are allowed and the goal is to count ranges summing to k:**
"First check the sliding-window assumption: with negative numbers, extending the right endpoint can decrease the sum, so a sum greater than k does not justify discarding the left endpoint. We need a representation of range sums that does not rely on this monotonicity. Consider `[2, -1, 3]`: the full prefix sums to 4. If we subtract the sum of prefix `[2]`, which range's sum remains?"
Once the learner understands that a range sum is the difference of two prefix sums, connect that to fixing the right endpoint and querying the required historical prefix sum, then to hash-based counting. Do not reveal the entire solution at once.

## Phase 2 - Code review

1. The learner shares their code.
2. Review the following:
   - **Correctness**: Check the logic. When scripted verification is needed (exhaustive tests, randomized stress tests, edge cases, performance checks, or reproducing pitfalls), combine the checks into one script invocation rather than multiple rounds. See Efficiency Rules in `Learning/Practice/Algorithm/CLAUDE.md`.
   - **Edge cases**: Empty input, a single element, maximum values, negative numbers, and other relevant cases.
   - **Complexity**: Analyze time and space using Big-O notation.
   - **Code style**: Apply Python 3 best practices and consult the Python pitfalls checklist in `Learning/Practice/Algorithm/CLAUDE.md`.
3. If there is a bug, identify the specific line and explain the cause. **Do not rewrite the solution.**
4. Compare the approach with an optimal solution. Prioritize concepts; provide code only when requested.
5. After the code passes review, **classify before asking whether to save**:
   - Summarize the actual solution pattern and its recognition cues in one sentence, grounding the explanation in the learner's code.
   - Read the frontmatter and `## Key Insight` of every file in `Learning/Practice/Algorithm/Patterns/`, plus `## Composed Of` when present. Do not read Template/Gotchas/Problems for classification; see Efficiency Rules in `Learning/Practice/Algorithm/CLAUDE.md`.
   - Decide whether to update an existing pattern or create a new one. State the specific card title and briefly explain the classification.
   - Ask **one combined confirmation**, for example: "I recommend updating the existing pattern card X. Would you like to save this classification to the pattern card and daily log?" For a new card, explicitly say it will be created.
   - **Yes** (including "go" or an equivalent confirmation in the learner's language) → Enter Phase 3 and save using the proposed classification. This confirms both classification and saving; do not ask for classification approval again.
   - **No** → End the session without writing any vault files.
   - If the learner requests a different classification, resolve that change before saving. Do not ask whether to save before completing the classification check.

## Phase 3 - Save notes (only after user confirmation)

**On entering Phase 3, immediately use `TodoWrite` to create the following task list (`merge: false`) before proceeding:**

```text
1. Determine the solve date
2. Use the classification confirmed in Phase 2 (create or update)
3. Write the pattern card
4. Write the log
5. Check for reusable atoms
```

1. **Determine the solve date** (`YYYY-MM-DD`):
   - **Default to the current session date** without asking.
   - Use a different date only if the learner has **already** specified one, such as "solved yesterday" or "backfill 2026-08-19". Otherwise, use today.
   - Use this solve date in the pattern's Problems table and the log filename.

2. **Use the confirmed pattern classification**:
   - Reuse the classification and card scan completed in Phase 2. Do not repeat the scan or ask for another classification confirmation.
   - Read the selected existing card in full before updating it, or use the pattern template when creating the confirmed new card.

3. **Update an existing pattern**:
   - Append the problem number to the frontmatter `problems` array.
   - Add a row to the Problems table with the number, name, difficulty, and solve date from step 1.
   - Set the frontmatter `updated` field to today.
   - Append any newly discovered pitfalls to the Gotchas section.

4. **Create a new pattern**:
   - Use `Templates/Algorithm Pattern.md`.
   - For `id`, read all existing card IDs and use the maximum plus one.
   - Populate title, category, tags, problems, Key Insight, Trigger (when applicable), Composed Of (see step 6 for applicability), Template, and Gotchas.
   - Add the first Problems table row with the number, name, difficulty, and solve date from step 1.
   - Set frontmatter `created` / `updated` to the current note-saving session date (today). Distinguish these from the Problems table's Date column, which records the solve date.
   - Assess `difficulty` based on the pattern's complexity.

5. **Write the log**:
   - Check whether `Learning/Practice/Algorithm/Log/{solve-date}.md` exists, using the solve date from step 1.
   - If absent, create it from `Templates/Algorithm Log.md`, set frontmatter `date` to the solve date, and add the first entry.
   - If present, append a new `##` section and update the frontmatter `problems_solved` array.
   - Include the pattern wikilink, difficulty, result emoji, notes, and complexity.

6. **Check for opportunities to extract reusable atoms** (see Atom Card Rules in `Learning/Practice/Algorithm/CLAUDE.md` for granularity criteria):
   - Use `Glob` to list all filenames in `Atoms/` (each filename is the atom title; see the naming convention in CLAUDE.md) and `Patterns/`. Do not use shell globs; see the first Pattern Card Rule for the rationale.
   - Read each pattern card's `## Key Insight` and, when present, `## Composed Of`. Read only these sections rather than Gotchas/Template/Problems to avoid unnecessary work.
   - If an existing atom covers the core mechanism of the current pattern, add or verify its `## Composed Of` link and set that atom's frontmatter `updated` field to today.
   - If a reusable technique appears in both the current card and at least one **other existing pattern card's** Key Insight, but has no corresponding atom, create an atom card and add `## Composed Of` links to both patterns. Consider all existing patterns, not only those otherwise involved in this session.
   - If unsure whether a technique is an atom rather than an implementation detail, default to skipping extraction. Prefer temporarily missing an opportunity over creating an overly granular atom that will need to be removed later.
   - If none of the above applies and this session created a new pattern from the template in step 4, remove its empty `## Composed Of` section and placeholder comment. Do not leave unfilled template placeholders in the card.

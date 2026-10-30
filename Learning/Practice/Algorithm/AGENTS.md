# Algorithm Module - Agent Instructions

> Inherit the general conventions from the vault root AGENTS.md.

## Directory Configuration

| Path | Purpose |
|------|---------|
| `Learning/Practice/Algorithm/Patterns/` | Pattern cards, one Markdown file per pattern |
| `Learning/Practice/Algorithm/Atoms/` | Reusable techniques shared across patterns, one Markdown file per atom |
| `Learning/Practice/Algorithm/Log/` | Daily problem-solving logs |
| `Learning/Practice/Algorithm/Legacy/` | Original files from before migration, for read-only reference |
| `Learning/Practice/Algorithm/00_index.md` | Dataview dashboard |
| `Templates/Algorithm Pattern.md` | Template for new pattern cards |
| `Templates/Algorithm Log.md` | Template for new logs |
| `Templates/Algorithm Atom.md` | Template for new atom cards |

## Coaching and Learning Evidence

`.agents/skills/algo-solve/SKILL.md` is authoritative for the solving flow, adaptive hints, code review, error diagnosis, and saving authorization. The core training goal is recognizing patterns and matching them to corresponding solution tools. Decomposition and bottleneck analysis support these two skills. This file owns storage conventions and supporting technical guidance.

- Pattern cards store general recognition cues, mechanisms, tool-selection reasoning, and applicability limits. Atom cards explain independently reusable tools or techniques.
- Correct pattern recognition and tool matching need only brief confirmation before implementation. Teach through actual mistakes or sticking points; do not require explanations of correct choices.
- Logs separate recognition outcomes, recognition/tool-selection errors, and implementation errors. Record effective feedback and follow-up only for observed gaps. A concise correct identification counts as correct recognition without a verbal justification.
- During coaching, read relevant history only. Do not bulk-migrate old notes to new templates; add useful sections to a card when the current session contributes relevant knowledge.

## Guiding Heuristics

Use the following principles during coaching and code review.

### Pattern Recognition Framework

These cues help the coach identify mechanisms. Ground them in the specific problem before turning them into hints; do not present them as generic questions.

1. **Repeated work**: Locate the specific information recomputed by brute force and determine whether it can be reused across candidates.
2. **Fix one endpoint**: After fixing one variable in a multivariable relationship, determine whether the remaining task is lookup, counting, finding an extremum, or solving a subproblem. Connect that operation to a suitable pattern.
3. **Required operations**: Choose data structures from the required queries and updates, then verify that their maintained information is sufficient to produce the answer.
4. **Constraints and applicability**: Use input size to assess complexity and data properties to validate the mechanism. Sliding-window advancement, binary-search monotonicity, and greedy-choice correctness each require their own justification; input size or problem keywords alone do not establish them.

### Core Principles

- **BST inorder traversal produces sorted order**: Consider inorder traversal for operations involving adjacent values, sorting, or the kth smallest value.
- **Traversal choice**: Inorder for BST ordering, preorder for top-down propagation, and postorder for bottom-up aggregation.
- **Recursive DFS return semantics**: Parameters carry per-call state. Use a closure with `nonlocal` for a shared answer when the answer through the current node differs from the value returned to its parent.
- **Loop complexity is not just the iteration count**: Include the operations inside the loop.
- **`bisect_left/right` returns an index in `[0, len(arr)]`**: Python's `arr[-1]` silently accesses the last element, which can hide off-by-one errors.
- **Simplify geometry in grid simulations**: For rotation plus gravity, apply gravity in the corresponding direction on the original grid, then rotate.

### Python Pitfalls (check during code review)

- `[[0]*n]*m` shares references to the same row.
- Class variables can leak state between tests; use `nonlocal` or instance variables as appropriate.
- `arr[-1]` silently performs negative indexing.
- Distinguish `is` from `==`: use equality comparison for values or structural equality, not identity comparison.
- `.sort()` returns `None`.
- Returning from one recursive frame does not stop the entire recursion.

## Efficiency Rules

Tool round trips are the main source of overhead; script execution itself is usually under one second. During code verification and note retrieval, reduce unnecessary round trips as follows.

- **Combine verification scripts**: Run exhaustive tests, randomized stress tests, edge cases, performance measurements, and reproductions of pitfalls (such as comparing different update orders) in one invocation when they fit in the same script. Make another call only when an unexpected result requires targeted follow-up.
- **Do not repeat full validation for a pure refactor**: If only names or code structure change and the logic is unchanged, such as replacing `b`/`l` with meaningful names, a few hundred random spot checks for equivalence are sufficient. Do not repeat exhaustive or large-scale stress testing of correctness already established.
- **Read only necessary pattern/atom sections**: For classification, read frontmatter and `## Key Insight`, plus `## Composed Of` when present. Do not read `## Template`, `## Gotchas`, or `## Problems` merely to determine whether two cards describe the same technique. Read a specific card in full once it is selected for an update or reference.
- **Avoid bare `cd`**: In shell tools that preserve the working directory across calls, changing it can redirect subsequent relative paths, including those used by file-reading tools. Use absolute paths or a subshell such as `(cd dir && cmd)` to keep the directory change local to that invocation.

## Pattern Card Rules

- **Check existing patterns before classifying**: Use `rg --files --no-ignore Learning/Practice/Algorithm/Patterns` to list filenames, including gitignored notes. Quote individual file paths when reading them. Scan names for a matching pattern; when uncertain, read frontmatter, `## Key Insight`, and `## Composed Of` when present. Do not read Template/Gotchas/Problems for this decision; see Efficiency Rules. **Never skip this check and create a new card immediately.**
- **Existing pattern**: Preserve existing content and add only new recognition cues, tool-selection reasoning, applicability limits, or pitfalls from this session. Do not duplicate an existing problem record when updating the same session. Add the problem number to frontmatter `problems[]`, add a Problems table row with the solve date (defaulting to the current session date), and update `updated`.
- **New pattern**: Create a file from `Templates/Algorithm Pattern.md`, assign the highest existing ID plus one, and populate all fields. Set `created` / `updated` to the saving session date and assess `difficulty` from the pattern's complexity. Use the solve date in the first Problems table row as well.
- **Card content**: `Key Insight` explains the reusable mechanism and the work it avoids; `Trigger` connects structural cues to required operations and a suitable tool; `Applicability` explains preconditions and useful failure boundaries. These describe general knowledge, not the learner's performance. Keep existing cards readable without requiring all new sections.
- `difficulty` describes how difficult the pattern is to understand, not the difficulty of an individual problem.
- Use the pattern title as the filename, removing filesystem-invalid characters: `/ \ : * ? " < > |`.
- Use tags in the form `[leetcode/pattern, leetcode/{category-slug}]`.
- When saving notes, determine whether the pattern combines more fundamental reusable techniques. Follow Atom Card Rules and add `## Composed Of` when appropriate.

## Atom Card Rules

**Why extract atoms**: The number of patterns can grow combinatorially as problems combine basic techniques, while the underlying algorithmic and structural techniques are fewer and grow more slowly. Separate atom cards allow these techniques to be reused and indexed across patterns and categories instead of repeating the same explanation in many cards.

**Granularity criteria** (check carefully; this is a common source of mistakes):

- **An atom** is an algorithmic or structural technique that can be taught independently and recognized across unrelated problems or categories. Examples include postorder bottom-up aggregation, top-down constraint propagation, monotonic stack/queue maintenance, three-pointer iterative reversal, dummy sentinel nodes, modifying and restoring state in backtracking, binary search for predecessors/successors, Union-Find, and Floyd's slow/fast pointers. An experienced learner should recognize the technique from a standalone explanation that does not mention a specific problem.
- **An implementation detail is not an atom**: Particular coding choices, conventions, and pitfalls do not necessarily constitute independently teachable techniques. Examples include forward versus backward iteration for space-optimized DP, choosing 0 versus positive/negative infinity as a sentinel, simultaneously updating two variables with tuple assignment, and Python recursion-depth limits. Keep these in the pattern's Gotchas section even if similar wording appears in several cards. A previous extraction mistakenly treated such details as atoms and had to be undone.

**Rule of thumb**: If explaining the extracted technique still requires naming the specific problem, it is a detail within a pattern. If the technique can be fully explained without a particular problem, it may qualify as an atom.

**When and how to extract** (in this order):

- **Timing**: Do not design a taxonomy in advance. After saving is authorized, extract or reuse atoms when the current pattern's core mechanism overlaps an existing atom or clearly combines independently nameable techniques.
- **Compare across the full collection each time notes are saved**: Do not limit the comparison to cards already involved in the session. Use `rg --files --no-ignore` to discover gitignored notes. First scan all titles in `Atoms/` for directly reusable atoms, then scan every pattern's Key Insight to find techniques that recur elsewhere without a corresponding atom. Atoms are intended to remain a small, slowly growing collection; read the relevant insight sections rather than skipping the comparison.
- **Extract only demonstrated reuse**: Create a new atom when the current pattern and at least one other existing pattern share the independently teachable technique. Link both patterns to it. If an existing atom already covers the mechanism, reuse it instead. Remove an empty `Composed Of` section from a newly created card when no atom applies.
- **Skip extraction when granularity is uncertain**: After the full comparison, if it is still unclear whether the technique is independently teachable, do not create an atom. An incorrect extraction that must later be undone costs more than temporarily missing an opportunity.

**Creating and referencing atoms**:

- **Create an atom** from `Templates/Algorithm Atom.md`. Its `title` describes the technique itself without naming a particular problem. Do not set `category`; atoms should be reusable across categories.
- **Tags**: Use `[leetcode/atom]` or `[leetcode/atom, leetcode/{related-domain}]`. An optional domain tag such as `leetcode/tree` or `leetcode/array` can help browsing without imposing a required classification. For a technique spanning several domains, such as binary search used in both DP and BST problems, `leetcode/atom` alone is sufficient. This is compatible with omitting `category`: that field would impose a single classification, whereas a domain tag is only a browsing aid.
- **Filename equals atom title**: Remove filesystem-invalid characters `/ \ : * ? " < > |` and ensure the filename stem exactly matches frontmatter `title`. A mismatch can prevent filenames returned by `rg --files --no-ignore` from matching pattern wikilinks, silently causing broken links or missed matches.
- **Frontmatter `type: atom`**: This follows the vault's use of `type` in module manifests, essays, and other notes. Current Dataview queries filter by the `#leetcode/atom` tag; `type` is reserved for possible future use and does not currently drive these queries.
- **Backlinks require no manual maintenance**: The atom's Used By section renders `dv.current().file.inlinks`. A pattern linking to `[[atom title]]` appears automatically; do not maintain a separate list that could become stale.
- **Maintain `updated` manually**: As with pattern cards, when another pattern adds a reference to an existing atom, set that atom's frontmatter `updated` to today. Unlike Used By, this date is not computed automatically; stale dates undermine sorting by least recently updated.
- **Reference atoms from patterns**: Add `## Composed Of` after `## Key Insight`. List each atom and explain in one sentence how it is used in this pattern. Include the specific role in the combination, not just a bare link.
- **Composed Of is optional**: If a pattern is already at the smallest useful granularity and has no more fundamental reusable techniques, omit the section or state that the card is already atomic and needs no further decomposition.
- **`## Template` is optional**: Include it only when the atom has a clear, directly reusable code skeleton. Conceptual or design-oriented atoms may leave it empty or remove the section.

## Log Rules

- Use one `##` section per problem.
- Include a pattern wikilink `[[pattern name]]`, difficulty, result emoji, notes, and complexity. Result describes the solution outcome, not mastery.
- Use the fields in `Templates/Algorithm Log.md`: recognition outcome, recognition/tool-selection error, implementation error, effective support, and optional follow-up for an observed gap. Do not mark correct recognition as uncertain merely because no explanation was requested or given. If only code was reviewed, recognition may be "not observed"; do not invent a coaching history or quiz the learner to fill the log.
- Keep each field concise. Use "none observed" or "not observed" as appropriate, and remove template guidance comments from finished notes. Existing entries need no migration.
- Keep frontmatter `problems_solved` consistent with the body sections.
- Use `YYYY-MM-DD.md` as the filename, based on the **solve date**.
- Default the solve date to the current session date **without asking**. Use another date only if the learner has already specified one.
- If the daily log already exists, append a section without overwriting it.

## Category Values

Valid category values, matching the Dataview grouping keys:

- Array
- Linked List
- Binary Tree — Traversal
- Binary Tree — Recursion
- BST
- Graph
- DP
- Data Structure
- Backtracking
- String
- Enumeration
- Bit Manipulation

Add new categories when needed, but prefer existing categories.

## Language

- Use English for technical discussion by default; reply in Chinese when the learner uses Chinese.
- Always use clean, readable Python 3 code.
- Follow the vault's existing style when mixing English and Chinese in notes.

## Do NOT

- Do not proactively provide complete code unless explicitly requested.
- Do not rewrite the learner's code; make targeted fixes only.
- Do not delete or modify files in `Legacy/`.

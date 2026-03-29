## Metadata
* URL: [https://kiro.dev/blog/bug-fix-paradox/](https://kiro.dev/blog/bug-fix-paradox/)
* Author: nslog
* Publisher: kiro.dev
* Published Date: 2026-02-19
* Tags: 

## Highlights
* Kiro’s bug-fixing workflow to make that boundary explicit
* property-aware code evolution
* Every bug fix has a dual intent: fix the buggy behavior, preserve everything else. That intent partitions the input space, but the partition usually stays implicit. We can make it explicit and testable.
* Every experienced engineer reasons about C, often implicitly. But without C as an explicit, shared artifact, there's no guarantee the agent’s boundary matches yours.
* The agent drifts from the boundary
* The agent invents a boundary
* The agent can’t check that it respected the boundary
* C draws the boundary
* The postcondition P fills that gap: it defines what the code should do for inputs where C holds
* Without P, the agent can suppress the error with a try/except and call it fixed. P forces it to align with what correct means.
* Fix and preservation properties
* Fix property (C ⟹ P): When C holds, the patched code satisfies P.
* Preservation property (not C ⟹ unchanged): When C doesn't hold, the patched code behaves identically to the original.
* Bugfix doc
* Current Behavior (Defect) 1.1 WHEN deleting a node with two children AND the right child has no left subtree THEN the system crashes with AttributeError: 'NoneType' object has no attribute 'left' Expected Behavior (Correct) 2.1 WHEN deleting a node with two children AND the right child has no left subtree THEN the system SHALL successfully delete the node by replacing it with the right child's value Unchanged Behavior (Regression Prevention) 3.1 WHEN deleting a node with two children AND the right child has a left subtree THEN the system SHALL CONTINUE TO find the minimum value in the right subtree and replace the deleted node 3.2 WHEN deleting a leaf node or a node with one child THEN the system SHALL CONTINUE TO remove the node and return None](https://media.getmatter.app/media/article_images/2026/02/20/306d043a4a4b010e2777fbe9e58a8a10.3294x1864.png) This mirrors the partition defined by the bug condition C. Defect and fix requirements target buggy inputs. Preservation requirements identify specific behaviors that must not change.
* Design: bug condition and root cause hypothesis
* The task plan: testing the hypothesis
* With property-aware code evolution, you and Kiro work from the same contract. Kiro drafts the boundary and the hypothesis. You can push back, redraw, tighten the scope, or ask for a different approach. By the time code is written, you’ve both agreed on what changes and what doesn’t.

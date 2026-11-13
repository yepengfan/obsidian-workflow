# Algorithm Review Content

## Create an item

- Use one algorithm problem that can be independently reimplemented as the review unit. For LeetCode use `lc-<number>`, such as `lc-1071`. For other sources use a distinct, stable lowercase hyphenated ID. Reuse the original ID for later attempts at the same problem.
- Put the verified problem statement, inputs and outputs, necessary constraints, and public examples in `prompt`. Keep the wording neutral so the learner can identify the approach independently.
- Store the original problem URL in `source`. For LeetCode use a verified direct problem link, such as `https://leetcode.com/problems/greatest-common-divisor-of-strings/`.
- Use `review_focus` for recognition cues, tool selection, boundaries, or sticking points supported by previous evidence. Open it and past solutions after the attempt.

## Start a review

- Display a clickable LeetCode link alongside the title, such as `[LC 1071 - Greatest Common Divisor of Strings](https://leetcode.com/problems/greatest-common-divisor-of-strings/)`. This applies to both automatically started `/practice` reviews and selected `/practice-review-today` items.
- Prefer the `source` returned by `show <id>`. If an older item lacks a link, find and verify the official URL from its confirmed number or title before displaying it. Do not guess the slug or open solutions and previous submissions.
- Ask the learner to solve independently on LeetCode, then paste their code and actual time into the conversation. Keep the neutral prompt and agreed time limit; do not require them to write the solution directly in chat.

## Reflect after the attempt

Choose one question from the actual code and process, and ask the learner for their own observation in English.

- Where did you first get stuck: understanding the prompt, recognizing the structure, choosing a tool, or implementing it? Which constraint did you notice then?
- Which example or boundary first exposed an error? What check will you make after coding next time?
- Which cue helped you find a viable approach? How will you recognize it in a similar problem?

## Example

The `lc-1071` prompt describes two strings and the longest string that divides both. Its `review_focus` can check length relationships, character repetition, and the case where no common divisor string exists. The same item links each round's independent code and reflection.

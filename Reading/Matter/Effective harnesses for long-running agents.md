## Metadata
* URL: [https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
* Author: aratahikaru5
* Publisher: anthropic.com
* Tags: 

## Highlights
* Claude’s failures manifested in two patterns.
  * **Note**: The two failure modes are:

1. Trying to do too much at once— the agent attempts to one-shot everything, runs out of context mid-implementation, and leaves a half-finished mess for the next session to untangle.

2. Declaring done prematurely — a later agent sees existing progress and assumes the job is complete, stopping before all features are actually built.
* prompt each agent to make incremental progress towards its goal while also leaving the environment in a clean state at the end of a session
* the best way to elicit this behavior was to ask the model to commit its progress to git with descriptive commit messages and to write summaries of its progress in a progress file.
* Absent explicit prompting, Claude tended to make code changes, and even do testing with unit tests or curl commands against a development server, but would fail recognize that the feature didn’t work end-to-end.

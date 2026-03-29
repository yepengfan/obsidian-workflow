## Metadata
* URL: [https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)
* Author: Martin Fowler
* Publisher: Martin Fowler
* Published Date: 2026-02-17
* Tags: 

## Highlights
* mix deterministic and LLM-based approaches across 3 categories (grouping based on my interpretation):
* Context engineering: Continuously enhanced knowledge base in the codebase, plus agent access to dynamic context like observability data and browser navigation
* Architectural constraints: Monitored not only by the LLM-based agents, but also deterministic custom linters and structural tests
* “Garbage collection”: Agents that run periodically to find inconsistencies in documentation or violations of architectural constraints, fighting entropy and decay
* The article made me imagine a future where teams pick from a set of harnesses for common application topologies to get started.
* “golden path”. Will harnesses — with custom linters, structural tests, basic context and knowledge documentation, and additional context providers — become the new service templates?

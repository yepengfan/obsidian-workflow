Find thematic connections across Book Summaries related to: $ARGUMENTS

## Steps

1. **Search for related summaries** by scanning `Book Summaries/` for notes whose Key Themes, Core Takeaways, or 中文摘要 mention the topic or closely related concepts. Use Grep to search for keywords and synonyms.

2. **Read the top matches** (up to 10 most relevant files). Identify overlapping ideas, complementary perspectives, and contrasting viewpoints.

3. **Present a connections report** in this format:

### 🔗 Connections: [topic]

**Books that discuss this topic:**
- [[Book Summaries/Title]] — *brief explanation of how it connects*
- [[Book Summaries/Title]] — *brief explanation*
- ...

**Cross-book insights:**
- [Synthesis of how multiple books approach this topic differently or reinforce each other. This is the most valuable part — connect ideas across books, don't just list them.]

**Suggested reading order** (if the user wants to go deeper):
1. Start with: [[Book]] — reason
2. Then: [[Book]] — reason
3. Deep dive: [[Book]] — reason

4. **Optionally create a Map of Content (MOC)** — If the user says "create MOC" or "save", create a note in `Thoughts/` named `MOC - [Topic].md` with this structure:

```markdown
---
date: [today's date]
tags: moc
---

# [Topic]

> [!info] Map of Content
> This MOC connects books and notes related to [topic].

## Books

- [[Book Summaries/Title]] — brief connection
- ...

## Cross-Book Insights

[Synthesized insights from multiple sources]

## Related Notes

- [[any other vault notes that connect]]
```

## Rules
- Only link to notes that actually exist in the vault
- Search broadly — the topic might appear under different names in different books
- The cross-book insights section should synthesize, not just summarize — find the thread that connects different authors' perspectives
- Match the language of the user's query (English query → English response, Chinese query → Chinese response)
- NEVER modify anything in WeRead/

Audit and clean up tags across the vault.

## Tag Taxonomy

The vault uses these standard tags. When auditing, classify notes into the appropriate categories:

### Content Type Tags
- `book-summary` — AI-generated book summary (Book Summaries/ folder)
- `book-summary-index` — Index/dashboard for book summaries
- `daily` — Daily journal notes
- `research` — Research notes created via /research
- `moc` — Map of Content (thematic index notes)
- `meeting` — Meeting notes
- `decision-log` — Decision records
- `project-brief` — Project documentation

### Topic Tags (use as secondary tags alongside content type)
- `investing` — Finance, investing, markets
- `psychology` — Psychology, behavioral science, decision-making
- `technology` — Software, architecture, engineering
- `leadership` — Management, leadership, teamwork
- `productivity` — Habits, time management, efficiency
- `philosophy` — Philosophy, life principles, worldview
- `literature` — Fiction, novels, literary works
- `business` — Entrepreneurship, startups, strategy
- `self-improvement` — Personal growth, mindset, resilience
- `history` — History, civilization, culture
- `science` — Science, biology, physics

## Steps

1. **Scan the vault** for all files with frontmatter tags. Report:
   - Current tag distribution (count per tag)
   - Files with NO tags that probably should have them
   - Files with inconsistent or non-standard tags

2. **Propose changes** — For each file that needs tag updates, show:
   - File path
   - Current tags
   - Proposed tags (using the taxonomy above)
   - Reason

3. **Wait for approval** before making any changes.

4. **If approved**, update the frontmatter tags. Rules:
   - Book Summaries: Keep `book-summary` and ADD one topic tag (e.g., `tags: [book-summary, investing]`)
   - Work docs: Add appropriate content type tag + topic tag
   - Never remove existing valid tags, only add or standardize
   - NEVER modify WeRead/ files
   - Preserve all other frontmatter fields

5. **Report** the final summary of changes made.

## Scope

If $ARGUMENTS specifies a folder, only audit that folder. Otherwise audit the entire vault (excluding WeRead/ and Attachments/).

Create a new brownbag session note at `Work/Brownbag Sessions/$ARGUMENTS.md` using the `Templates/Brownbag Session.md` template.

1. First, scan all existing notes in `Work/Brownbag Sessions/` and find the highest `id` value (format: `BB-N`). The new session gets `BB-(N+1)`. If no sessions exist yet, start with `BB-1`.
2. Replace `{{id}}` with the next number, `{{title}}` with the session topic provided, and `{{date}}` with today's date (YYYY-MM-DD).
3. If the session note already exists, tell me instead of overwriting it.
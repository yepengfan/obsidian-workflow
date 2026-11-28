---
tags: [practice-review/index]
cssclasses: [dashboard, practice-review-page, module-dashboard]
---

```dataviewjs
const shared = { app, title: "Practice Review", description: "Your review queue, schedule, and recorded practice attempts.", links: [["Review guide", "Learning/Practice/Review/AGENTS.md"]] };
await dv.view("scripts/dashboard/ui", shared);
await dv.view("scripts/dashboard/practice-review", { app, container: shared.ui.content });
```

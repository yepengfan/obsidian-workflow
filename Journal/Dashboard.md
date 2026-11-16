---
cssclasses: [dashboard, module-dashboard]
---

```dataviewjs
const shared = { app, title: "Journal", icon: "journal", description: "Daily reflection and the things you want to revisit.", links: [["Rolling review", "Journal/Review.md"], ["Guide", "Journal/Guide.md"]] };
await dv.view("scripts/dashboard/ui", shared);
await dv.view("scripts/journal", { app, container: shared.ui.content });
```

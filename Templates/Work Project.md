---
tags: work-project
---

# {{title}}

## Open Tasks

```dataviewjs
const project = dv.current().file.name;
const pages = dv.pages('"Work"')
    .where(p => p.file.tags.includes("#work-daily"));

const tasks = pages.file.tasks
    .where(t => t.section?.subpath === project && !t.completed);

if (tasks.length > 0) {
    dv.taskList(tasks, true);
} else {
    dv.paragraph("No open tasks.");
}
```

## Completed Tasks

```dataviewjs
const project = dv.current().file.name;
const pages = dv.pages('"Work"')
    .where(p => p.file.tags.includes("#work-daily"));

const tasks = pages.file.tasks
    .where(t => t.section?.subpath === project && t.completed);

if (tasks.length > 0) {
    dv.taskList(tasks, true);
} else {
    dv.paragraph("No completed tasks yet.");
}
```

## Notes


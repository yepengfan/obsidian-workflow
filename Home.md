---
cssclasses:
  - dashboard
banner: "![[home.jpg]]"
banner_x: 0.5
banner_y: 0
---

## Work

[[Work Dashboard|Open Work Dashboard]] · `$= "[[Work/" + dv.date("today").toFormat("yyyy/yyyy-MM-dd") + "|Today's Note]]"`

**Today's open tasks:**

```dataviewjs
const today = dv.date("today").toFormat("yyyy-MM-dd");
const todayPage = dv.page("Work/" + today.slice(0, 4) + "/" + today);
if (todayPage) {
    const tasks = todayPage.file.tasks.where(t => !t.completed);
    if (tasks.length > 0) {
        dv.taskList(tasks, false);
    } else {
        dv.paragraph("All done for today!");
    }
} else {
    dv.paragraph("No daily note yet — click today in Calendar to start.");
}
```

---

## Recent Updates

```dataview
TABLE file.mtime AS "Modified"
FROM ""
SORT file.mtime DESC
LIMIT 5
```

---

## Recent Reading Activity

```dataview
TABLE author AS "Author", readingStatus AS "Status", progress AS "Progress", lastReadDate AS "Last Read"
FROM "WeRead"
WHERE lastReadDate
SORT lastReadDate DESC
LIMIT 10
```

### Articles

```dataview
TABLE length(rows) AS "Notes"
FROM "Matter" OR "Instapaper Notes" OR "Omnivore"
FLATTEN file.folder AS source
GROUP BY source
SORT length(rows) DESC
```

### Book Summaries

```dataview
TABLE author AS "Author", title AS "Original Title"
FROM "Book Summaries"
SORT file.name ASC
LIMIT 10
```

---

## Thoughts

```dataview
LIST
FROM "Thoughts"
SORT file.mtime DESC
```

---

## Entertainment

```dataview
LIST
FROM "Entertainment"
SORT file.mtime DESC
```

---

## Learning

```dataview
LIST
FROM "AWS Skill Builder"
SORT file.mtime DESC
```

---

## Vault Stats

```dataviewjs
const folders = dv.pages('').groupBy(p => p.file.folder.split('/')[0]).sort(g => g.rows.length, 'desc');
dv.table(["Folder", "Notes"], folders.map(g => [g.key || "Root", g.rows.length]));
```

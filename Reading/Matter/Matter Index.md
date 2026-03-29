---
tags: [index]
---

# Matter Articles

[[Home|← Home]]

```dataview
TABLE author AS "Author", publisher AS "Publisher"
FROM "Reading/Matter"
WHERE file.name != "Matter Index"
SORT file.mtime DESC
```

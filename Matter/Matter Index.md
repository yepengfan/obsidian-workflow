---
tags: [index]
---

# Matter Articles

[[Home|← Home]]

```dataview
TABLE author AS "Author", publisher AS "Publisher"
FROM "Matter"
WHERE file.name != "Matter Index"
SORT file.mtime DESC
```

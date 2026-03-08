---
tags: [index]
---

# Instapaper Articles

[[Home|← Home]]

```dataview
TABLE author AS "Author", date AS "Saved"
FROM "Instapaper Notes"
WHERE file.name != "Instapaper Index"
SORT file.mtime DESC
```

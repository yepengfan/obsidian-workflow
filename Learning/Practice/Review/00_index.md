---
tags: [practice-review/index]
---

# 练习回顾与间隔复习

用 `/practice` 选择练习或 Review，再选择模块。练习直接进入原有流程输入题目；Review 从到期队列选题。[[Learning/Practice/Review/AGENTS|复习模块规则]]

```dataviewjs
const config = dv.page("system/modules/practice-review/module.md");
if (!config) {
  dv.paragraph("找不到复习模块配置。");
} else if (config.enabled !== true) {
  dv.paragraph("复习模块已暂停。用 `/module-toggle practice-review` 启用。");
} else {
  const today = dv.date("today").toISODate();
  const due = [];
  const unstarted = [];
  let invalidDates = 0;

  for (const item of dv.pages('"Learning/Practice/Review/Items"')) {
    if (item.status !== "active") continue;
    const entry = {
      id: item.id ?? item.file.name,
      title: item.title ?? item.file.name,
      domain: item.domain ?? "",
    };

    if (item.next_review == null) {
      unstarted.push(entry);
      continue;
    }

    const rawDate = item.next_review;
    const date = typeof rawDate === "string" && /^\d{4}-\d{2}-\d{2}$/.test(rawDate)
      ? dv.date(rawDate)
      : rawDate;
    if (!date?.isValid || typeof date.toISODate !== "function") {
      invalidDates++;
      continue;
    }

    const nextReview = date.toISODate();
    if (nextReview <= today) due.push({ ...entry, nextReview });
  }

  due.sort((a, b) => a.nextReview.localeCompare(b.nextReview) || a.id.localeCompare(b.id));
  unstarted.sort((a, b) => a.id.localeCompare(b.id));
  const dueToday = due.filter(item => item.nextReview === today).length;
  dv.paragraph(`今日到期 **${dueToday}** · 逾期 **${due.length - dueToday}** · 待首次练习 **${unstarted.length}**`);
  if (invalidDates > 0) {
    dv.paragraph(`有 ${invalidDates} 个条目的复习日期无效。修正对应的 next_review 后即可纳入统计。`);
  }

  dv.header(2, "到期复习");
  if (due.length > 0) {
    dv.table(["题目", "ID", "领域", "复习日期"], due.map(item => [
      item.title, item.id, item.domain, item.nextReview,
    ]));
  } else {
    dv.paragraph("今天没有到期或逾期的复习。");
  }

  dv.header(2, "待首次练习");
  const firstListLimit = 5;
  if (unstarted.length > 0) {
    dv.table(["题目", "ID", "领域"], unstarted.slice(0, firstListLimit).map(item => [
      item.title, item.id, item.domain,
    ]));
    if (unstarted.length > firstListLimit) {
      dv.paragraph(`另有 ${unstarted.length - firstListLimit} 项。用 /practice-review-today 查看完整列表。`);
    }
  } else {
    dv.paragraph("当前没有待首次练习的条目。");
  }
}
```

const app = input.app;
const isMobile = app.isMobile;
const lPanels = { fe: dv.el("div", "") };
// ========== FRONTEND TAB ==========
{
  const p = lPanels["fe"];

  // Stats
  const patterns = dv
    .pages('"Learning/Practice/Frontend/Patterns"')
    .where((x) => x.file.tags.includes("#frontend/pattern"));
  const logs = dv
    .pages('"Learning/Practice/Frontend/Log"')
    .where((x) => x.file.tags.includes("#frontend/log"));

  const totalPatterns = patterns.length;
  const pArr = patterns.array();
  const totalProblems = pArr.reduce(
    (sum, x) =>
      sum +
      (x.problems ? (Array.isArray(x.problems) ? x.problems.length : 1) : 0),
    0,
  );

  const todayD = dv.date("today");
  const weekStart =
    todayD.weekday === 1 ? todayD : todayD.minus({ days: todayD.weekday - 1 });
  const lastMonthStart = todayD.set({ day: 1 }).minus({ months: 1 });
  const lastMonthEnd = todayD.set({ day: 1 }).minus({ days: 1 });
  const lArr = logs.array();
  const weekProblems = lArr
    .filter((l) => dv.date(l.date) >= weekStart)
    .reduce(
      (sum, l) =>
        sum +
        (l.challenges_completed
          ? Array.isArray(l.challenges_completed)
            ? l.challenges_completed.length
            : 1
          : 0),
      0,
    );
  const lastMonthProblems = lArr
    .filter((l) => {
      const d = dv.date(l.date);
      return d >= lastMonthStart && d <= lastMonthEnd;
    })
    .reduce(
      (sum, l) =>
        sum +
        (l.challenges_completed
          ? Array.isArray(l.challenges_completed)
            ? l.challenges_completed.length
            : 1
          : 0),
      0,
    );

  const statsLine = p.createEl("div", {
    attr: {
      style:
        "font-size:0.85em;padding:8px 12px;background:var(--background-secondary);border-radius:8px;border-left:3px solid var(--color-accent);margin-bottom:10px;",
    },
  });
  statsLine.innerHTML = `<strong>${totalPatterns}</strong> patterns · <strong>${totalProblems}</strong> challenges · 本周 <strong>${weekProblems}</strong> 题 · 上月 <strong>${lastMonthProblems}</strong> 题`;

  // Category distribution bars
  const catCount = {};
  for (const x of pArr) {
    const c = x.category || "Other";
    catCount[c] = (catCount[c] || 0) + 1;
  }
  const catEntries = Object.entries(catCount).sort((a, b) => b[1] - a[1]);
  const maxCat = catEntries.length > 0 ? catEntries[0][1] : 1;

  if (catEntries.length > 0) {
    const catWrap = p.createEl("div", {
      attr: { style: "margin-bottom:10px;" },
    });
    catWrap.createEl("div", {
      text: "📊 Category 分布",
      attr: {
        style:
          "font-size:0.8em;font-weight:600;margin-bottom:4px;color:var(--text-muted);",
      },
    });
    for (const [cat, count] of catEntries) {
      const row = catWrap.createEl("div", {
        attr: {
          style: "display:flex;align-items:center;gap:6px;margin-bottom:2px;",
        },
      });
      row.createEl("div", {
        text: cat,
        attr: {
          style: `font-size:0.72em;color:var(--text-muted);width:${isMobile ? "80px" : "140px"};text-align:right;flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;`,
        },
      });
      const barOuter = row.createEl("div", {
        attr: {
          style:
            "flex:1;height:8px;background:var(--background-modifier-border);border-radius:4px;overflow:hidden;",
        },
      });
      barOuter.createEl("div", {
        attr: {
          style: `width:${(count / maxCat) * 100}%;height:100%;background:var(--color-accent);border-radius:4px;opacity:0.8;`,
        },
      });
      row.createEl("div", {
        text: String(count),
        attr: {
          style:
            "font-size:0.72em;color:var(--text-faint);width:18px;flex-shrink:0;",
        },
      });
    }
  }

  // Recent activity (last 7 log entries)
  const recentLogs = lArr
    .filter((l) => l.date)
    .sort((a, b) => dv.date(b.date).ts - dv.date(a.date).ts)
    .slice(0, 7);

  if (recentLogs.length > 0) {
    const actWrap = p.createEl("div", {
      attr: { style: "margin-bottom:10px;" },
    });
    actWrap.createEl("div", {
      text: "📝 最近练题",
      attr: {
        style:
          "font-size:0.8em;font-weight:600;margin-bottom:4px;color:var(--text-muted);",
      },
    });
    for (const log of recentLogs) {
      const d = dv.date(log.date).toFormat("MM-dd");
      const solved = log.challenges_completed
        ? Array.isArray(log.challenges_completed)
          ? log.challenges_completed
          : [log.challenges_completed]
        : [];
      const row = actWrap.createEl("div", {
        attr: {
          style: "display:flex;align-items:center;gap:6px;padding:2px 0;",
        },
      });
      row.createEl("span", {
        text: d,
        attr: {
          style:
            "font-size:0.72em;color:var(--text-faint);width:36px;flex-shrink:0;",
        },
      });
      const pills = row.createEl("div", {
        attr: { style: "display:flex;gap:3px;flex-wrap:wrap;" },
      });
      for (const name of solved) {
        pills.createEl("a", {
          text: name,
          attr: {
            class: "internal-link",
            "data-href": log.file.path,
            style:
              "font-size:0.7em;padding:1px 6px;border-radius:4px;background:var(--background-secondary);border:1px solid var(--background-modifier-border);text-decoration:none;white-space:nowrap;",
          },
        });
      }
      if (solved.length === 0) {
        pills.createEl("span", {
          text: "-",
          attr: { style: "font-size:0.72em;color:var(--text-faint);" },
        });
      }
    }
  }

  if (totalPatterns === 0 && recentLogs.length === 0) {
    p.createEl("div", {
      text: "还没有练习记录 - 用 /frnt-solve 开始做题！",
      attr: {
        style: "font-size:0.82em;color:var(--text-muted);padding:6px 0;",
      },
    });
  }
}

const app = input.app;
const isMobile = app.isMobile;
const lPanels = { sd: dv.el("div", "") };
function roadmapTopicMatches(item, topic) {
  const normalizedTopic = String(topic ?? "").toLowerCase();
  return Array.from(item?.aliases ?? []).some((alias) =>
    normalizedTopic.includes(String(alias).toLowerCase()),
  );
}
// ========== SYSTEM DESIGN TAB ==========
{
  const p = lPanels["sd"];

  // Practice queue - WIP first, then planned sessions in SYSD roadmap order.
  {
    const sessionFiles = app.vault
      .getMarkdownFiles()
      .filter(
        (f) =>
          f.path.startsWith("Learning/Practice/System-Design/Solutions/") &&
          f.name === "progress.md",
      );
    const hasStatus = (file, status) => {
      const cache = app.metadataCache.getFileCache(file);
      const tags = cache?.frontmatter?.tags || [];
      return tags.includes(`system-design/${status}`);
    };
    const wipFiles = sessionFiles.filter((file) => hasStatus(file, "wip"));
    const plannedFiles = sessionFiles.filter((file) =>
      hasStatus(file, "planned"),
    );
    const sysdPlan = dv.page("Learning/Plans/SYSD/00_plan");
    const roadmap = Array.from(sysdPlan?.roadmap ?? []);

    const sessionInfo = (file) => {
      const parts = file.path.split("/");
      const folder = parts[parts.length - 2] || "Unknown";
      const folderName = folder.replace(/-\d{4}-\d{2}-\d{2}$/, "") || folder;
      const cache = app.metadataCache.getFileCache(file);
      const fm = cache?.frontmatter || {};
      const topic = String(fm.topic || folderName);
      const roadmapIndex = roadmap.findIndex((item) =>
        roadmapTopicMatches(item, topic),
      );
      const item = roadmapIndex >= 0 ? roadmap[roadmapIndex] : null;
      return {
        file,
        folder,
        folderName,
        title: item?.title ? String(item.title) : folderName.replace(/-/g, " "),
        focus: item?.focus ? String(item.focus) : "",
        started: fm.started || "",
        roadmapIndex:
          roadmapIndex >= 0 ? roadmapIndex : Number.MAX_SAFE_INTEGER,
      };
    };

    if (wipFiles.length > 0) {
      const wipWrap = p.createEl("div", {
        attr: { style: "margin-bottom:10px;" },
      });
      wipWrap.createEl("div", {
        text: `🔄 进行中 · ${wipFiles.length}`,
        attr: {
          style:
            "font-size:0.8em;font-weight:600;margin-bottom:4px;color:var(--text-muted);",
        },
      });
      for (const wf of wipFiles) {
        const infoData = sessionInfo(wf);

        const newPath = `Learning/Practice/System-Design/Solutions/${infoData.folder}/${infoData.folderName}.excalidraw.md`;
        const oldPath = `Learning/Practice/System-Design/Solutions/${infoData.folder}/${infoData.folder}.excalidraw.md`;
        const excalidrawPath = app.vault.getAbstractFileByPath(newPath)
          ? newPath
          : oldPath;
        const card = wipWrap.createEl("div", {
          attr: {
            style:
              "display:flex;align-items:center;gap:10px;padding:9px 12px;background:var(--background-secondary);border-radius:8px;border-left:3px solid var(--color-orange);margin-bottom:6px;cursor:pointer;",
          },
        });
        card.addEventListener("click", () =>
          app.workspace.openLinkText(excalidrawPath, "", false),
        );

        card.createEl("span", {
          text: "🔄",
          attr: { style: "font-size:1.1em;flex-shrink:0;" },
        });
        const info = card.createEl("div", {
          attr: { style: "flex:1;min-width:0;" },
        });
        info.createEl("div", {
          text: infoData.title,
          attr: {
            style:
              "font-size:0.85em;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;",
          },
        });
        const details = [
          infoData.focus,
          infoData.started ? `Started ${infoData.started}` : "",
        ]
          .filter(Boolean)
          .join(" · ");
        if (details) {
          info.createEl("div", {
            text: details,
            attr: {
              style:
                "font-size:0.65em;color:var(--text-faint);margin-top:1px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;",
            },
          });
        }
        card.createEl("span", {
          text: "Continue →",
          attr: {
            style:
              "font-size:0.72em;color:var(--color-orange);white-space:nowrap;flex-shrink:0;",
          },
        });
      }
    }

    if (plannedFiles.length > 0) {
      const plannedWrap = p.createEl("div", {
        attr: { style: "margin-bottom:10px;" },
      });
      plannedWrap.createEl("div", {
        text: `📋 Planned · ${plannedFiles.length}`,
        attr: {
          style:
            "font-size:0.8em;font-weight:600;margin-bottom:4px;color:var(--text-muted);",
        },
      });
      const plannedGrid = plannedWrap.createEl("div", {
        attr: {
          style: `display:grid;grid-template-columns:${isMobile ? "1fr" : "repeat(2,minmax(0,1fr))"};gap:5px;`,
        },
      });
      const plannedItems = plannedFiles
        .map(sessionInfo)
        .sort((a, b) => a.roadmapIndex - b.roadmapIndex);
      for (const item of plannedItems) {
        const card = plannedGrid.createEl("div", {
          attr: {
            style:
              "display:flex;align-items:center;gap:8px;padding:7px 10px;background:var(--background-secondary);border-radius:7px;border-left:3px solid var(--color-accent);cursor:pointer;min-width:0;",
          },
        });
        card.addEventListener("click", () =>
          app.workspace.openLinkText(item.file.path, "", false),
        );
        card.createEl("span", {
          text: "◻",
          attr: {
            style: "font-size:0.9em;color:var(--color-accent);flex-shrink:0;",
          },
        });
        const info = card.createEl("div", {
          attr: { style: "flex:1;min-width:0;" },
        });
        info.createEl("div", {
          text: item.title,
          attr: {
            style:
              "font-size:0.76em;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;",
          },
        });
        if (item.focus) {
          info.createEl("div", {
            text: item.focus,
            attr: {
              style:
                "font-size:0.62em;color:var(--text-faint);margin-top:1px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;",
            },
          });
        }
        card.createEl("span", {
          text: "Planned",
          attr: {
            style:
              "font-size:0.6em;color:var(--text-faint);white-space:nowrap;flex-shrink:0;",
          },
        });
      }
    }
  }

  // Stats
  const patterns = dv
    .pages('"Learning/Practice/System-Design/Patterns"')
    .where((x) => x.file.tags.includes("#system-design/pattern"));
  const logs = dv
    .pages('"Learning/Practice/System-Design/Log"')
    .where((x) => x.file.tags.includes("#system-design/log"));

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
        (l.problems_solved
          ? Array.isArray(l.problems_solved)
            ? l.problems_solved.length
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
        (l.problems_solved
          ? Array.isArray(l.problems_solved)
            ? l.problems_solved.length
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
  statsLine.innerHTML = `<strong>${totalPatterns}</strong> patterns · <strong>${totalProblems}</strong> problems · 本周 <strong>${weekProblems}</strong> 题 · 上月 <strong>${lastMonthProblems}</strong> 题`;

  // Category distribution - Donut Chart
  const catCount = {};
  for (const x of pArr) {
    const c = x.category || "Other";
    catCount[c] = (catCount[c] || 0) + 1;
  }
  const catEntries = Object.entries(catCount).sort((a, b) => b[1] - a[1]);
  const catColors = [
    "#7C6EF6",
    "#E8674A",
    "#4CAF7D",
    "#F5A623",
    "#5B9BD5",
    "#D45DBF",
    "#45B7AA",
    "#F07171",
    "#8E8CD8",
    "#6ABE5F",
    "#E09C3F",
    "#5ECCC9",
    "#C97AB5",
    "#7FB069",
  ];
  const R = 70,
    SW = 28,
    CX = 100,
    CY = 100,
    CIRC = 2 * Math.PI * R;

  const catWrap = p.createEl("div", { attr: { style: "margin-bottom:10px;" } });
  catWrap.createEl("div", {
    text: "📊 Category 分布",
    attr: {
      style:
        "font-size:0.8em;font-weight:600;margin-bottom:4px;color:var(--text-muted);",
    },
  });
  const chartRow = catWrap.createEl("div", {
    attr: {
      style: `display:flex;${isMobile ? "flex-direction:column;" : ""}align-items:center;gap:${isMobile ? "8" : "16"}px;`,
    },
  });

  let arcs = "",
    arcOff = 0;
  catEntries.forEach(([, count], i) => {
    const seg = (count / (totalPatterns || 1)) * CIRC;
    arcs += `<circle cx="${CX}" cy="${CY}" r="${R}" fill="none" stroke="${catColors[i % catColors.length]}" stroke-width="${SW}" stroke-dasharray="${seg} ${CIRC - seg}" stroke-dashoffset="-${arcOff}" transform="rotate(-90 ${CX} ${CY})"/>`;
    arcOff += seg;
  });
  if (!arcs)
    arcs = `<circle cx="${CX}" cy="${CY}" r="${R}" fill="none" stroke="var(--background-modifier-border)" stroke-width="${SW}"/>`;

  const donutSz = isMobile ? "120px" : "140px";
  const svgEl = chartRow.createEl("div", {
    attr: { style: `flex-shrink:0;width:${donutSz};height:${donutSz};` },
  });
  svgEl.innerHTML = `<svg viewBox="0 0 200 200" style="width:100%;height:100%"><g>${arcs}</g><text x="${CX}" y="${CY - 6}" text-anchor="middle" fill="var(--text-normal)" font-size="28" font-weight="700">${totalPatterns}</text><text x="${CX}" y="${CY + 14}" text-anchor="middle" fill="var(--text-muted)" font-size="12">patterns</text></svg>`;

  const legend = chartRow.createEl("div", {
    attr: {
      style: `display:flex;flex-direction:column;gap:2px;${isMobile ? "" : "flex:1;"}`,
    },
  });
  catEntries.forEach(([cat, count], i) => {
    const item = legend.createEl("div", {
      attr: { style: "display:flex;align-items:center;gap:6px;" },
    });
    item.createEl("div", {
      attr: {
        style: `width:8px;height:8px;border-radius:2px;background:${catColors[i % catColors.length]};flex-shrink:0;`,
      },
    });
    item.createEl("div", {
      text: cat,
      attr: {
        style:
          "font-size:0.7em;color:var(--text-muted);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;",
      },
    });
    item.createEl("div", {
      text: String(count),
      attr: { style: "font-size:0.7em;color:var(--text-faint);flex-shrink:0;" },
    });
  });

  // Recent pattern cards - latest 5 by updated date
  {
    const recent = pArr
      .filter((x) => x.updated)
      .sort((a, b) => dv.date(b.updated).ts - dv.date(a.updated).ts)
      .slice(0, 5);
    if (recent.length > 0) {
      p.createEl("div", {
        text: "📝 最近 Pattern Cards",
        attr: {
          style:
            "font-size:0.8em;font-weight:600;margin:10px 0 6px;color:var(--text-muted);",
        },
      });
      const rcList = p.createEl("div", {
        attr: { style: "display:flex;flex-direction:column;gap:5px;" },
      });
      for (const pat of recent) {
        const card = rcList.createEl("div", {
          attr: {
            style:
              "display:flex;align-items:center;gap:10px;padding:7px 12px;background:var(--background-secondary);border-radius:8px;border-left:3px solid var(--color-accent);",
          },
        });
        const info = card.createEl("div", {
          attr: { style: "flex:1;min-width:0;" },
        });
        const nameEl = info.createEl("div", {
          attr: {
            style:
              "font-size:0.8em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;",
          },
        });
        nameEl.innerHTML = `<a class="internal-link" data-href="${pat.file.path}">${pat.title || pat.file.name}</a>`;
        const probCount = pat.problems
          ? Array.isArray(pat.problems)
            ? pat.problems.length
            : 1
          : 0;
        info.createEl("div", {
          text: `${pat.category || "-"} · ${probCount} 题`,
          attr: {
            style: "font-size:0.65em;color:var(--text-faint);margin-top:1px;",
          },
        });
        card.createEl("div", {
          text: dv.date(pat.updated).toFormat("M/d"),
          attr: {
            style: "font-size:0.7em;color:var(--text-faint);flex-shrink:0;",
          },
        });
      }
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
      const solved = log.problems_solved
        ? Array.isArray(log.problems_solved)
          ? log.problems_solved
          : [log.problems_solved]
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
        const pill = pills.createEl("a", {
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

  if (totalPatterns === 0) {
    p.createEl("div", {
      text: "还没有 patterns - 用 /sysd-solve 开始练题！",
      attr: {
        style: "font-size:0.82em;color:var(--text-muted);padding:6px 0;",
      },
    });
  }

  // Link to full dashboard
  p.createEl("div", {
    attr: { style: "margin-top:10px;font-size:0.85em;" },
  }).innerHTML =
    '<a class="internal-link" data-href="Learning/Practice/System-Design/00_index.md">All patterns →</a>';
}

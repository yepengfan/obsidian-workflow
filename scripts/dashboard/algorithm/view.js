const app = input.app;
const isMobile = app.isMobile;
const lPanels = { algo: dv.el("div", "") };
// ========== ALGORITHM TAB ==========
{
  const p = lPanels["algo"];

  // Stats
  const patterns = dv
    .pages('"Learning/Practice/Algorithm/Patterns"')
    .where((x) => x.file.tags.includes("#leetcode/pattern"));
  const logs = dv
    .pages('"Learning/Practice/Algorithm/Log"')
    .where((x) => x.file.tags.includes("#leetcode/log"));
  const atoms = dv
    .pages('"Learning/Practice/Algorithm/Atoms"')
    .where((x) => x.file.tags.includes("#leetcode/atom"));

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

  // Weekly activity bar chart (last 12 weeks)
  {
    const actWrap = p.createEl("div", {
      attr: { style: "margin-bottom:10px;" },
    });
    actWrap.createEl("div", {
      text: "📝 最近做题",
      attr: {
        style:
          "font-size:0.8em;font-weight:600;margin-bottom:6px;color:var(--text-muted);",
      },
    });

    const today = dv.date("today");
    const bw = isMobile ? 16 : 22;
    const bgap = isMobile ? 3 : 4;
    const maxH = isMobile ? 56 : 72;
    const nWeeks = 12;

    // Current week's Monday
    const todayDow = today.weekday;
    const thisMon =
      todayDow === 1 ? today : today.minus({ days: todayDow - 1 });

    // Aggregate problems per week
    const weeks = [];
    for (let w = nWeeks - 1; w >= 0; w--) {
      const ws = thisMon.minus({ weeks: w });
      const we = ws.plus({ days: 6 });
      let cnt = 0;
      for (const l of lArr) {
        if (!l.date) continue;
        const ld = dv.date(l.date);
        if (ld.ts >= ws.ts && ld.ts <= we.ts) {
          cnt += l.problems_solved
            ? Array.isArray(l.problems_solved)
              ? l.problems_solved.length
              : 1
            : 0;
        }
      }
      weeks.push({ start: ws, count: cnt });
    }
    const maxCnt = Math.max(3, ...weeks.map((w) => w.count));

    // Accent RGB for empty bar tint
    const _ac = getComputedStyle(document.body)
      .getPropertyValue("--color-accent")
      .trim();
    let _r = 124,
      _g = 110,
      _b = 246;
    if (_ac.startsWith("#")) {
      const h = _ac.slice(1);
      _r = parseInt(h.substring(0, 2), 16);
      _g = parseInt(h.substring(2, 4), 16);
      _b = parseInt(h.substring(4, 6), 16);
    } else if (_ac.startsWith("rgb")) {
      const m = _ac.match(/(\d+)/g);
      if (m && m.length >= 3) {
        _r = +m[0];
        _g = +m[1];
        _b = +m[2];
      }
    }

    const colH = maxH + 30;
    const chart = actWrap.createEl("div", {
      attr: { style: `display:flex;gap:${bgap}px;` },
    });

    for (const wk of weeks) {
      const col = chart.createEl("div", {
        attr: {
          style: `display:flex;flex-direction:column;align-items:center;width:${bw}px;height:${colH}px;`,
        },
      });
      col.createEl("div", { attr: { style: "flex:1;" } });
      if (wk.count > 0) {
        col.createEl("div", {
          text: String(wk.count),
          attr: {
            style: "font-size:0.6em;color:var(--text-faint);margin-bottom:2px;",
          },
        });
      }
      const barH =
        wk.count > 0 ? Math.max(6, Math.round((wk.count / maxCnt) * maxH)) : 3;
      const barBg =
        wk.count > 0 ? "var(--color-accent)" : `rgba(${_r},${_g},${_b},0.1)`;
      const barStyle = `width:${bw - 4}px;height:${barH}px;border-radius:3px;background:${barBg};`;
      if (wk.count > 0) {
        const bar = col.createEl("div", {
          attr: {
            title: `${wk.start.toFormat("yyyy-MM-dd")} 周 · ${wk.count} 题 · 点击查看本周详情`,
            style: barStyle + "cursor:pointer;",
          },
        });
        bar.addEventListener("click", () => {
          app.__algoWeeklyView = app.__algoWeeklyView || {};
          app.__algoWeeklyView.selectedWeekStart =
            wk.start.toFormat("yyyy-MM-dd");
          app.workspace.openLinkText(
            "Learning/Practice/Algorithm/Weekly View.md",
            "",
            false,
          );
        });
      } else {
        col.createEl("div", { attr: { style: barStyle } });
      }
      col.createEl("div", {
        text: wk.start.toFormat("M/d"),
        attr: {
          style:
            "font-size:0.5em;color:var(--text-faint);margin-top:3px;white-space:nowrap;",
        },
      });
    }
  }

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

  // Recent atom cards - latest 5 by updated date
  {
    const aArr = atoms.array();
    const recentAtoms = aArr
      .filter((x) => x.updated)
      .sort((a, b) => dv.date(b.updated).ts - dv.date(a.updated).ts)
      .slice(0, 5);
    if (recentAtoms.length > 0) {
      p.createEl("div", {
        text: "🧬 最近更新的 Atoms",
        attr: {
          style:
            "font-size:0.8em;font-weight:600;margin:10px 0 6px;color:var(--text-muted);",
        },
      });
      const raList = p.createEl("div", {
        attr: { style: "display:flex;flex-direction:column;gap:5px;" },
      });
      for (const atom of recentAtoms) {
        const card = raList.createEl("div", {
          attr: {
            style:
              "display:flex;align-items:center;gap:10px;padding:7px 12px;background:var(--background-secondary);border-radius:8px;border-left:3px solid #8E8CD8;",
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
        nameEl.innerHTML = `<a class="internal-link" data-href="${atom.file.path}">${atom.title || atom.file.name}</a>`;
        const usedByCount = atom.file.inlinks ? atom.file.inlinks.length : 0;
        info.createEl("div", {
          text: `Atom · used by ${usedByCount} pattern${usedByCount === 1 ? "" : "s"}`,
          attr: {
            style: "font-size:0.65em;color:var(--text-faint);margin-top:1px;",
          },
        });
        card.createEl("div", {
          text: dv.date(atom.updated).toFormat("M/d"),
          attr: {
            style: "font-size:0.7em;color:var(--text-faint);flex-shrink:0;",
          },
        });
      }
    }
  }

  // Link to full dashboard
  p.createEl("div", {
    attr: { style: "margin-top:10px;font-size:0.85em;display:flex;gap:14px;" },
  }).innerHTML =
    '<a class="internal-link" data-href="Learning/Practice/Algorithm/00_index.md">All patterns →</a>' +
    '<a class="internal-link" data-href="Learning/Practice/Algorithm/Weekly View.md">Weekly view →</a>';
}

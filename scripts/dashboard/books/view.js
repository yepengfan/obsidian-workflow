const app = input.app;
const isMobile = app.isMobile;
// ========== 📖 读书 ==========
dv.el("div", "📖 读书", {
  attr: {
    style:
      "font-size:0.92em;font-weight:700;margin:16px 0 6px;color:var(--text-normal);",
  },
});

{
  const container = dv.el("div", "");
  const bookPages = dv
    .pages('"Learning/Books"')
    .where((p) => p.file.name === "meta");
  const bookChapters = (folder) => {
    const all = dv
      .pages(`"${folder}/chapters"`)
      .where((c) => c.chapter !== undefined)
      .sort((c) => c.chapter, "asc");
    // Some EPUB tables of contents repeat all real chapters as a bare "Chapter N" tail.
    const titled = all.where(
      (c) => !/^Chapter\s+\d+$/i.test(String(c.title || "").trim()),
    );
    const bare = all.where((c) =>
      /^Chapter\s+\d+$/i.test(String(c.title || "").trim()),
    );
    const repeatedTail =
      titled.length > 0 &&
      bare.length === titled.length &&
      Array.from(bare).every(
        (c, i) =>
          c.chapter > titled.length &&
          String(c.title).trim().toLowerCase() === `chapter ${i + 1}`,
      );
    return repeatedTail ? titled : all;
  };
  // Prefer a book's pinned cover, then its WeRead cover. Local covers need a resource URL.
  function resolveCoverUrl(coverValue) {
    if (!coverValue) return null;
    const str = String(coverValue);
    if (/^https?:\/\//i.test(str)) return str;
    const file = app.vault.getAbstractFileByPath(str);
    return file ? app.vault.getResourcePath(file) : null;
  }
  function findBookCover(meta, bookName) {
    if (meta?.cover) return resolveCoverUrl(meta.cover);
    const wrFolder = app.vault.getAbstractFileByPath(`WeRead/${bookName}`);
    if (!wrFolder || !wrFolder.children) return null;
    for (const child of wrFolder.children) {
      if (child.extension !== "md") continue;
      const cover = app.metadataCache.getFileCache(child)?.frontmatter?.cover;
      if (cover) return resolveCoverUrl(cover);
    }
    return null;
  }

  // Production layer: books upgraded into Learning/Books/ (not raw WeRead capture).
  const metas = bookPages
    .where((p) => p.status === "reading")
    .sort((p) => p.started, "desc");

  if (metas.length === 0) {
    container.createEl("p", {
      text: "当前没有在读书籍。",
      attr: { style: "color:var(--text-muted);font-size:0.85em;" },
    });
  } else {
    const archLabel = {
      "technical-reference": "tech-ref",
      "cognitive-mental-model": "cognitive",
    };

    // Read WeRead progress live from the plugin-synced source file (single source
    // of truth). meta.md's static weread_progress is only a fallback for when the
    // source note can't be found - mirror of findBookCover, direction reversed.
    function findWeReadProgress(meta) {
      const src = meta?.weread_source;
      if (src) {
        const f = app.vault.getAbstractFileByPath(String(src));
        if (f) {
          const prog = app.metadataCache.getFileCache(f)?.frontmatter?.progress;
          if (prog != null) return String(prog);
        }
      }
      return meta?.weread_progress ? String(meta.weread_progress) : null;
    }

    // Which app the book is read in. Prefer the explicit `reading_channel` field
    // (canonical: weread | apple-books | both). Older books used file-format-mixed
    // values (e.g. "EPUB + WeRead") - normalize those. If still unknown, infer from
    // the capture sources (weread_source only → weread, ibooks only → apple-books,
    // both → both). Returns null when nothing can be determined.
    function bookChannel(meta) {
      const raw = String(meta?.reading_channel || "")
        .toLowerCase()
        .trim();
      if (raw === "both") return "both"; // canonical value - not matched by the token regexes below
      const hasWr = /weread/.test(raw);
      const hasAb = /apple|ibooks/.test(raw);
      if (hasWr && hasAb) return "both";
      if (hasWr) return "weread";
      if (hasAb) return "apple-books";
      const wrSrc = !!meta?.weread_source,
        abSrc = !!meta?.ibooks_source;
      if (wrSrc && abSrc) return "both";
      if (wrSrc) return "weread";
      if (abSrc) return "apple-books";
      return null;
    }
    const channelLabel = {
      weread: "WeRead",
      "apple-books": "Apple Books",
      both: "WeRead + Apple Books",
    };
    // Brand colors matching each app's icon - WeRead blue, Apple Books orange.
    // { fg: text, bg: tinted fill, bd: border }. `both` blends toward WeRead blue.
    const channelColor = {
      weread: {
        fg: "#2f80ed",
        bg: "rgba(47,128,237,0.12)",
        bd: "rgba(47,128,237,0.45)",
      },
      "apple-books": {
        fg: "#f59e0b",
        bg: "rgba(245,158,11,0.14)",
        bd: "rgba(245,158,11,0.5)",
      },
      both: {
        fg: "#2f80ed",
        bg: "rgba(47,128,237,0.12)",
        bd: "rgba(47,128,237,0.45)",
      },
    };

    for (const m of metas) {
      const folder = m.file.folder; // Learning/Books/<Title>
      const bookName = folder.split("/").pop();
      const mocPath = `${folder}/MOC.md`;
      const understandingPath = `${folder}/understanding.md`;
      const understandingExists =
        !!app.vault.getAbstractFileByPath(understandingPath);
      // Chapter heading in understanding.md is "Ch{N}. {title}" (strip leading "N." or "N "
      // from skeleton title - same regex as book_init.py chapter_filename_stem). Encode # in
      // the fragment so titles like "C# …" don't truncate the data-href URL.
      const chHeading = (c) =>
        `Ch${c.chapter}. ${String(c.title || "").replace(/^\d+[\.\s]+/, "")}`;
      const chAnchor = (c) =>
        `${understandingPath}#${chHeading(c).replace(/#/g, "%23")}`;
      const chLink = (c) => (understandingExists ? chAnchor(c) : c.file.path);

      // Chapter progress from meta.md's progress tracker (understanding = 落盘 done).
      const chapters = bookChapters(folder);
      const total = chapters.length;
      const prog = m.progress || {};
      const chKey = (n) => "ch" + String(n).padStart(2, "0");
      const isChDone = (c) => {
        const p = prog[chKey(c.chapter)];
        return !!(p && p.understanding && p.understanding !== "not_started");
      };
      const isChMapped = (c) => {
        const p = prog[chKey(c.chapter)];
        return !!(p && p.map && p.map !== "not_started");
      };
      const doneCh = chapters.where((c) => isChDone(c)).length; // 理解落盘完成数
      const mapCh = chapters.where((c) => isChMapped(c)).length; // 地图预填数
      const current = chapters.find((c) => !isChDone(c));
      const currentNum = current ? current.chapter : total > 0 ? total : null;

      // Card (mirrors 学习计划 card style) - accent bar + cover thumbnail + content
      const card = container.createEl("div", {
        attr: {
          style:
            "display:flex;gap:0;margin-bottom:8px;border:1px solid var(--background-modifier-border);border-radius:8px;overflow:hidden;background:var(--background-secondary);",
        },
      });
      card.createEl("div", {
        attr: {
          style: "width:3px;background:var(--color-accent);flex-shrink:0;",
        },
      });

      // Cover thumbnail (meta.md cover: field, else WeRead fallback) - placeholder icon if none found
      const coverUrl = findBookCover(m, bookName);
      const coverSize = isMobile ? "44px" : "52px";
      const coverWrap = card.createEl("div", {
        attr: {
          style: `width:${coverSize};flex-shrink:0;display:flex;align-items:center;justify-content:center;background:var(--background-primary);`,
        },
      });
      function showCoverPlaceholder() {
        coverWrap.empty();
        coverWrap.createEl("span", {
          text: "📖",
          attr: { style: "font-size:1.3em;opacity:0.35;" },
        });
      }
      if (coverUrl) {
        const coverImg = coverWrap.createEl("img", {
          attr: {
            src: coverUrl,
            alt: bookName,
            style: "width:100%;height:100%;object-fit:cover;",
          },
        });
        // Fall back to the placeholder icon if the WeRead-hosted cover 404s or is unreachable.
        coverImg.addEventListener("error", showCoverPlaceholder, {
          once: true,
        });
      } else {
        showCoverPlaceholder();
      }

      const body = card.createEl("div", {
        attr: { style: "flex:1;min-width:0;padding:9px 12px;" },
      });

      // Row 1: book title (wraps, clamped to 2 lines - no more truncated badge) + archetype pill
      const row1 = body.createEl("div", {
        attr: {
          style:
            "display:flex;align-items:flex-start;gap:6px;margin-bottom:3px;",
        },
      });
      row1.createEl("a", {
        text: bookName,
        attr: {
          class: "internal-link",
          "data-href": mocPath,
          title: bookName,
          style:
            "flex:1;min-width:0;font-weight:700;font-size:0.85em;line-height:1.3;color:var(--text-normal);text-decoration:none;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;",
        },
      });
      if (archLabel[m.archetype]) {
        row1.createEl("span", {
          text: archLabel[m.archetype],
          attr: {
            style:
              "font-size:0.62em;padding:1px 7px;margin-top:1px;border-radius:20px;border:1px solid var(--color-accent);color:var(--color-accent);white-space:nowrap;flex-shrink:0;",
          },
        });
      }
      // Reading-channel pill (which app it's read in) - muted, so it reads as metadata
      const channel = bookChannel(m);
      if (channel) {
        const cc = channelColor[channel] || {
          fg: "var(--text-muted)",
          bg: "transparent",
          bd: "var(--background-modifier-border)",
        };
        row1.createEl("span", {
          text: channelLabel[channel],
          title: "阅读渠道（你在哪个 App 读）",
          attr: {
            style: `font-size:0.62em;padding:1px 7px;margin-top:1px;border-radius:20px;border:1px solid ${cc.bd};background:${cc.bg};color:${cc.fg};white-space:nowrap;flex-shrink:0;`,
          },
        });
      }

      // Full title (edition, subtitle, etc.) - only shown when it adds info beyond the folder name.
      if (m.title && m.title !== bookName) {
        body.createEl("div", {
          text: m.title,
          attr: {
            style:
              "font-size:0.72em;color:var(--text-muted);margin-bottom:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;",
          },
        });
      }

      // Row 2: author · 图{mapped}/理解{done} · Ch current/total · WeRead %
      const bits = [];
      if (m.author) bits.push(m.author);
      if (total > 0) bits.push(`图${mapCh}/理解${doneCh}`);
      if (total > 0)
        bits.push(doneCh === total ? "✓ 完成" : `Ch${currentNum}/${total}`);
      // WeRead % only makes sense when the book is actually read in WeRead. A book
      // read in Apple Books may still carry a weread_source pointer (highlight sync
      // only), so gate on the reading channel to avoid a stale/contradictory %.
      const wr =
        channel === "weread" || channel === "both"
          ? findWeReadProgress(m)
          : null;
      if (wr) bits.push(`WeRead ${wr}`);
      if (bits.length) {
        body.createEl("div", {
          text: bits.join(" · "),
          attr: {
            style:
              "font-size:0.72em;color:var(--text-faint);margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;",
          },
        });
      }

      // Chapter progress dots (落盘 done = filled, current = dashed, else muted)
      if (total > 0) {
        const dotSize = isMobile ? "8px" : "10px";
        const dotGap = isMobile ? "2px" : "3px";
        const dotsWrap = body.createEl("div", {
          attr: {
            style: `display:flex;align-items:center;gap:${dotGap};margin-top:7px;flex-wrap:wrap;`,
          },
        });
        for (const c of chapters) {
          const isDone = isChDone(c); // 理解已落盘
          const isMapped = !isDone && isChMapped(c); // 地图已预填、待补理解
          const stateLabel = isDone
            ? " · 已落盘"
            : isMapped
              ? " · 地图已预填，待补理解"
              : "";
          dotsWrap.createEl("a", {
            attr: {
              class: "internal-link",
              "data-href": chLink(c),
              title: `Ch${c.chapter}: ${c.title || ""}${stateLabel}`,
              style:
                `width:${dotSize};height:${dotSize};border-radius:2px;display:inline-block;` +
                (isDone
                  ? "background:var(--color-accent);opacity:0.85;"
                  : isMapped
                    ? "border:1.5px solid var(--color-accent);opacity:0.65;"
                    : "background:var(--background-modifier-border);opacity:0.5;"),
            },
          });
        }
      }

      // Row: 📝 落盘 link (left) + ▶ 开始阅读 (right). 落盘 opens understanding.md
      // directly; 开始阅读 opens the book MOC (becomes linked_note) then Claudian chat.
      const btnRow = body.createEl("div", {
        attr: {
          style:
            "display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:7px;",
        },
      });
      btnRow.createEl("a", {
        text: "📝 落盘",
        attr: {
          class: "internal-link",
          "data-href": understandingExists ? understandingPath : mocPath,
          title: understandingExists
            ? "打开本书的 understanding.md（落盘记录）"
            : "understanding.md 尚未创建 - 打开 MOC（运行 /book-read 开始落盘）",
          style:
            "font-size:0.7em;color:var(--text-muted);text-decoration:none;white-space:nowrap;",
        },
      });
      const startBtn = btnRow.createEl("button", {
        text: "打开本书",
        attr: {
          style:
            "font-size:0.7em;padding:2px 9px;border-radius:6px;border:1px solid var(--color-accent);background:var(--color-accent);color:#fff;cursor:pointer;white-space:nowrap;",
        },
      });
      startBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        await app.workspace.openLinkText(mocPath, "", false);
        // The MOC is the supported entry; reading guidance is available via /book-read.
      });
    }
  }

  const finished = bookPages
    .where((p) => p.status === "finished")
    .sort((p) => p.finished, "desc");
  container.createEl("div", {
    text: `已读完 (${finished.length})`,
    attr: {
      style:
        "font-size:0.78em;font-weight:700;color:var(--text-muted);margin:13px 0 6px;",
    },
  });
  if (finished.length === 0) {
    container.createEl("p", {
      text: "暂无已读完书籍。",
      attr: { style: "color:var(--text-muted);font-size:0.78em;margin:0;" },
    });
  } else {
    for (const m of finished) {
      const folder = m.file.folder;
      const title = m.title || folder.split("/").pop();
      const chapters = bookChapters(folder);
      const progress = m.progress || {};
      const mapped = chapters.where(
        (c) =>
          progress[`ch${String(c.chapter).padStart(2, "0")}`]?.map === "done",
      ).length;
      const row = container.createEl("div", {
        attr: {
          style: `display:flex;align-items:stretch;margin-bottom:8px;border:1px solid var(--background-modifier-border);border-radius:8px;overflow:hidden;background:var(--background-secondary);font-size:${isMobile ? "0.88em" : "0.82em"};`,
        },
      });
      row.createEl("div", {
        attr: {
          style: "width:3px;background:var(--color-accent);flex-shrink:0;",
        },
      });
      const coverWrap = row.createEl("div", {
        attr: {
          style: `position:relative;width:${isMobile ? "44px" : "54px"};min-height:78px;flex-shrink:0;display:flex;align-items:center;justify-content:center;background:var(--background-primary);overflow:hidden;`,
        },
      });
      function showCoverPlaceholder() {
        coverWrap.empty();
        coverWrap.createEl("span", {
          text: "📖",
          attr: { style: "font-size:1.3em;opacity:0.35;" },
        });
      }
      const coverUrl = findBookCover(m, folder.split("/").pop());
      if (coverUrl) {
        const coverImg = coverWrap.createEl("img", {
          attr: {
            src: coverUrl,
            alt: `${title} 封面`,
            style:
              "position:absolute;inset:0;width:100%;height:100%;object-fit:contain;",
          },
        });
        coverImg.addEventListener("error", showCoverPlaceholder, {
          once: true,
        });
      } else {
        showCoverPlaceholder();
      }
      const body = row.createEl("div", {
        attr: { style: "flex:1;min-width:0;padding:8px 10px;" },
      });
      const top = body.createEl("div", {
        attr: {
          style: "display:flex;align-items:flex-start;gap:6px;flex-wrap:wrap;",
        },
      });
      const titleLink = top.createEl("a", {
        text: title,
        attr: {
          class: "internal-link",
          "data-href": `${folder}/MOC.md`,
          style:
            "font-weight:700;color:var(--text-normal);text-decoration:none;min-width:0;flex:1 1 160px;cursor:pointer;line-height:1.3;",
        },
      });
      titleLink.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        app.workspace.openLinkText(`${folder}/MOC.md`, "", false);
      });
      top.createEl("span", {
        text: `${m.finished ? dv.date(m.finished).toFormat("yyyy-MM-dd") : "已读完"} · 地图 ${mapped}/${chapters.length}`,
        attr: {
          style: "color:var(--text-faint);white-space:nowrap;font-size:0.86em;",
        },
      });
      const links = body.createEl("div", {
        attr: { style: "display:flex;gap:12px;flex-wrap:wrap;margin-top:7px;" },
      });
      for (const [label, path] of [
        ["章节地图", `${folder}/understanding.md`],
        ["读书心得", `${folder}/article.md`],
      ]) {
        if (!app.vault.getAbstractFileByPath(path)) continue;
        const link = links.createEl("a", {
          text: label,
          attr: {
            class: "internal-link",
            "data-href": path,
            style:
              "color:var(--color-accent);text-decoration:none;white-space:nowrap;cursor:pointer;",
          },
        });
        link.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          app.workspace.openLinkText(path, "", false);
        });
      }
    }
  }

  const indexRow = container.createEl("div", {
    attr: { style: "margin-top:10px;font-size:0.82em;" },
  });
  const indexLink = indexRow.createEl("a", {
    text: "全部书籍 →",
    attr: {
      class: "internal-link",
      "data-href": "Learning/Books/Books Index.md",
      style: "cursor:pointer;",
    },
  });
  indexLink.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    app.workspace.openLinkText("Learning/Books/Books Index.md", "", false);
  });
}
dv.header(2, "微信读书书架");
const pages = dv
  .pages('"WeRead"')
  .where((p) => p.author && p.doc_type === "weread-highlights-reviews")
  .where((p) => {
    const s = p.readingStatus;
    // readingStatus: 2="在读", 4="读完" (plugin uses numeric codes)
    const isReading = s === "在读" || s == 2;
    if (!isReading) return false;
    // Exclude books with 100% progress (effectively finished)
    const prog = parseInt(String(p.progress)) || 0;
    return prog < 100;
  })
  .sort((p) => p.lastReadDate, "desc")
  .limit(8);

const readContainer = dv.el("div", "");
const grid = readContainer.createEl("div", {
  attr: {
    style:
      "display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px;margin-top:8px;",
  },
});

for (const p of pages) {
  const title = p.file.name.replace(/-CB_.*$/, "").replace(/-\d+$/, "");
  const cover = p.cover || "";
  const rawProg = p.progress || "0%";
  // Sanitize: treat "-1" or negative as 0%, clamp to 0-100
  const parsedNum = parseInt(String(rawProg)) || 0;
  const clampedNum = Math.max(0, Math.min(100, parsedNum));
  const progress = clampedNum + "%";

  const card = grid.createEl("div", {
    attr: {
      style:
        "border:1px solid var(--background-modifier-border);border-radius:10px;overflow:hidden;background:var(--background-secondary);box-shadow:0 1px 3px rgba(0,0,0,0.06);",
    },
  });

  if (cover) {
    card.createEl("img", {
      attr: { src: cover, style: "width:100%;height:130px;object-fit:cover;" },
    });
  }

  const body = card.createEl("div", { attr: { style: "padding:8px;" } });
  const titleEl = body.createEl("div", {
    attr: {
      style:
        "font-weight:600;font-size:0.8em;margin-bottom:4px;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;",
    },
  });
  titleEl.innerHTML = `<a class="internal-link" data-href="${p.file.path}">${title}</a>`;
  if (p.author) {
    body.createEl("div", {
      text: p.author,
      attr: {
        style: "font-size:0.7em;color:var(--text-muted);margin-bottom:4px;",
      },
    });
  }
  // Progress bar
  const barBg = body.createEl("div", {
    attr: {
      style:
        "height:4px;background:var(--background-modifier-border);border-radius:2px;overflow:hidden;",
    },
  });
  barBg.createEl("div", {
    attr: {
      style: `height:100%;width:${clampedNum}%;background:var(--interactive-accent);border-radius:2px;`,
    },
  });
  body.createEl("div", {
    text: progress,
    attr: { style: "font-size:0.68em;color:var(--text-faint);margin-top:2px;" },
  });
}

if (pages.length === 0) {
  readContainer.createEl("div", {
    text: "No books currently in progress.",
    attr: { style: "color:var(--text-muted);font-style:italic;" },
  });
}

const linkWrap = readContainer.createEl("div", {
  attr: { style: "margin-top:12px;font-size:0.85em;" },
});
const bookLink = linkWrap.createEl("a", {
  text: "Open Books Index →",
  cls: "internal-link",
  attr: { style: "cursor:pointer;" },
});
bookLink.addEventListener("click", (e) => {
  e.preventDefault();
  app.commands.executeCommandById(
    "obsidian-weread-plugin:open-weread-bookshelf-view",
  );
});

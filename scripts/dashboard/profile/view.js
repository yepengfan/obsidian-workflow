const app = input.app;
const panels = { card: dv.el("div", "") };
// ========== CARD TAB ==========
const bcPage = dv.page("Profile/Personal Baseball Card");
if (bcPage) {
  // 3D wrapper for perspective
  const cardWrap = panels["card"].createEl("div", {
    attr: {
      style: "width:260px;max-width:100%;margin:0 auto;perspective:600px;",
    },
  });
  const card = cardWrap.createEl("div", {
    attr: {
      style:
        "position:relative;border:1px solid var(--background-modifier-border);border-radius:12px;overflow:hidden;background:#faf6f0;box-shadow:0 2px 6px rgba(0,0,0,0.08);transition:transform 0.15s ease,box-shadow 0.15s ease;transform-style:preserve-3d;will-change:transform;",
    },
  });

  // Header
  const hdr = card.createEl("div", {
    attr: { style: "padding:14px 14px 6px;text-align:center;" },
  });
  const imgFile = app.vault.getAbstractFileByPath("Profile/ted-profile.png");
  if (imgFile) {
    hdr.createEl("img", {
      attr: {
        src: app.vault.getResourcePath(imgFile),
        style:
          "width:48px;height:48px;border-radius:50%;object-fit:cover;object-position:top;border:2px solid var(--background-modifier-border);",
      },
    });
  }
  hdr.createEl("div", {
    text: "Ted Fan",
    attr: { style: "font-size:0.92em;font-weight:800;margin-top:4px;" },
  });
  const bcBadges = hdr.createEl("div", {
    attr: {
      style: "display:flex;justify-content:center;gap:3px;margin-top:3px;",
    },
  });
  bcBadges.createEl("span", {
    text: String(bcPage.mbti || ""),
    attr: {
      style:
        "font-size:0.52em;font-weight:700;padding:1px 4px;border-radius:3px;background:var(--interactive-accent);color:var(--text-on-accent);",
    },
  });
  bcBadges.createEl("span", {
    text: String(bcPage.role || ""),
    attr: {
      style:
        "font-size:0.52em;padding:1px 4px;border-radius:3px;border:1px solid var(--background-modifier-border);color:var(--text-muted);",
    },
  });
  bcBadges.createEl("span", {
    text: "🏆 " + String(bcPage.py_archetype || ""),
    attr: {
      style:
        "font-size:0.52em;padding:1px 4px;border-radius:3px;border:1px solid var(--background-modifier-border);color:var(--text-muted);",
    },
  });
  // Archetype tagline
  hdr.createEl("div", {
    text: "Planful, methodical and results-oriented",
    attr: {
      style:
        "font-size:0.55em;color:var(--text-faint);font-style:italic;margin-top:3px;",
    },
  });

  // Radar chart
  const traits = [
    {
      n: "Deliberative",
      s: "Del",
      v: Number(bcPage.py_deliberative) || 0,
      g: "t",
    },
    { n: "Detailed", s: "Det", v: Number(bcPage.py_detailed) || 0, g: "t" },
    { n: "Creative", s: "Cre", v: Number(bcPage.py_creative) || 0, g: "t" },
    { n: "Conceptual", s: "Con", v: Number(bcPage.py_conceptual) || 0, g: "t" },
    { n: "Leadership", s: "Ldr", v: Number(bcPage.py_leadership) || 0, g: "e" },
    { n: "Tough", s: "Tgh", v: Number(bcPage.py_tough) || 0, g: "e" },
    { n: "Nurturing", s: "Nur", v: Number(bcPage.py_nurturing) || 0, g: "e" },
    {
      n: "Extraverted",
      s: "Ext",
      v: Number(bcPage.py_extraverted) || 0,
      g: "e",
    },
    { n: "Composed", s: "Cmp", v: Number(bcPage.py_composed) || 0, g: "a" },
    { n: "Determined", s: "Dtr", v: Number(bcPage.py_determined) || 0, g: "a" },
    { n: "Humble", s: "Hum", v: Number(bcPage.py_humble) || 0, g: "a" },
    { n: "Autonomous", s: "Aut", v: Number(bcPage.py_autonomous) || 0, g: "a" },
  ];
  const gCol = { t: "#2ba5a5", e: "#8b6bae", a: "#c4953a" };
  const sz = 240,
    rcx = sz / 2,
    rcy = sz / 2,
    RR = 72;
  const NN = traits.length,
    rstep = (2 * Math.PI) / NN;
  const rpt = (i, pct) => {
    const a = -Math.PI / 2 + i * rstep;
    return [
      rcx + (pct / 100) * RR * Math.cos(a),
      rcy + (pct / 100) * RR * Math.sin(a),
    ];
  };
  let svg = `<svg viewBox="0 0 ${sz} ${sz}" style="width:100%;max-width:220px;display:block;margin:0 auto;">`;
  for (const p of [25, 50, 75, 100])
    svg += `<circle cx="${rcx}" cy="${rcy}" r="${(p / 100) * RR}" fill="none" stroke="var(--background-modifier-border)" stroke-width="0.5"/>`;
  for (let i = 0; i < NN; i++) {
    const [x, y] = rpt(i, 100);
    svg += `<line x1="${rcx}" y1="${rcy}" x2="${x}" y2="${y}" stroke="var(--background-modifier-border)" stroke-width="0.3"/>`;
  }
  const polyPts = traits.map((t, i) => rpt(i, t.v).join(",")).join(" ");
  // Glow filter for radar polygon
  svg += `<defs><filter id="radarGlow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>`;
  svg += `<polygon points="${polyPts}" fill="rgba(58,154,92,0.12)" stroke="#3a9a5c" stroke-width="1.8" stroke-linejoin="round" filter="url(#radarGlow)"/>`;
  traits.forEach((t, i) => {
    const [x, y] = rpt(i, t.v);
    const c = t.v >= 70 ? "#3a9a5c" : t.v >= 40 ? "#999" : "#c75c5c";
    svg += `<circle cx="${x}" cy="${y}" r="3.5" fill="${c}" stroke="var(--background-primary)" stroke-width="1"><title>${t.n}: ${t.v}%</title></circle>`;
  });
  // Trait labels around the outside
  traits.forEach((t, i) => {
    const [x, y] = rpt(i, 130);
    const col = gCol[t.g];
    svg += `<text x="${x}" y="${y}" text-anchor="middle" dominant-baseline="central" font-size="6.5" font-weight="600" fill="${col}" opacity="0.8"><title>${t.n}: ${t.v}%</title>${t.s}</text>`;
  });
  svg += "</svg>";
  const chartEl = card.createEl("div", {
    attr: {
      style:
        "padding:6px 8px 2px;border-top:1px solid var(--background-modifier-border);",
    },
  });
  chartEl.innerHTML = svg;

  // Summary
  card.createEl("div", {
    text: "Strong thinker & executor · Low social engagement",
    attr: {
      style:
        "padding:2px 14px 0;text-align:center;font-size:0.58em;color:var(--text-faint);line-height:1.4;",
    },
  });

  // Footer: date + link
  const footer = card.createEl("div", {
    attr: {
      style:
        "padding:6px 14px 10px;display:flex;justify-content:space-between;align-items:center;",
    },
  });
  footer.createEl("span", {
    text: bcPage.py_date ? dv.date(bcPage.py_date).toFormat("MMM yyyy") : "",
    attr: { style: "font-size:0.55em;color:var(--text-faint);" },
  });
  footer.createEl("span", { attr: { style: "font-size:0.7em;" } }).innerHTML =
    '<a class="internal-link" data-href="Profile/Personal Baseball Card">Open Card →</a>';

  // === HOLOGRAPHIC EFFECT (mouse + touch) ===
  function applyHoloEffect(clientX, clientY) {
    const rect = card.getBoundingClientRect();
    const px = (clientX - rect.left) / rect.width;
    const py = (clientY - rect.top) / rect.height;
    const rotY = (px - 0.5) * 20;
    const rotX = (0.5 - py) * 20;
    const hue = Math.round(px * 360);
    const cx = px * 100,
      cy = py * 100;

    card.style.transform = `rotateY(${rotY}deg) rotateX(${rotX}deg)`;
    card.style.boxShadow = [
      `${-rotY * 0.5}px ${rotX * 0.5}px 15px rgba(0,0,0,0.1)`,
      `${-rotY * 0.8}px ${rotX * 0.8}px 30px hsla(${hue}, 60%, 65%, 0.15)`,
      `${-rotY * 0.3}px ${rotX * 0.3}px 8px hsla(${(hue + 120) % 360}, 50%, 70%, 0.1)`,
    ].join(",");

    const edgeHue = (hue + 60) % 360;
    card.style.borderColor = `hsla(${edgeHue}, 70%, 75%, 0.5)`;
    card.style.borderWidth = "1px";
    const side = px > 0.5 ? "Right" : "Left";
    card.style[`border${side}Color`] = `hsla(${edgeHue}, 80%, 80%, 0.8)`;

    card.style.backgroundImage = [
      `radial-gradient(circle at ${cx}% ${cy}%, rgba(255,255,255,0.35) 0%, transparent 45%)`,
      `conic-gradient(from ${(px - 0.5) * 180}deg at ${cx}% ${cy}%, rgba(255,50,50,0.12), rgba(255,180,50,0.12), rgba(50,255,100,0.12), rgba(50,180,255,0.12), rgba(180,50,255,0.12), rgba(255,50,150,0.12), rgba(255,50,50,0.12))`,
      `repeating-linear-gradient(${135 + (px - 0.5) * 20}deg, transparent 0px, transparent 2px, rgba(255,255,255,0.06) 2px, rgba(255,255,255,0.06) 3px)`,
    ].join(",");
    card.style.backgroundColor = "#faf6f0";
  }

  let isFirstMove = false;
  let floatTimer = null;
  function startInteraction() {
    if (floatTimer) {
      clearTimeout(floatTimer);
      floatTimer = null;
    }
    card.style.animation = "none";
    card.style.transform = "rotateY(0deg) rotateX(0deg)";
    card.style.transition = "none";
    void card.offsetHeight;
    card.style.transition = "transform 0.1s ease, box-shadow 0.1s ease";
    isFirstMove = true;
  }

  function endInteraction() {
    isFirstMove = false;
    card.style.transition =
      "transform 0.5s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.4s ease, border-color 0.4s ease, background-image 0.4s ease";
    card.style.transform = "rotateY(0deg) rotateX(0deg)";
    card.style.boxShadow = "0 2px 6px rgba(0,0,0,0.08)";
    card.style.borderColor = "var(--background-modifier-border)";
    card.style.borderLeftColor = "var(--background-modifier-border)";
    card.style.borderRightColor = "var(--background-modifier-border)";
    card.style.backgroundImage = "none";
    floatTimer = setTimeout(() => {
      card.style.animation = "bc-float 4s ease-in-out infinite";
      floatTimer = null;
    }, 600);
  }

  // Mouse events
  cardWrap.addEventListener("mousemove", (e) => {
    if (isFirstMove) {
      isFirstMove = false;
      requestAnimationFrame(() => applyHoloEffect(e.clientX, e.clientY));
    } else {
      applyHoloEffect(e.clientX, e.clientY);
    }
  });
  cardWrap.addEventListener("mouseenter", startInteraction);
  cardWrap.addEventListener("mouseleave", (e) => {
    const rect = cardWrap.getBoundingClientRect();
    if (
      e.clientX >= rect.left &&
      e.clientX <= rect.right &&
      e.clientY >= rect.top &&
      e.clientY <= rect.bottom
    ) {
      return;
    }
    endInteraction();
  });

  // Touch events - only on card body, not footer links
  let touching = false;
  cardWrap.addEventListener(
    "touchstart",
    (e) => {
      if (e.target.closest("a")) return; // let links work normally
      touching = true;
      startInteraction();
      const t = e.touches[0];
      applyHoloEffect(t.clientX, t.clientY);
    },
    { passive: true },
  );
  cardWrap.addEventListener(
    "touchmove",
    (e) => {
      if (!touching) return;
      e.preventDefault();
      const t = e.touches[0];
      applyHoloEffect(t.clientX, t.clientY);
    },
    { passive: false },
  );
  cardWrap.addEventListener("touchend", () => {
    if (!touching) return;
    touching = false;
    endInteraction();
  });

  // Idle breathing animation
  const breatheId = "bc-breathe";
  if (!document.getElementById(breatheId)) {
    const s = document.createElement("style");
    s.id = breatheId;
    s.textContent = `@keyframes bc-float{0%,100%{transform:translateY(0px)}50%{transform:translateY(-3px)}}`;
    document.head.appendChild(s);
  }
  card.style.animation = "bc-float 4s ease-in-out infinite";
}

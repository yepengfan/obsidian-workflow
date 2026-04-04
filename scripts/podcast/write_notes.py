#!/usr/bin/env python3
"""Step 3: Generate Obsidian notes from enriched podcast episode data.

Reads enriched.json from TMPDIR_PODCAST, then:
  - Writes individual episode notes to Podcasts/episodes/{slug}.md
  - Refreshes the Podcasts/Podcasts.md recommendation dashboard
  - Updates scripts/podcast/state.json with newly processed GUIDs

Existing episode notes are NOT overwritten (idempotent per-episode).

Environment variables:
  TMPDIR_PODCAST  — directory containing enriched.json
  VAULT_DIR       — absolute path to the Obsidian vault root
  TODAY           — ISO date string (YYYY-MM-DD)
"""

import json
import os
import sys
from pathlib import Path


# ── Config ────────────────────────────────────────────────────────────

SCORE_GROUPS = [
    (9, 10, "⭐ Strongly Recommended (9-10)"),
    (7, 8,  "👍 Worth Listening (7-8)"),
    (5, 6,  "📋 Optional (5-6)"),
    (0, 4,  "⏭️ Skip (<5)"),
]


# ── Paragraph-grouped transcript (dataviewjs) ────────────────────────
# Groups SRT segments into natural paragraphs based on speech pauses.
# Supports persistent highlights stored in frontmatter.

DATAVIEWJS_TRANSCRIPT = r"""```dataviewjs
// ── Podcast Transcript (paragraph view) ─────────────────────────
// Groups SRT segments into natural paragraphs. Click to seek,
// hover for highlight button. Highlights persist in frontmatter.

const slug = dv.current().file.name;
const srtPath = `Podcasts/audio/${slug}.srt`;
const srtFile = app.vault.getAbstractFileByPath(srtPath);
if (!srtFile) { dv.paragraph("_No transcript file found._"); return; }

const raw = await app.vault.read(srtFile);
const segs = [];
for (const block of raw.trim().split(/\n\n+/)) {
  const lines = block.split('\n');
  if (lines.length < 3) continue;
  const m = lines[1].match(/(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})/);
  if (!m) continue;
  const start = +m[1]*3600 + +m[2]*60 + +m[3] + +m[4]/1000;
  const end   = +m[5]*3600 + +m[6]*60 + +m[7] + +m[8]/1000;
  const text  = lines.slice(2).join(' ').trim();
  if (text) segs.push({ start, end, text });
}
if (!segs.length) { dv.paragraph("_Transcript is empty._"); return; }

// ── Group segments into paragraphs ──────────────────────────────
// New paragraph when: gap > 1.5s between segments, or duration > 35s
const paras = [];
let cur = { segs: [segs[0]] };
for (let i = 1; i < segs.length; i++) {
  const gap = segs[i].start - segs[i - 1].end;
  const dur = segs[i].start - cur.segs[0].start;
  if (gap > 1.5 || dur > 35) {
    paras.push(cur);
    cur = { segs: [segs[i]] };
  } else {
    cur.segs.push(segs[i]);
  }
}
paras.push(cur);

// Build paragraph metadata
for (const p of paras) {
  p.start = p.segs[0].start;
  p.end = p.segs[p.segs.length - 1].end;
  p.text = p.segs.map(s => s.text).join(' ');
}

// Highlights from frontmatter
const hlRaw = dv.current().highlights || [];
const hlSet = new Set(Array.from(hlRaw).map(String));

function fmtTs(sec) {
  const hh = Math.floor(sec / 3600);
  const mm = String(Math.floor((sec % 3600) / 60)).padStart(2, '0');
  const ss = String(Math.floor(sec % 60)).padStart(2, '0');
  return hh > 0 ? `${hh}:${mm}:${ss}` : `${+mm}:${ss}`;
}
function fmtTsFull(sec) {
  const hh = String(Math.floor(sec / 3600)).padStart(2, '0');
  const mm = String(Math.floor((sec % 3600) / 60)).padStart(2, '0');
  const ss = String(Math.floor(sec % 60)).padStart(2, '0');
  return `${hh}:${mm}:${ss}`;
}

// Inject inline styles (mobile fallback — keep in sync with podcast-transcript.css)
if (!document.getElementById('tx-inline-css')) {
  const s = document.createElement('style');
  s.id = 'tx-inline-css';
  s.textContent = `
    .podcast-transcript { max-height:70vh; overflow-y:auto; scroll-behavior:smooth;
      padding:16px 24px; background:var(--background-primary);
      border:1px solid var(--background-modifier-border); border-radius:var(--radius-m); }
    .tx-para { position:relative; padding:8px 12px; margin-bottom:4px;
      border-left:3px solid transparent; border-radius:0 var(--radius-s) var(--radius-s) 0;
      cursor:pointer; transition:background-color .2s,border-color .2s; }
    .tx-para:hover { background:var(--background-modifier-hover); }
    .tx-para-body { color:var(--text-normal); line-height:1.8; }
    .tx-para-ts { display:inline-block; font-family:var(--font-monospace);
      font-size:var(--font-ui-smaller); color:var(--text-faint);
      background:var(--background-secondary); padding:1px 6px;
      border-radius:var(--radius-s); margin-right:8px; user-select:none; vertical-align:baseline; }
    .tx-para.tx-active { background:color-mix(in srgb,var(--interactive-accent) 8%,transparent);
      border-left-color:var(--interactive-accent); }
    .tx-para.tx-active .tx-para-ts { color:var(--interactive-accent);
      background:color-mix(in srgb,var(--interactive-accent) 12%,transparent);
      font-weight:600; }
    .tx-para.tx-highlight { background:color-mix(in srgb,#f59e0b 10%,transparent);
      border-left-color:#f59e0b; }
    .tx-para.tx-highlight:hover { background:color-mix(in srgb,#f59e0b 16%,transparent); }
    .tx-para.tx-highlight.tx-active { background:color-mix(in srgb,#f59e0b 13%,transparent);
      border-left-color:#f59e0b; }
    .tx-para.tx-highlight .tx-para-ts { color:#b45309;
      background:color-mix(in srgb,#f59e0b 15%,transparent); }
    .tx-hl-btn { position:absolute; top:8px; right:8px; width:26px; height:26px;
      display:flex; align-items:center; justify-content:center; border:none;
      border-radius:var(--radius-s); background:transparent; cursor:pointer;
      opacity:0; transition:opacity .15s; font-size:14px; padding:0;
      line-height:1; user-select:none; z-index:1; }
    .tx-para:hover .tx-hl-btn { opacity:.4; }
    .tx-para:hover .tx-hl-btn:hover { opacity:1; background:var(--background-modifier-hover); }
    .tx-para.tx-highlight .tx-hl-btn { opacity:.7; }
    .tx-notice { text-align:center; padding:16px; color:var(--text-muted);
      font-size:var(--font-ui-smaller); font-style:italic; }`;
  document.head.appendChild(s);
}

const scrollKey = `tx-scroll-${slug}`;
const ct = dv.container.createEl("div", { cls: "podcast-transcript" });

const paraEls = paras.map((p, i) => {
  const tsKey = fmtTsFull(p.start);
  const isHL = hlSet.has(tsKey);
  const el = ct.createEl("div", {
    cls: "tx-para" + (isHL ? " tx-highlight" : ""),
    attr: { "data-i": String(i), "data-ts": tsKey }
  });
  const body = el.createEl("div", { cls: "tx-para-body" });
  body.createEl("span", { cls: "tx-para-ts", text: fmtTs(p.start) });
  body.appendText(p.text);
  const btn = el.createEl("button", { cls: "tx-hl-btn", text: isHL ? "\u25CF" : "\u25CB" });
  btn.addEventListener("click", async (e) => {
    e.stopPropagation();
    const wasHL = el.classList.contains("tx-highlight");
    el.classList.toggle("tx-highlight");
    btn.textContent = wasHL ? "\u25CB" : "\u25CF";
    sessionStorage.setItem(scrollKey, String(ct.scrollTop));
    const file = app.vault.getAbstractFileByPath(dv.current().file.path);
    await app.fileManager.processFrontMatter(file, (fm) => {
      if (!fm.highlights) fm.highlights = [];
      if (wasHL) {
        fm.highlights = fm.highlights.filter(h => String(h) !== tsKey);
      } else {
        fm.highlights.push(tsKey);
        fm.highlights.sort();
      }
    });
  });
  return el;
});

// Restore scroll position after frontmatter-triggered re-render
const saved = sessionStorage.getItem(scrollKey);
if (saved) {
  requestAnimationFrame(() => { ct.scrollTop = parseFloat(saved); });
  sessionStorage.removeItem(scrollKey);
}

// Find <audio>: Media Extended (desktop) → native embed (mobile)
function findAudio() {
  const view = ct.closest('.markdown-preview-view') || ct.closest('.view-content');
  if (view) {
    const host = view.querySelector('.mx-media-embed .mx-player-shadow-root');
    if (host?.shadowRoot) {
      const el = host.shadowRoot.querySelector('audio') || host.shadowRoot.querySelector('video');
      if (el) return el;
    }
  }
  const scope = view || ct.closest('.workspace-leaf') || document;
  return scope.querySelector('.internal-embed audio') || scope.querySelector('audio');
}

let audio = findAudio();
if (!audio) {
  await new Promise(resolve => {
    let tries = 0;
    const iv = setInterval(() => {
      audio = findAudio();
      if (audio || ++tries > 20) { clearInterval(iv); resolve(); }
    }, 500);
  });
}
if (!audio) {
  ct.createEl("div", { cls: "tx-notice", text: "Audio player not detected \u2014 transcript is read-only." });
}

// Sync: highlight active paragraph + auto-scroll
if (audio) {
  let activeIdx = -1;
  audio.addEventListener("timeupdate", () => {
    const t = audio.currentTime;
    let idx = -1;
    for (let i = paras.length - 1; i >= 0; i--) {
      if (paras[i].start <= t) { idx = i; break; }
    }
    if (idx === activeIdx) return;
    if (activeIdx >= 0 && paraEls[activeIdx]) paraEls[activeIdx].removeClass("tx-active");
    if (idx >= 0 && paraEls[idx]) {
      paraEls[idx].addClass("tx-active");
      paraEls[idx].scrollIntoView({ behavior: "smooth", block: "center" });
    }
    activeIdx = idx;
  });
}

// Click-to-seek (ignore highlight button clicks)
ct.addEventListener("click", (e) => {
  if (e.target.closest(".tx-hl-btn")) return;
  const para = e.target.closest(".tx-para");
  if (!para || !audio) return;
  const i = +para.dataset.i;
  if (isNaN(i) || !paras[i]) return;
  audio.currentTime = paras[i].start;
  if (audio.paused) audio.play();
});
```"""


# ── Highlights summary (dataviewjs) ──────────────────────────────────

DATAVIEWJS_HIGHLIGHTS = r"""```dataviewjs
// ── Highlights Summary ──────────────────────────────────────────
// Shows highlighted transcript paragraphs as a quick-reference list.

const slug = dv.current().file.name;
const hlRaw = dv.current().highlights || [];
if (!hlRaw.length) {
  dv.paragraph("_No highlights yet \u2014 click \u25CB on transcript paragraphs to highlight._");
  return;
}

const srtPath = `Podcasts/audio/${slug}.srt`;
const srtFile = app.vault.getAbstractFileByPath(srtPath);
if (!srtFile) { dv.paragraph("_No transcript file found._"); return; }

const raw = await app.vault.read(srtFile);
const segs = [];
for (const block of raw.trim().split(/\n\n+/)) {
  const lines = block.split('\n');
  if (lines.length < 3) continue;
  const m = lines[1].match(/(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})/);
  if (!m) continue;
  const start = +m[1]*3600 + +m[2]*60 + +m[3] + +m[4]/1000;
  const end   = +m[5]*3600 + +m[6]*60 + +m[7] + +m[8]/1000;
  const text  = lines.slice(2).join(' ').trim();
  if (text) segs.push({ start, end, text });
}

// Rebuild paragraphs (same grouping as transcript)
const paras = [];
let cur = { segs: [segs[0]] };
for (let i = 1; i < segs.length; i++) {
  const gap = segs[i].start - segs[i - 1].end;
  const dur = segs[i].start - cur.segs[0].start;
  if (gap > 1.5 || dur > 35) { paras.push(cur); cur = { segs: [segs[i]] }; }
  else { cur.segs.push(segs[i]); }
}
paras.push(cur);
for (const p of paras) {
  p.start = p.segs[0].start;
  p.text = p.segs.map(s => s.text).join(' ');
}

const hlSet = new Set(Array.from(hlRaw).map(String));
function fmtTsFull(sec) {
  const hh = String(Math.floor(sec / 3600)).padStart(2, '0');
  const mm = String(Math.floor((sec % 3600) / 60)).padStart(2, '0');
  const ss = String(Math.floor(sec % 60)).padStart(2, '0');
  return `${hh}:${mm}:${ss}`;
}
function fmtTs(sec) {
  const hh = Math.floor(sec / 3600);
  const mm = String(Math.floor((sec % 3600) / 60)).padStart(2, '0');
  const ss = String(Math.floor(sec % 60)).padStart(2, '0');
  return hh > 0 ? `${hh}:${mm}:${ss}` : `${+mm}:${ss}`;
}

const matched = paras.filter(p => hlSet.has(fmtTsFull(p.start)));
if (!matched.length) { dv.paragraph("_Highlights not found in transcript._"); return; }

if (!document.getElementById('tx-hl-summary-css')) {
  const s = document.createElement('style');
  s.id = 'tx-hl-summary-css';
  s.textContent = `
    .tx-highlights-summary { padding:8px 0; }
    .tx-hl-count { color:var(--text-muted); font-size:var(--font-ui-smaller);
      padding-bottom:8px; }
    .tx-hl-item { padding:8px 12px; border-left:3px solid #f59e0b; margin-bottom:8px;
      cursor:pointer; border-radius:0 var(--radius-s) var(--radius-s) 0;
      transition:background-color .15s; }
    .tx-hl-item:hover { background:color-mix(in srgb,#f59e0b 10%,transparent); }
    .tx-hl-item .tx-hl-ts { display:inline-block; font-family:var(--font-monospace);
      font-size:var(--font-ui-smaller); color:#b45309;
      background:color-mix(in srgb,#f59e0b 10%,transparent); padding:1px 6px;
      border-radius:var(--radius-s); margin-right:8px; margin-bottom:4px; user-select:none; }
    .tx-hl-item .tx-hl-text { color:var(--text-normal); line-height:1.7; }`;
  document.head.appendChild(s);
}

const ct = dv.container.createEl("div", { cls: "tx-highlights-summary" });
ct.createEl("div", { cls: "tx-hl-count",
  text: `${matched.length} highlighted paragraph${matched.length > 1 ? 's' : ''}` });

for (const p of matched) {
  const item = ct.createEl("div", { cls: "tx-hl-item", attr: { "data-start": String(p.start) } });
  const body = item.createEl("div");
  body.createEl("span", { cls: "tx-hl-ts", text: fmtTs(p.start) });
  body.createEl("span", { cls: "tx-hl-text", text: p.text });
}

// Click to seek audio
function findAudio() {
  const view = ct.closest('.markdown-preview-view') || ct.closest('.view-content');
  if (view) {
    const host = view.querySelector('.mx-media-embed .mx-player-shadow-root');
    if (host?.shadowRoot) {
      const el = host.shadowRoot.querySelector('audio') || host.shadowRoot.querySelector('video');
      if (el) return el;
    }
  }
  const scope = view || ct.closest('.workspace-leaf') || document;
  return scope.querySelector('.internal-embed audio') || scope.querySelector('audio');
}
ct.addEventListener("click", (e) => {
  const item = e.target.closest(".tx-hl-item");
  if (!item) return;
  const start = parseFloat(item.dataset.start);
  if (isNaN(start)) return;
  const audio = findAudio();
  if (!audio) return;
  audio.currentTime = start;
  if (audio.paused) audio.play();
});
```"""


# ── Episode note generation ───────────────────────────────────────────

def build_episode_note(ep: dict) -> str:
    """Render a complete Obsidian episode note as a markdown string."""
    slug = ep.get("slug", "unknown")
    podcast_name = ep.get("podcast_name", "").replace('"', '\\"')
    episode_number = ep.get("episode_number", "").replace('"', '\\"')
    title = ep.get("title", "Untitled").replace('"', '\\"')
    publish_date = ep.get("publish_date", ep.get("date", ""))
    duration = ep.get("duration", "")
    score = ep.get("score", 0)
    summary_zh = ep.get("summary_zh", "")
    summary_en = ep.get("summary_en", "")
    takeaways = ep.get("takeaways", [])
    zettel_candidates = ep.get("zettel_candidates", [])
    transcript_segments = ep.get("transcript_segments", [])

    # Tags: always include "podcast" plus episode-specific tags
    ep_tags = ep.get("tags", [])
    all_tags = ["podcast"] + [t for t in ep_tags if t != "podcast"]
    tags_yaml = "[" + ", ".join(all_tags) + "]"

    # Takeaways as bullet list
    if takeaways:
        takeaways_md = "\n".join(f"- {t}" for t in takeaways)
    else:
        takeaways_md = "_No takeaways generated._"

    # Zettel candidates as bullet list inside a tip callout
    if zettel_candidates:
        zettel_items = "\n".join(f"> - {z}" for z in zettel_candidates)
        zettel_md = f"> [!tip] 可转化为 Zettel 的观点\n{zettel_items}"
    else:
        zettel_md = "> [!tip] 可转化为 Zettel 的观点\n> _No Zettel candidates identified._"

    # Transcript section — dynamic dataviewjs block if transcript exists
    has_transcript = bool(transcript_segments)

    note = f"""---
type: podcast-episode
podcast: "{podcast_name}"
episode: "{episode_number}"
title: "{title}"
date: {publish_date}
duration: "{duration}"
score: {score}
status: unlistened
listened_date:
archived_date:
audio: "[[Podcasts/audio/{slug}.mp3]]"
highlights:
tags: {tags_yaml}
---

# {title}

## Summary

> [!abstract]
> {summary_zh}
>
> {summary_en}

## Key Takeaways

{takeaways_md}

## Zettel Candidates

{zettel_md}

## Audio

![[Podcasts/audio/{slug}.mp3]]

## Transcript

{DATAVIEWJS_TRANSCRIPT if has_transcript else "_No transcript available._"}

## Highlights

{DATAVIEWJS_HIGHLIGHTS if has_transcript else "_No transcript available._"}

## My Notes

> ✍️ Write your thoughts here...
"""
    return note


# ── Dashboard generation ──────────────────────────────────────────────

def build_score_table(episodes: list) -> str:
    """Build grouped score sections for the Podcasts.md dashboard."""
    sections = []

    for min_score, max_score, heading in SCORE_GROUPS:
        group = [
            ep for ep in episodes
            if min_score <= ep.get("score", 0) <= max_score
        ]
        # Sort descending by score within each group
        group.sort(key=lambda ep: ep.get("score", 0), reverse=True)

        if not group:
            continue

        rows = []
        for ep in group:
            slug = ep.get("slug", "unknown")
            podcast_name = ep.get("podcast_name", "")
            title = ep.get("title", "Untitled")
            score = ep.get("score", 0)
            duration = ep.get("duration", "")
            summary_en = ep.get("summary_en", ep.get("summary_zh", ""))
            rows.append(
                f"| {podcast_name} | [[Podcasts/episodes/{slug}\\|{title}]] "
                f"| {score} | {duration} | {summary_en} |"
            )

        table = (
            "| Podcast | Episode | Score | Duration | Summary |\n"
            "|---------|---------|:-----:|----------|----------|\n"
            + "\n".join(rows)
        )
        sections.append(f"### {heading}\n\n{table}")

    return "\n\n".join(sections) if sections else "_No episodes._"


def build_podcasts_dashboard(episodes: list, today: str) -> str:
    """Render the full Podcasts.md dashboard markdown."""
    count = len(episodes)
    score_sections = build_score_table(episodes)

    recently_listened_dv = """\
```dataviewjs
const pages = dv.pages('"Podcasts/episodes"')
  .where(p => p.status === "listened")
  .sort(p => p.listened_date, "desc")
  .limit(10);
dv.table(
  ["Episode", "Podcast", "Score", "Listened"],
  pages.map(p => [p.file.link, p.podcast, p.score, p.listened_date])
);
```"""

    stats_dv = """\
```dataviewjs
const pages = dv.pages('"Podcasts/episodes"');
const counts = {unlistened: 0, listened: 0, archived: 0};
for (const p of pages) {
  const s = p.status || "unlistened";
  counts[s] = (counts[s] || 0) + 1;
}
dv.paragraph(
  `📥 Unlistened: **${counts.unlistened}** | ` +
  `✅ Listened: **${counts.listened}** | ` +
  `🗄️ Archived: **${counts.archived}**`
);
```"""

    dashboard = f"""---
type: dashboard
---

# Podcast Feed

## New Episodes

> [!tip] 上次更新：{today} | 共 {count} 期新内容

{score_sections}

## Recently Listened

{recently_listened_dv}

## Stats

{stats_dv}
"""
    return dashboard


# ── State management ──────────────────────────────────────────────────

def load_state(state_path: Path) -> dict:
    """Load state.json or return empty structure."""
    if state_path.exists():
        try:
            return json.loads(state_path.read_text())
        except (json.JSONDecodeError, OSError):
            print("[write] Warning: state.json corrupted, starting fresh.", file=sys.stderr)
    return {"processed": {}}


def save_state(state_path: Path, state: dict) -> None:
    """Persist state.json."""
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))


# ── Main ─────────────────────────────────────────────────────────────

def main() -> None:
    tmpdir = os.environ["TMPDIR_PODCAST"]
    today = os.environ["TODAY"]
    vault_dir = Path(os.environ["VAULT_DIR"])

    # Paths
    enriched_path = Path(tmpdir) / "enriched.json"
    episodes_dir = vault_dir / "Podcasts" / "episodes"
    podcasts_md = vault_dir / "Podcasts" / "Podcasts.md"
    state_path = Path(__file__).parent / "state.json"

    # Ensure output directories exist
    episodes_dir.mkdir(parents=True, exist_ok=True)
    (vault_dir / "Podcasts").mkdir(parents=True, exist_ok=True)

    # Load enriched data
    enriched_data = json.loads(enriched_path.read_text())
    if isinstance(enriched_data, list):
        episodes = enriched_data
    else:
        episodes = enriched_data.get("episodes", [])

    if not episodes:
        print("[write] No episodes to write.", file=sys.stderr)
        return

    print(f"[write] Writing {len(episodes)} episode notes...", file=sys.stderr)

    # Load state
    state = load_state(state_path)
    processed = state.setdefault("processed", {})

    written = 0
    skipped = 0

    for ep in episodes:
        slug = ep.get("slug", "unknown")
        guid = ep.get("guid", slug)
        note_path = episodes_dir / f"{slug}.md"

        # Do not overwrite existing notes (idempotent)
        if note_path.exists():
            print(f"[write] Skipping existing note: {slug}", file=sys.stderr)
            skipped += 1
            # Still record in state if missing
            if guid not in processed:
                processed[guid] = {"date": today, "slug": slug}
            continue

        # Write episode note
        note_content = build_episode_note(ep)
        note_path.write_text(note_content, encoding="utf-8")
        written += 1

        # Update state
        processed[guid] = {"date": today, "slug": slug}

    # Refresh Podcasts.md dashboard
    dashboard_content = build_podcasts_dashboard(episodes, today)
    podcasts_md.write_text(dashboard_content, encoding="utf-8")
    print(f"[write] Updated Podcasts.md", file=sys.stderr)

    # Persist state
    save_state(state_path, state)

    print(
        f"[write] Done — wrote {written} notes, skipped {skipped} existing.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()

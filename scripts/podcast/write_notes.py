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


# ── Synced transcript (dataviewjs) ────────────────────────────────────

DATAVIEWJS_TRANSCRIPT = r"""```dataviewjs
// ── Synced Podcast Transcript ──────────────────────────────────
// Reads .srt, syncs highlight to audio playback, click-to-seek.

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

const ct = dv.container.createEl("div", { cls: "podcast-transcript" });
const segEls = segs.map((seg, i) => {
  const row = ct.createEl("div", { cls: "tx-seg", attr: { "data-i": String(i) } });
  const hh = String(Math.floor(seg.start / 3600)).padStart(2, '0');
  const mm = String(Math.floor((seg.start % 3600) / 60)).padStart(2, '0');
  const ss = String(Math.floor(seg.start % 60)).padStart(2, '0');
  row.createEl("span", { cls: "tx-ts", text: `${hh}:${mm}:${ss}` });
  row.createEl("span", { cls: "tx-text", text: seg.text });
  return row;
});

// Find <audio> inside Media Extended's open shadow DOM
function findAudio() {
  const view = ct.closest('.markdown-preview-view') || ct.closest('.view-content');
  if (!view) return null;
  const host = view.querySelector('.mx-media-embed .mx-player-shadow-root');
  if (!host?.shadowRoot) return null;
  return host.shadowRoot.querySelector('audio') || host.shadowRoot.querySelector('video');
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
  ct.createEl("div", { cls: "tx-notice", text: "Audio player not detected — transcript is read-only." });
}

// Sync: highlight active segment + auto-scroll
if (audio) {
  let activeIdx = -1;
  audio.addEventListener("timeupdate", () => {
    const t = audio.currentTime;
    // Binary search for the last segment whose start <= t
    let lo = 0, hi = segs.length - 1, idx = -1;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      if (segs[mid].start <= t) { idx = mid; lo = mid + 1; } else { hi = mid - 1; }
    }
    if (idx === activeIdx) return;
    if (activeIdx >= 0 && segEls[activeIdx]) segEls[activeIdx].removeClass("tx-active");
    if (idx >= 0 && segEls[idx]) {
      segEls[idx].addClass("tx-active");
      segEls[idx].scrollIntoView({ behavior: "smooth", block: "center" });
    }
    activeIdx = idx;
  });
}

// Click-to-seek
ct.addEventListener("click", (e) => {
  const row = e.target.closest(".tx-seg");
  if (!row || !audio) return;
  const i = +row.dataset.i;
  if (isNaN(i) || !segs[i]) return;
  audio.currentTime = segs[i].start;
  if (audio.paused) audio.play();
});
```"""


# ── Episode note generation ───────────────────────────────────────────

def build_episode_note(ep: dict) -> str:
    """Render a complete Obsidian episode note as a markdown string."""
    slug = ep.get("slug", "unknown")
    podcast_name = ep.get("podcast_name", "")
    episode_number = ep.get("episode_number", "")
    title = ep.get("title", "Untitled")
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

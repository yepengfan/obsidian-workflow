#!/usr/bin/env python3
"""Podcast lifecycle management — archive and clean up old audio files.

Scans Podcasts/audio/ for .mp3 files, reads the corresponding episode note's
frontmatter to determine status and dates, then applies lifecycle rules:

  1. listened + 30 days → move audio to archive/, set status=archived
  2. archived + 90 days → delete audio file (keep .srt + episode note)

Also auto-fills listened_date if status=listened but listened_date is empty.

Usage:
    python lifecycle.py [--vault-path /path/to/vault]
"""

import argparse
import json
import re
import shutil
import sys
from datetime import date, timedelta
from pathlib import Path

ARCHIVE_AFTER_DAYS = 30   # listened → archived
DELETE_AFTER_DAYS = 90     # archived → audio deleted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Podcast lifecycle management")
    script_dir = Path(__file__).parent
    default_vault = script_dir.parent.parent
    parser.add_argument("--vault-path", default=str(default_vault), help="Obsidian vault path")
    return parser.parse_args()


def parse_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from a markdown file as a dict."""
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}

    fm = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value:
                fm[key] = value
    return fm


def update_frontmatter_field(filepath: Path, field: str, value: str) -> None:
    """Update a single frontmatter field in a markdown file."""
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return

    fm_text = match.group(1)
    # Check if field exists
    pattern = re.compile(rf"^{re.escape(field)}:.*$", re.MULTILINE)
    if pattern.search(fm_text):
        new_fm = pattern.sub(f"{field}: {value}", fm_text)
    else:
        new_fm = fm_text + f"\n{field}: {value}"

    new_text = f"---\n{new_fm}\n---{text[match.end():]}"
    filepath.write_text(new_text, encoding="utf-8")


def find_episode_note(slug: str, episodes_dir: Path) -> Path | None:
    """Find the episode note for a given audio slug."""
    note_path = episodes_dir / f"{slug}.md"
    if note_path.exists():
        return note_path
    return None


def main() -> None:
    args = parse_args()
    vault = Path(args.vault_path)
    audio_dir = vault / "Podcasts" / "audio"
    archive_dir = audio_dir / "archive"
    episodes_dir = vault / "Podcasts" / "episodes"
    today = date.today()

    if not audio_dir.exists():
        print("[lifecycle] No audio directory found. Nothing to do.", file=sys.stderr)
        return

    archive_dir.mkdir(parents=True, exist_ok=True)

    archived_count = 0
    deleted_count = 0
    autofilled_count = 0

    # Process .mp3 files in main audio directory
    for mp3 in sorted(audio_dir.glob("*.mp3")):
        slug = mp3.stem
        note = find_episode_note(slug, episodes_dir)

        if not note:
            continue

        fm = parse_frontmatter(note)
        status = fm.get("status", "unlistened")

        # Auto-fill listened_date if missing
        if status == "listened" and not fm.get("listened_date"):
            update_frontmatter_field(note, "listened_date", today.isoformat())
            autofilled_count += 1
            print(f"[lifecycle]   Auto-filled listened_date for {slug}", file=sys.stderr)
            fm["listened_date"] = today.isoformat()

        # Archive: listened + 30 days
        if status == "listened" and fm.get("listened_date"):
            listened_date = date.fromisoformat(fm["listened_date"])
            days_since = (today - listened_date).days
            if days_since >= ARCHIVE_AFTER_DAYS:
                # Move mp3 to archive
                dest = archive_dir / mp3.name
                shutil.move(str(mp3), str(dest))
                # Also move .srt if it exists
                srt = mp3.with_suffix(".srt")
                if srt.exists():
                    shutil.move(str(srt), str(archive_dir / srt.name))
                # Update note
                update_frontmatter_field(note, "status", "archived")
                update_frontmatter_field(note, "archived_date", today.isoformat())
                archived_count += 1
                print(f"[lifecycle]   Archived: {slug} ({days_since} days since listened)", file=sys.stderr)

    # Process archived .mp3 files
    for mp3 in sorted(archive_dir.glob("*.mp3")):
        slug = mp3.stem
        note = find_episode_note(slug, episodes_dir)

        if not note:
            continue

        fm = parse_frontmatter(note)
        status = fm.get("status", "")

        if status == "archived" and fm.get("archived_date"):
            archived_date = date.fromisoformat(fm["archived_date"])
            days_since = (today - archived_date).days
            if days_since >= DELETE_AFTER_DAYS:
                # Delete mp3 only (keep .srt for transcript reference)
                mp3.unlink()
                deleted_count += 1
                print(f"[lifecycle]   Deleted audio: {slug} ({days_since} days since archived)", file=sys.stderr)

    # Summary
    if archived_count or deleted_count or autofilled_count:
        print(
            f"[lifecycle] Summary: {archived_count} archived, {deleted_count} audio deleted, "
            f"{autofilled_count} dates auto-filled",
            file=sys.stderr,
        )
    else:
        print("[lifecycle] No lifecycle actions needed.", file=sys.stderr)


if __name__ == "__main__":
    main()

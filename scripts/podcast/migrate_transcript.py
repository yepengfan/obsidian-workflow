#!/usr/bin/env python3
"""One-time migration: replace static transcripts with synced dataviewjs block.

Scans Podcasts/episodes/*.md for notes that have the old static transcript
format (**[HH:MM:SS]** text) and replaces the ## Transcript section with the
dataviewjs synced transcript block.

Idempotent: skips notes already containing a dataviewjs block in the
Transcript section.

Usage:
    python migrate_transcript.py [--dry-run] [--vault-path /path/to/vault]
"""

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DEFAULT_VAULT = SCRIPT_DIR.parent.parent

# Import the canonical dataviewjs block from write_notes.py
from write_notes import DATAVIEWJS_TRANSCRIPT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate static transcripts to synced dataviewjs")
    parser.add_argument("--vault-path", default=str(DEFAULT_VAULT), help="Obsidian vault root")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    return parser.parse_args()


def migrate_note(note_path: Path, dry_run: bool) -> bool:
    """Migrate a single episode note. Returns True if changed."""
    content = note_path.read_text(encoding="utf-8")

    # Skip if already migrated (has dataviewjs in Transcript section)
    if "```dataviewjs" in content and "Synced Podcast Transcript" in content:
        return False

    # Find the ## Transcript section: everything between "## Transcript\n"
    # and the next "## " heading (typically "## My Notes")
    pattern = r"(## Transcript\n)\n(.*?)(\n## )"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return False

    old_transcript = match.group(2)

    # Only migrate if it has the old static format: **[HH:MM:SS]** text
    if "**[" not in old_transcript:
        return False

    # Replace the transcript content
    new_content = content[:match.start(2)] + DATAVIEWJS_TRANSCRIPT + "\n" + content[match.start(3):]

    if dry_run:
        print(f"  [dry-run] Would migrate: {note_path.name}", file=sys.stderr)
    else:
        note_path.write_text(new_content, encoding="utf-8")
        print(f"  [migrated] {note_path.name}", file=sys.stderr)

    return True


def main() -> None:
    args = parse_args()
    vault = Path(args.vault_path).expanduser().resolve()
    episodes_dir = vault / "Podcasts" / "episodes"

    if not episodes_dir.exists():
        print(f"[migrate] ERROR: {episodes_dir} not found.", file=sys.stderr)
        sys.exit(1)

    notes = sorted(episodes_dir.glob("*.md"))
    print(f"[migrate] Scanning {len(notes)} episode notes...", file=sys.stderr)

    migrated = 0
    skipped = 0

    for note_path in notes:
        if migrate_note(note_path, args.dry_run):
            migrated += 1
        else:
            skipped += 1

    verb = "Would migrate" if args.dry_run else "Migrated"
    print(f"[migrate] Done — {verb} {migrated}, skipped {skipped}.", file=sys.stderr)


if __name__ == "__main__":
    main()

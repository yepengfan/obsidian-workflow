#!/usr/bin/env python3
"""Add .claude/skills/*/SKILL.md entries to module config_files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "system" / "modules"

COMMAND_TO_SKILL = {
    ".claude/commands/algo/solve.md": ".claude/skills/algo-solve/SKILL.md",
    ".claude/commands/book/book-init.md": ".claude/skills/book-init/SKILL.md",
    ".claude/commands/brownbag/brownbag.md": ".claude/skills/brownbag/SKILL.md",
    ".claude/commands/feeds/ai-digest.md": ".claude/skills/feeds-ai-digest/SKILL.md",
    ".claude/commands/feeds/engineering-blogs.md": ".claude/skills/feeds-engineering-blogs/SKILL.md",
    ".claude/commands/feeds/github-trending.md": ".claude/skills/feeds-github-trending/SKILL.md",
    ".claude/commands/frnt/solve.md": ".claude/skills/frnt-solve/SKILL.md",
    ".claude/commands/grammar/practice.md": ".claude/skills/grammar-practice/SKILL.md",
    ".claude/commands/grammar/review.md": ".claude/skills/grammar-review/SKILL.md",
    ".claude/commands/learning/learning-init.md": ".claude/skills/learning-init/SKILL.md",
    ".claude/commands/learning/learning-log.md": ".claude/skills/learning-log/SKILL.md",
    ".claude/commands/learning/learning-review.md": ".claude/skills/learning-review/SKILL.md",
    ".claude/commands/module-toggle.md": ".claude/skills/module-toggle/SKILL.md",
    ".claude/commands/sysd/solve.md": ".claude/skills/sysd-solve/SKILL.md",
    ".claude/commands/vault-ops/backup.md": ".claude/skills/vault-ops-backup/SKILL.md",
    ".claude/commands/vault-ops/organize.md": ".claude/skills/vault-ops-organize/SKILL.md",
    ".claude/commands/vault-ops/research.md": ".claude/skills/vault-ops-research/SKILL.md",
    ".claude/commands/vault-ops/summarize.md": ".claude/skills/vault-ops-summarize/SKILL.md",
    ".claude/commands/vault-ops/tag-audit.md": ".claude/skills/vault-ops-tag-audit/SKILL.md",
    ".claude/commands/work/daily.md": ".claude/skills/work-daily/SKILL.md",
    ".claude/commands/work/decision-log.md": ".claude/skills/work-decision-log/SKILL.md",
    ".claude/commands/work/meeting.md": ".claude/skills/work-meeting/SKILL.md",
    ".claude/commands/work/project.md": ".claude/skills/work-project/SKILL.md",
    ".claude/commands/zettelkasten/backlink.md": ".claude/skills/zettelkasten-backlink/SKILL.md",
    ".claude/commands/zettelkasten/inbox-review.md": ".claude/skills/zettelkasten-inbox-review/SKILL.md",
    ".claude/commands/zettelkasten/project-retro.md": ".claude/skills/zettelkasten-project-retro/SKILL.md",
    ".claude/commands/zettelkasten/retro.md": ".claude/skills/zettelkasten-retro/SKILL.md",
    ".claude/commands/zettelkasten/zettel.md": ".claude/skills/zettelkasten-zettel/SKILL.md",
}


def patch_module(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    for command, skill in COMMAND_TO_SKILL.items():
        if skill in text:
            continue
        needle = f"  - {command}\n"
        if needle in text:
            text = text.replace(needle, f"{needle}  - {skill}\n", 1)

    if text != original:
        text = re.sub(
            r"^updated: \d{4}-\d{2}-\d{2}$",
            "updated: 2026-08-03",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = []
    for module_path in sorted(MODULES.glob("*/module.md")):
        if patch_module(module_path):
            changed.append(str(module_path.relative_to(ROOT)))

    feed_orchestrator = MODULES / "feed-orchestrator" / "module.md"
    text = feed_orchestrator.read_text(encoding="utf-8")
    original = text
    skill_line = "  - .claude/skills/feeds-all/SKILL.md"
    if skill_line not in text:
        text = text.replace(
            "  - scripts/feed-orchestrator/load-env.sh\n",
            "  - scripts/feed-orchestrator/load-env.sh\n"
            f"{skill_line}\n"
            "  - .claude/commands/feeds/all.md\n",
            1,
        )
    text = text.replace("| Cursor | `/feeds/all` |", "| Cursor | `/feeds-all` or `/feeds/all` |")
    text = re.sub(
        r"^updated: \d{4}-\d{2}-\d{2}$",
        "updated: 2026-08-03",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if text != original:
        feed_orchestrator.write_text(text, encoding="utf-8")
        changed.append(str(feed_orchestrator.relative_to(ROOT)))

    print("Updated modules:")
    for line in changed:
        print(f"  {line}")


if __name__ == "__main__":
    main()

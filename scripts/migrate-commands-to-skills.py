#!/usr/bin/env python3
"""One-off helper: migrate .claude/commands/*.md to .claude/skills/*/SKILL.md."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ROOT / ".claude" / "commands"
SKILLS = ROOT / ".claude" / "skills"

DESCRIPTIONS: dict[str, str] = {
    "algo-solve": (
        "Interactive LeetCode solving workflow — Socratic hints (4 layers), code "
        "review, pattern card and daily log沉淀. Use when the user wants to solve a "
        "LeetCode problem, practice algorithms, or says /algo/solve or /algo-solve."
    ),
    "book-init": (
        "Onboard a new book into Learning/Books/ — locate EPUB/PDF, run book_init.py, "
        "confirm metadata. Use when adding a book or /book/book-init."
    ),
    "brownbag": (
        "Create a brownbag session plan from Templates/Brownbag Session.md. "
        "Use when planning a brownbag talk or /brownbag/brownbag."
    ),
    "feeds-ai-digest": (
        "Run the AI daily digest RSS pipeline (fetch, score, summarize, write reports). "
        "Use for /feeds/ai-digest or AI news digest generation."
    ),
    "feeds-all": (
        "Run all daily feed pipelines in parallel via the feed orchestrator. "
        "Use for /feeds/all or when generating all feeds at once."
    ),
    "feeds-engineering-blogs": (
        "Run the engineering blogs digest pipeline. "
        "Use for /feeds/engineering-blogs."
    ),
    "feeds-github-trending": (
        "Run the GitHub trending repos digest pipeline. "
        "Use for /feeds/github-trending."
    ),
    "frnt-solve": (
        "Frontend challenge workflow — sandbox setup, guided implementation, code review, "
        "pattern card logging. Use for GreatFrontEnd-style challenges or /frnt/solve."
    ),
    "grammar-practice": (
        "Advanced English grammar structure practice with Socratic rewriting. "
        "Use for /grammar/practice or grammar drills."
    ),
    "grammar-review": (
        "Review grammar structure cards by recency and show practice stats. "
        "Use for /grammar/review."
    ),
    "learning-init": (
        "Initialize a new learning plan under Learning/Plans/<CODE>/. "
        "Use for /learning/learning-init."
    ),
    "learning-log": (
        "Write or update a weekly learning log for a plan. "
        "Use for /learning/learning-log."
    ),
    "learning-review": (
        "Review learning plan progress and phase status. "
        "Use for /learning/learning-review."
    ),
    "module-toggle": (
        "List or toggle vault module enabled state in system/modules/. "
        "Use for /module-toggle."
    ),
    "sysd-solve": (
        "System design practice workflow — Delivery Framework guidance, review, "
        "pattern card logging. Use for /sysd/solve or system design interviews."
    ),
    "vault-ops-backup": (
        "Backup the Obsidian vault. Use for /vault-ops/backup."
    ),
    "vault-ops-organize": (
        "Organize vault files and folders. Use for /vault-ops/organize."
    ),
    "vault-ops-research": (
        "Research a topic and capture findings in the vault. "
        "Use for /vault-ops/research."
    ),
    "vault-ops-summarize": (
        "Summarize notes or documents in the vault. Use for /vault-ops/summarize."
    ),
    "vault-ops-tag-audit": (
        "Audit and clean up tags across the vault. Use for /vault-ops/tag-audit."
    ),
    "work-daily": (
        "Create or update today's work daily note with rollover tasks. "
        "Use for /work/daily."
    ),
    "work-decision-log": (
        "Record a structured decision log entry for a work project. "
        "Use for /work/decision-log."
    ),
    "work-meeting": (
        "Create a meeting note for a work project. Use for /work/meeting."
    ),
    "work-project": (
        "Create or update a work project page from template. Use for /work/project."
    ),
    "zettelkasten-backlink": (
        "Add or audit backlinks between zettel notes. Use for /zettelkasten/backlink."
    ),
    "zettelkasten-inbox-review": (
        "Weekly inbox processing — convert to zettel or archive. "
        "Use for /zettelkasten/inbox-review."
    ),
    "zettelkasten-project-retro": (
        "Run a project retrospective in the zettelkasten workflow. "
        "Use for /zettelkasten/project-retro."
    ),
    "zettelkasten-retro": (
        "Run a zettelkasten retrospective session. Use for /zettelkasten/retro."
    ),
    "zettelkasten-zettel": (
        "Create a new atomic zettel note in Zettelkasten/. Use for /zettelkasten/zettel."
    ),
}


def skill_name(rel: Path) -> str:
    stem = rel.with_suffix("")
    parts = stem.parts
    if len(parts) == 1:
        return parts[0]
    parent, child = parts[0], parts[1]
    if child.startswith(f"{parent}-") or (parent == "learning" and child.startswith("learning-")):
        return child
    if parent == child:
        return parent
    return f"{parent}-{child}"


def old_slash(rel: Path) -> str:
    return "/" + rel.with_suffix("").as_posix()


def build_skill_md(name: str, body: str) -> str:
    description = DESCRIPTIONS[name]
    return (
        "---\n"
        f"name: {name}\n"
        "description: >-\n"
        f"  {description}\n"
        "disable-model-invocation: true\n"
        "---\n\n"
        f"{body.rstrip()}\n"
    )


def main() -> None:
    created: list[str] = []
    skipped: list[str] = []

    for command_path in sorted(COMMANDS.rglob("*.md")):
        rel = command_path.relative_to(COMMANDS)
        name = skill_name(rel)
        skill_dir = SKILLS / name
        skill_path = skill_dir / "SKILL.md"
        body = command_path.read_text(encoding="utf-8")

        if skill_path.exists():
            existing = skill_path.read_text(encoding="utf-8")
            if existing.split("---", 2)[-1].strip() == body.strip():
                skipped.append(name)
                continue

        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(build_skill_md(name, body), encoding="utf-8")
        created.append(f"{name} ({old_slash(rel)} -> /{name})")

    print(f"Created/updated: {len(created)}")
    for line in created:
        print(f"  {line}")
    if skipped:
        print(f"Skipped unchanged: {len(skipped)}")
        for line in skipped:
            print(f"  {line}")


if __name__ == "__main__":
    main()

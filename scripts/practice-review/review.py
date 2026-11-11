#!/usr/bin/env python3
"""Maintain practice-review notes and calculate the due queue."""

import argparse
import fcntl
import json
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("practice-review requires PyYAML")


ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "system/modules/practice-review/module.md"
REVIEW = ROOT / "Learning/Practice/Review"
ITEMS = REVIEW / "Items"
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)(.*)\Z", re.DOTALL)
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
ATTEMPT_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
OUTCOMES = {"independent": "独立完成", "assisted": "提示后完成", "incomplete": "未完成"}


def read_note(path):
    with path.open(encoding="utf-8", newline="") as file:
        match = FRONTMATTER.fullmatch(file.read())
    if match is None:
        raise ValueError(f"{path.name} requires YAML frontmatter")
    try:
        metadata = yaml.safe_load(match[1])
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid YAML frontmatter in {path.name}") from error
    if not isinstance(metadata, dict):
        raise ValueError(f"{path.name} frontmatter must be a mapping")
    return metadata, match[2]


def write_note(path, metadata, body):
    frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=path.parent,
            prefix=".review-", suffix=".tmp", delete=False,
        ) as file:
            temporary = Path(file.name)
            file.write(f"---\n{frontmatter}---\n{body}")
            file.flush()
            os.fsync(file.fileno())
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@contextmanager
def item_lock(item_id):
    locks = ITEMS / ".locks"
    locks.mkdir(parents=True, exist_ok=True)
    # A stable lock file protects read-modify-replace on the note across CLI calls.
    with (locks / f"{item_id}.lock").open("a") as file:
        fcntl.flock(file.fileno(), fcntl.LOCK_EX)
        yield


def load_config():
    config, _ = read_note(MODULE)
    if config.get("enabled") is False:
        raise ValueError("practice-review module is disabled")
    if config.get("enabled") is not True:
        raise ValueError("practice-review enabled must be true or false")
    intervals = config.get("interval_days")
    if not isinstance(intervals, list) or not intervals or any(
        type(days) is not int or days < 1 for days in intervals
    ):
        raise ValueError("interval_days must be a nonempty list of positive integers")
    retry = config.get("retry_days")
    if type(retry) is not int or retry < 1:
        raise ValueError("retry_days must be a positive integer")
    return intervals, retry


def read_payload(path):
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path.name}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return payload


def read_text_field(data, field, *, required=False):
    value = data.get(field, "")
    if not isinstance(value, str) or (required and not value.strip()):
        expected = "a nonempty string" if required else "a string"
        raise ValueError(f"{field} must be {expected}")
    return value


def item_slug(value, field):
    if not isinstance(value, str) or SLUG.fullmatch(value) is None:
        raise ValueError(f"{field} must be a lowercase slug, such as lc-1071")
    return value


def read_date(value):
    if type(value) is date:
        return value
    if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return date.fromisoformat(value)
    raise ValueError("Dates must use YYYY-MM-DD")


def summarize(path, metadata):
    try:
        item_id = item_slug(metadata.get("id"), "id")
        if item_id != path.stem:
            raise ValueError("id must match the filename")
        domain = item_slug(metadata.get("domain"), "domain")
        title = read_text_field(metadata, "title", required=True)
        status = metadata.get("status")
        if status not in ("active", "archived"):
            raise ValueError("status must be active or archived")
        summary = {
            "id": item_id,
            "domain": domain,
            "title": title,
            "status": status,
            "path": path.relative_to(ROOT).as_posix(),
        }
        for key in ("review_count", "stage"):
            value = metadata.get(key)
            if type(value) is not int or value < 0:
                raise ValueError(f"{key} must be a nonnegative integer")
            summary[key] = value
        for key in ("last_review", "next_review"):
            value = metadata.get(key)
            summary[key] = read_date(value).isoformat() if value is not None else None
        return summary
    except ValueError as error:
        raise ValueError(f"Invalid item {path.name}: {error}") from error


def show(item_id):
    path = ITEMS / f"{item_id}.md"
    metadata, _ = read_note(path)
    return {
        **summarize(path, metadata),
        "prompt": read_text_field(metadata, "prompt", required=True),
        "source": read_text_field(metadata, "source") or None,
    }


def due(today):
    day = today.isoformat()
    queue = {"date": day, "overdue": [], "today": [], "unstarted": [], "upcoming": []}
    for path in ITEMS.glob("*.md"):
        metadata, _ = read_note(path)
        if metadata.get("status") == "archived":
            continue
        summary = summarize(path, metadata)
        next_review = summary["next_review"]
        if next_review is None:
            queue["unstarted"].append(summary)
        elif next_review <= day:
            key = "today" if next_review == day else "overdue"
            queue[key].append(summary)
        else:
            queue["upcoming"].append(summary)
    for key in ("overdue", "today", "unstarted", "upcoming"):
        queue[key].sort(key=lambda item: (item["next_review"] or "", item["id"]))
    return queue


def add(payload):
    item_id = item_slug(payload.get("id"), "id")
    domain = item_slug(payload.get("domain"), "domain")
    title = read_text_field(payload, "title", required=True).strip()
    prompt = read_text_field(payload, "prompt", required=True)
    source = read_text_field(payload, "source")
    focus = read_text_field(payload, "review_focus")
    for directory in ("Flows", "Content"):
        if not (REVIEW / directory / f"{domain}.md").is_file():
            raise ValueError(f"Missing {directory}/{domain}.md")

    path = ITEMS / f"{item_id}.md"
    with item_lock(item_id):
        if path.exists():
            existing, _ = read_note(path)
            summary = summarize(path, existing)
            if summary["domain"] != domain or summary["title"] != title:
                raise ValueError(f"{item_id} already belongs to a different item")
            return {**summary, "created": False}

        metadata = {
            "id": item_id, "domain": domain, "title": title, "status": "active",
            "prompt": prompt, "review_count": 0, "stage": 0,
            "last_review": None, "next_review": None, "attempt_ids": [],
        }
        if source:
            metadata["source"] = source
        body = f"# {' '.join(title.splitlines())}\n\n"
        if focus.strip():
            body += f"## 回顾重点\n\n{focus}\n\n"
        body += "## 练习记录\n"
        write_note(path, metadata, body)
        return {**summarize(path, metadata), "created": True}


def record(item_id, payload, day, intervals, retry_days):
    attempt_id = read_text_field(payload, "attempt_id", required=True)
    if ATTEMPT_ID.fullmatch(attempt_id) is None:
        raise ValueError("attempt_id must use letters, digits, hyphens or underscores")
    outcome = read_text_field(payload, "outcome", required=True)
    if outcome not in OUTCOMES:
        raise ValueError("outcome must be independent, assisted or incomplete")
    reflection = read_text_field(payload, "reflection", required=True)
    submission = read_text_field(payload, "submission")
    observations = read_text_field(payload, "observations")

    path = ITEMS / f"{item_id}.md"
    with item_lock(item_id):
        metadata, body = read_note(path)
        summary = summarize(path, metadata)
        if summary["status"] == "archived":
            raise ValueError(f"{item_id} is archived")
        attempt_ids = metadata.get("attempt_ids", [])
        if not isinstance(attempt_ids, list) or not all(
            isinstance(value, str) for value in attempt_ids
        ):
            raise ValueError(f"{item_id} attempt_ids must be a list of strings")
        if attempt_id in attempt_ids:
            return {**summary, "recorded": False}

        last_review = summary["last_review"]
        if last_review is not None and day < read_date(last_review):
            raise ValueError(f"Review date precedes the last review of {item_id}")
        stage = summary["stage"]
        previous_due = summary["next_review"]
        if outcome != "independent":
            next_review = day + timedelta(days=retry_days)
        elif previous_due is None:
            stage = 0
            next_review = day + timedelta(days=intervals[stage])
        elif day < read_date(previous_due):
            next_review = read_date(previous_due)
        else:
            stage = min(stage + 1, len(intervals) - 1)
            next_review = day + timedelta(days=intervals[stage])

        review_count = summary["review_count"] + 1
        metadata.update(
            review_count=review_count, stage=stage, last_review=day,
            next_review=next_review, last_outcome=outcome,
            attempt_ids=[*attempt_ids, attempt_id],
        )
        entry = (
            f"### {day} · 第 {review_count} 轮\n\n"
            f"**{OUTCOMES[outcome]}** · 下次复习 {next_review}\n\n"
            f"#### 本人心得\n\n{reflection}\n"
        )
        if submission.strip():
            entry += f"\n#### 本次作答\n\n{submission}\n"
        if observations.strip():
            entry += f"\n#### 练习反馈\n\n{observations}\n"
        write_note(path, metadata, body + "\n\n" + entry)
        return {**summarize(path, metadata), "recorded": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", metavar="YYYY-MM-DD", help="Use this local date")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("due", help="List due, upcoming and unstarted review items")
    commands.add_parser("show", help="Show an item without its history").add_argument("id")
    add_parser = commands.add_parser("add", help="Add a practice item")
    add_parser.add_argument("--item-file", type=Path, required=True)
    record_parser = commands.add_parser("record", help="Record an ended practice round")
    record_parser.add_argument("id")
    record_parser.add_argument("--attempt-file", type=Path, required=True)
    args = parser.parse_args()

    try:
        day = read_date(args.date) if args.date is not None else date.today()
        intervals, retry_days = load_config()
        if args.command == "due":
            result = due(day)
        elif args.command == "show":
            result = show(item_slug(args.id, "id"))
        elif args.command == "add":
            result = add(read_payload(args.item_file))
        else:
            result = record(
                item_slug(args.id, "id"), read_payload(args.attempt_file),
                day, intervals, retry_days,
            )
    except (OSError, ValueError, OverflowError) as error:
        parser.exit(1, f"practice-review: {error}\n")

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

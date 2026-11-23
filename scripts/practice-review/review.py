#!/usr/bin/env python3
"""Maintain practice-review notes and calculate the due queue."""

import argparse
import fcntl
import hashlib
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


class FrontmatterDumper(yaml.SafeDumper):
    """Write repeated values in full; Obsidian properties do not resolve YAML aliases."""

    def ignore_aliases(self, data):
        return True


def write_note(path, metadata, body):
    frontmatter = yaml.dump(
        metadata, Dumper=FrontmatterDumper, allow_unicode=True, sort_keys=False,
    )
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
    flows = config.get("practice_flows")
    if not isinstance(flows, dict) or not flows:
        raise ValueError("practice_flows must map domains to their existing workflow files")
    archive = config.get("archive_after_final", False)
    if type(archive) is not bool:
        raise ValueError("archive_after_final must be true or false")
    return intervals, retry, flows, archive


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


HISTORY_ROUND = re.compile(
    r"^### (\d{4}-\d{2}-\d{2}) · (?:Round (\d+)|第 (\d+) 轮)\s*\n"
    r"\*\*(independent|assisted|incomplete|独立完成|提示后完成|未完成)\*\* · ", re.MULTILINE,
)


def schedule_round(stage, previous_due, completed, outcome, day, intervals, retry_days, archive_after_final=False):
    if completed is not None and completed < 2 and outcome != "incomplete":
        stage = min(completed, len(intervals) - 1)
    elif outcome != "independent":
        return stage, day + timedelta(days=retry_days)
    elif previous_due is None:
        stage = 0
    elif day < read_date(previous_due):
        return stage, read_date(previous_due)
    elif archive_after_final and stage == len(intervals) - 1:
        return stage, None
    else:
        stage = min(stage + 1, len(intervals) - 1)
    return stage, day + timedelta(days=intervals[stage])


def design_progress(metadata, body, intervals, retry_days):
    if metadata["domain"] != "system-design":
        return {}
    count = metadata.get("completed_design_rounds")
    if count is not None:
        if type(count) is not int or not 0 <= count <= metadata["review_count"]:
            raise ValueError("Invalid completed_design_rounds")
        return {"completed_design_rounds": count}
    history = HISTORY_ROUND.findall(body)
    if len(history) != metadata["review_count"] or any(
        int(en or zh) != i for i, (_, en, zh, _) in enumerate(history, 1)
    ):
        return {"completed_design_rounds": 0}
    completed = 0
    stage, due_date = 0, None
    translations = {label: key for key, label in OUTCOMES.items()}
    for day, _, _, label in history:
        outcome = translations.get(label, label)
        stage, due_date = schedule_round(stage, due_date, completed, outcome, read_date(day), intervals, retry_days)
        completed += outcome != "incomplete"
    progress = {"completed_design_rounds": completed}
    if history and history[-1][0] == str(metadata["last_review"]) and metadata["status"] == "active":
        progress.update(stage=stage, next_review=due_date)
    return progress


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
        if "completed_design_rounds" in metadata:
            summary["completed_design_rounds"] = metadata["completed_design_rounds"]
        return summary
    except ValueError as error:
        raise ValueError(f"Invalid item {path.name}: {error}") from error


def show(item_id, intervals, retry_days):
    path = ITEMS / f"{item_id}.md"
    metadata, body = read_note(path)
    metadata.update(design_progress(metadata, body, intervals, retry_days))
    return {
        **summarize(path, metadata),
        "prompt": read_text_field(metadata, "prompt", required=True),
        "source": read_text_field(metadata, "source") or None,
    }


def due(today, intervals, retry_days):
    day = today.isoformat()
    queue = {"date": day, "overdue": [], "today": [], "unstarted": [], "upcoming": []}
    for path in ITEMS.glob("*.md"):
        metadata, body = read_note(path)
        if metadata.get("status") == "archived":
            continue
        metadata.update(design_progress(metadata, body, intervals, retry_days))
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


def add(payload, flows):
    item_id = item_slug(payload.get("id"), "id")
    domain = item_slug(payload.get("domain"), "domain")
    title = read_text_field(payload, "title", required=True).strip()
    prompt = read_text_field(payload, "prompt", required=True)
    source = read_text_field(payload, "source")
    focus = read_text_field(payload, "review_focus")
    flow = flows.get(domain)
    if not isinstance(flow, str) or not flow.strip():
        raise ValueError(f"No practice flow configured for {domain}")
    if not (ROOT / flow).is_file():
        raise ValueError(f"Missing configured practice flow: {flow}")
    if not (REVIEW / "Content" / f"{domain}.md").is_file():
        raise ValueError(f"Missing Content/{domain}.md")

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
        if domain == "system-design":
            metadata["completed_design_rounds"] = 0
        if source:
            metadata["source"] = source
        body = f"# {' '.join(title.splitlines())}\n\n"
        if focus.strip():
            body += f"## 回顾重点\n\n{focus}\n\n"
        body += "## 练习记录\n"
        write_note(path, metadata, body)
        return {**summarize(path, metadata), "created": True}


def record(item_id, payload, day, intervals, retry_days, archive_after_final=False):
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
        metadata.update(design_progress(metadata, body, intervals, retry_days))
        summary = summarize(path, metadata)
        attempt_ids = metadata.get("attempt_ids", [])
        if not isinstance(attempt_ids, list) or not all(
            isinstance(value, str) for value in attempt_ids
        ):
            raise ValueError(f"{item_id} attempt_ids must be a list of strings")
        if attempt_id in attempt_ids:
            return {**summary, "recorded": False}

        if summary["status"] == "archived":
            raise ValueError(f"{item_id} is archived")
        last_review = summary["last_review"]
        if last_review is not None and day < read_date(last_review):
            raise ValueError(f"Review date precedes the last review of {item_id}")
        stage = summary["stage"]
        if stage >= len(intervals):
            raise ValueError(f"{item_id} stage is outside interval_days")
        previous_due = summary["next_review"]
        completed = metadata.get("completed_design_rounds")
        stage, next_review = schedule_round(stage, previous_due, completed, outcome, day, intervals, retry_days, archive_after_final)
        archived = next_review is None
        if completed is not None and outcome != "incomplete":
            metadata["completed_design_rounds"] = completed + 1

        review_count = summary["review_count"] + 1
        metadata.update(
            review_count=review_count, stage=stage, last_review=day,
            next_review=next_review, last_outcome=outcome,
            attempt_ids=[*attempt_ids, attempt_id],
        )
        if archived:
            metadata.update(status="archived", archived_on=day)
        schedule = "已归档" if archived else f"下次复习 {next_review}"
        entry = (
            f"### {day} · 第 {review_count} 轮\n\n"
            f"**{OUTCOMES[outcome]}** · {schedule}\n\n"
            f"#### 本人心得\n\n{reflection}\n"
        )
        if submission.strip():
            entry += f"\n#### 本次作答\n\n{submission}\n"
        if observations.strip():
            entry += f"\n#### 练习反馈\n\n{observations}\n"
        write_note(path, metadata, body + "\n\n" + entry)
        return {**summarize(path, metadata), "recorded": True}


def finish(topic, attempt, progress_path, day, config):
    intervals, retry_days, flows, archive = config
    item_id = item_slug(topic.get("id"), "id")
    attempt_id = read_text_field(attempt, "attempt_id", required=True)
    if not ATTEMPT_ID.fullmatch(attempt_id):
        raise ValueError("Invalid attempt_id")

    def register():
        add(topic, flows)
        record(item_id, attempt, day, intervals, retry_days, archive)
        path = ITEMS / f"{item_id}.md"
        saved, _ = read_note(path)
        receipt = summarize(path, saved)
        if attempt_id not in saved["attempt_ids"] or (
            receipt["status"] == "active" and not receipt["next_review"]
        ):
            raise ValueError("Registration could not be verified")
        return {**receipt, "verified": True, "attempt_id": attempt_id}

    if progress_path is None:
        return register()
    path = (ROOT / progress_path).resolve()
    solutions = (ROOT / "Learning/Practice/System-Design/Solutions").resolve()
    if topic["domain"] != "system-design" or path.parent.parent != solutions or path.name != "progress.md":
        raise ValueError("Invalid session progress path")
    # Serialize finalizers for this folder even if they supply different topic IDs.
    with item_lock("session." + hashlib.sha256(str(path).encode()).hexdigest()):
        metadata, body = read_note(path)
        tags = metadata.get("tags", [])
        tags = [tags] if isinstance(tags, str) else tags
        binding = {"round_id": attempt_id, "review_item_id": item_id, "round_completed_on": day.isoformat()}
        if any(metadata.get(key) is not None and str(metadata[key]) != value for key, value in binding.items()):
            raise ValueError("Session round does not match registration")
        if "system-design/wip" not in tags and not (
            "system-design/done" in tags and all(str(metadata.get(k)) == v for k, v in binding.items())
        ):
            raise ValueError("Session is not awaiting registration")
        metadata.update(binding)
        write_note(path, metadata, body)
        result = register()
        current, body = read_note(path)
        if any(str(current.get(k)) != v for k, v in binding.items()):
            raise ValueError("Session changed during registration")
        tags = current["tags"]
        current["tags"] = ["system-design/done" if t == "system-design/wip" else t
                           for t in ([tags] if isinstance(tags, str) else tags)]
        write_note(path, current, body)
        return result


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
    finish_parser = commands.add_parser("finish", help="Register and verify a confirmed round")
    finish_parser.add_argument("--item-file", type=Path, required=True)
    finish_parser.add_argument("--attempt-file", type=Path, required=True)
    finish_parser.add_argument("--progress-path", type=Path)
    args = parser.parse_args()

    try:
        day = read_date(args.date) if args.date is not None else date.today()
        intervals, retry_days, flows, archive_after_final = load_config()
        if args.command == "due":
            result = due(day, intervals, retry_days)
        elif args.command == "show":
            result = show(item_slug(args.id, "id"), intervals, retry_days)
        elif args.command == "add":
            result = add(read_payload(args.item_file), flows)
        elif args.command == "finish":
            result = finish(read_payload(args.item_file), read_payload(args.attempt_file),
                            args.progress_path, day, (intervals, retry_days, flows, archive_after_final))
        else:
            result = record(
                item_slug(args.id, "id"), read_payload(args.attempt_file),
                day, intervals, retry_days, archive_after_final,
            )
    except (OSError, ValueError, OverflowError) as error:
        parser.exit(1, f"practice-review: {error}\n")

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

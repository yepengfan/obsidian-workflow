"""Scheduling tests for the practice-review CLI.

Run: python -m pytest scripts/practice-review/test_review.py
"""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
import yaml

import review

INTERVALS = [1, 3, 7, 14, 60]
RETRY = 1


@pytest.fixture
def vault(tmp_path, monkeypatch):
    items = tmp_path / "Learning/Practice/Review/Items"
    items.mkdir(parents=True)
    module = tmp_path / "system/modules/practice-review/module.md"
    module.parent.mkdir(parents=True)
    monkeypatch.setattr(review, "ROOT", tmp_path)
    monkeypatch.setattr(review, "ITEMS", items)
    monkeypatch.setattr(review, "MODULE", module)
    return tmp_path


def write_item(vault, **fields):
    metadata = {
        "id": "lc-1", "domain": "algorithm", "title": "LC 1 - Two Sum",
        "status": "active", "prompt": "Find two numbers.", "review_count": 0,
        "stage": 0, "last_review": None, "next_review": None, "attempt_ids": [],
        **fields,
    }
    path = vault / "Learning/Practice/Review/Items/lc-1.md"
    review.write_note(path, metadata, "# LC 1 - Two Sum\n\n## 练习记录\n")
    return path


def read_item(path):
    metadata, body = review.read_note(path)
    return metadata, body


def record(day, outcome="independent", attempt="a1", archive=True):
    payload = {"attempt_id": attempt, "outcome": outcome, "reflection": "ok"}
    return review.record("lc-1", payload, day, INTERVALS, RETRY, archive)


def test_first_independent_completion_starts_stage_zero(vault):
    path = write_item(vault)
    record(date(2026, 11, 20))
    metadata, _ = read_item(path)
    assert metadata["stage"] == 0
    assert metadata["next_review"] == date(2026, 11, 21)
    assert metadata["status"] == "active"


def test_on_time_completion_advances_one_stage(vault):
    path = write_item(vault, stage=1, review_count=2, last_review=date(2026, 11, 17),
                      next_review=date(2026, 11, 20))
    record(date(2026, 11, 20))
    metadata, _ = read_item(path)
    assert metadata["stage"] == 2
    assert metadata["next_review"] == date(2026, 11, 27)


def test_stage_three_moves_to_sixty_days(vault):
    path = write_item(vault, stage=3, review_count=4, last_review=date(2026, 11, 6),
                      next_review=date(2026, 11, 20))
    record(date(2026, 11, 22))
    metadata, _ = read_item(path)
    assert metadata["stage"] == 4
    assert metadata["next_review"] == date(2027, 1, 21)
    assert metadata["status"] == "active"


def test_early_practice_keeps_schedule_and_does_not_archive(vault):
    path = write_item(vault, stage=4, review_count=5, last_review=date(2026, 11, 1),
                      next_review=date(2026, 12, 31))
    record(date(2026, 11, 20))
    metadata, _ = read_item(path)
    assert metadata["stage"] == 4
    assert metadata["next_review"] == date(2026, 12, 31)
    assert metadata["status"] == "active"


@pytest.mark.parametrize("outcome", ["assisted", "incomplete"])
def test_unfinished_final_round_retries_without_archiving(vault, outcome):
    path = write_item(vault, stage=4, review_count=5, last_review=date(2026, 9, 21),
                      next_review=date(2026, 11, 20))
    record(date(2026, 11, 20), outcome=outcome)
    metadata, _ = read_item(path)
    assert metadata["stage"] == 4
    assert metadata["next_review"] == date(2026, 11, 21)
    assert metadata["status"] == "active"


def test_passing_final_interval_archives_item(vault):
    path = write_item(vault, stage=4, review_count=5, last_review=date(2026, 9, 21),
                      next_review=date(2026, 11, 20))
    result = record(date(2026, 11, 23))
    metadata, body = read_item(path)
    assert metadata["status"] == "archived"
    assert metadata["archived_on"] == date(2026, 11, 23)
    assert metadata["next_review"] is None
    assert metadata["stage"] == 4
    assert metadata["review_count"] == 6
    assert result["status"] == "archived"
    assert "**独立完成** · 已归档" in body
    assert "&id" not in path.read_text(encoding="utf-8")
    assert "下次复习" not in body.split("### 2026-11-23")[1]

    queue = review.due(date(2026, 11, 23), INTERVALS, RETRY)
    assert all(item["id"] != "lc-1" for key in ("overdue", "today", "unstarted", "upcoming")
               for item in queue[key])
    with pytest.raises(ValueError, match="archived"):
        record(date(2026, 11, 24), attempt="a2")


def test_disabled_archive_repeats_final_interval(vault):
    path = write_item(vault, stage=4, review_count=5, last_review=date(2026, 9, 21),
                      next_review=date(2026, 11, 20))
    record(date(2026, 11, 20), archive=False)
    metadata, _ = read_item(path)
    assert metadata["status"] == "active"
    assert metadata["stage"] == 4
    assert metadata["next_review"] == date(2027, 1, 19)


def test_stage_outside_intervals_is_rejected(vault):
    write_item(vault, stage=5, review_count=6, last_review=date(2026, 9, 21),
               next_review=date(2026, 11, 20))
    with pytest.raises(ValueError, match="outside interval_days"):
        record(date(2026, 11, 20))


def write_module(vault, **fields):
    config = {"enabled": True, "interval_days": INTERVALS, "retry_days": RETRY,
              "practice_flows": {"algorithm": "flow.md"}, **fields}
    review.MODULE.write_text(f"---\n{yaml.safe_dump(config)}---\n", encoding="utf-8")


def test_load_config_reads_archive_flag(vault):
    write_module(vault, archive_after_final=True)
    assert review.load_config()[3] is True


def test_load_config_defaults_archive_flag_to_false(vault):
    write_module(vault)
    assert review.load_config()[3] is False


def test_load_config_rejects_non_boolean_archive_flag(vault):
    write_module(vault, archive_after_final="yes")
    with pytest.raises(ValueError, match="archive_after_final"):
        review.load_config()


def test_each_design_gets_two_full_learning_rounds(vault):
    path = write_item(vault, domain="system-design")
    record(date(2026, 11, 20), "incomplete", "ended-incomplete")
    first = record(date(2026, 11, 21), "assisted")
    assert first["next_review"] == "2026-11-22"
    second = record(date(2026, 11, 22), "assisted", "a2")
    assert second["next_review"] == "2026-11-25"
    assert second["completed_design_rounds"] == 2
    assert not record(date(2026, 11, 22), "assisted", "a2")["recorded"]
    metadata, body = read_item(path)
    del metadata["completed_design_rounds"]
    metadata.update(stage=0, next_review=date(2026, 11, 23))
    review.write_note(path, metadata, body)
    assert review.show("lc-1", INTERVALS, RETRY)["next_review"] == "2026-11-25"
    assert record(date(2026, 11, 25), "independent", "a3")["next_review"] == "2026-12-02"
    metadata, body = read_item(path)
    del metadata["completed_design_rounds"]
    metadata.update(stage=1, next_review=date(2026, 11, 28))
    review.write_note(path, metadata, body)
    assert review.show("lc-1", INTERVALS, RETRY)["next_review"] == "2026-12-02"


def test_finish_recovers_same_design_round(vault, monkeypatch):
    domain = "system-design"
    review_root = vault / "Learning/Practice/Review"
    monkeypatch.setattr(review, "REVIEW", review_root)
    (review_root / "Content").mkdir()
    (review_root / "Content/system-design.md").touch()
    (vault / "flow.md").touch()
    path = vault / "Learning/Practice/System-Design/Solutions/Dropbox/progress.md"
    path.parent.mkdir(parents=True)
    review.write_note(path, {"tags": ["system-design/wip"], "topic": "Dropbox"}, "all six stages")
    topic = {"id": "dropbox", "title": "Dropbox", "domain": domain, "prompt": "Design Dropbox."}
    attempt = {"attempt_id": "round-1", "outcome": "assisted", "reflection": "Resume uploads."}
    args = (topic, attempt, path, date(2026, 11, 23), (INTERVALS, RETRY, {domain: "flow.md"}, True))
    with pytest.raises(ValueError, match="progress path"):
        review.finish(topic, attempt, None, *args[3:])
    with pytest.raises(ValueError, match="Session topic"):
        review.finish({**topic, "title": "Bitly"}, *args[1:])
    assert "round_id" not in review.read_note(path)[0]
    assert not (review.ITEMS / "dropbox.md").exists()
    original_write = review.write_note

    def interrupt_close(target, fields, body):
        if target == path and "system-design/done" in fields.get("tags", []):
            raise OSError("interrupted after review write")
        original_write(target, fields, body)

    monkeypatch.setattr(review, "write_note", interrupt_close)
    with pytest.raises(OSError):
        review.finish(*args)
    monkeypatch.setattr(review, "write_note", original_write)
    for _ in range(2):
        receipt = review.finish(*args)
        assert receipt["review_count"] == 1 and str(receipt["next_review"]) == "2026-11-24"
    assert review.read_note(path)[0]["tags"] == ["system-design/done"]


def prepare_design_finish(vault, monkeypatch):
    domain = "system-design"
    review_root = vault / "Learning/Practice/Review"
    monkeypatch.setattr(review, "REVIEW", review_root)
    (review_root / "Content").mkdir(exist_ok=True)
    (review_root / "Content/system-design.md").touch()
    (vault / "flow.md").touch()
    topic = {"id": "youtube", "title": "YouTube", "domain": domain, "prompt": "Design YouTube."}
    attempt = {"attempt_id": "round-1", "outcome": "assisted", "reflection": "Use a CDN."}
    config = (INTERVALS, RETRY, {domain: "flow.md"}, False)
    return topic, attempt, config


def write_session(vault, folder, saved_topic):
    path = vault / "Learning/Practice/System-Design/Solutions" / folder / "progress.md"
    path.parent.mkdir(parents=True)
    review.write_note(path, {"tags": ["system-design/wip"], "topic": saved_topic}, "session")
    return path


def test_finish_accepts_full_problem_description_and_rejects_unrelated_session(vault, monkeypatch):
    topic, attempt, config = prepare_design_finish(vault, monkeypatch)
    described = write_session(vault, "YouTube", "Design YouTube")
    unrelated = write_session(vault, "Bitly", "Design Bitly")
    contained = write_session(vault, "Music", "Design YouTube Music")
    with pytest.raises(ValueError, match="Session topic"):
        review.finish(topic, attempt, unrelated, date(2026, 11, 23), config)
    with pytest.raises(ValueError, match="Session topic"):
        review.finish(topic, attempt, contained, date(2026, 11, 23), config)
    assert "round_id" not in review.read_note(unrelated)[0]
    assert "round_id" not in review.read_note(contained)[0]
    assert not (review.ITEMS / "youtube.md").exists()
    receipt = review.finish(topic, attempt, described, date(2026, 11, 23), config)
    assert receipt["verified"] is True and receipt["review_count"] == 1
    assert review.read_note(described)[0]["tags"] == ["system-design/done"]


def cli_vault(tmp_path):
    script = tmp_path / "scripts/practice-review/review.py"
    script.parent.mkdir(parents=True)
    script.write_text(Path(review.__file__).read_text(encoding="utf-8"), encoding="utf-8")
    module = tmp_path / "system/modules/practice-review"
    module.mkdir(parents=True)
    config = {"enabled": True, "interval_days": INTERVALS, "retry_days": RETRY,
              "practice_flows": {"system-design": "flow.md", "algorithm": "flow.md"}}
    (module / "module.md").write_text(f"---\n{yaml.safe_dump(config)}---\n", encoding="utf-8")
    (tmp_path / "flow.md").write_text("flow\n", encoding="utf-8")
    content = tmp_path / "Learning/Practice/Review/Content"
    content.mkdir(parents=True)
    (content / "system-design.md").write_text("content\n", encoding="utf-8")
    (content / "algorithm.md").write_text("content\n", encoding="utf-8")
    return script


def run_finish_cli(script, vault, item, progress=None):
    item_path = vault / "item.json"
    attempt_path = vault / "attempt.json"
    item_path.write_text(json.dumps(item), encoding="utf-8")
    attempt_path.write_text(json.dumps({
        "attempt_id": "round-1", "outcome": "assisted", "reflection": "Use a CDN.",
    }), encoding="utf-8")
    command = [sys.executable, str(script), "--date", "2026-11-23", "finish",
               "--item-file", str(item_path), "--attempt-file", str(attempt_path)]
    if progress is not None:
        command.extend(["--progress-path", progress])
    return subprocess.run(command, cwd=vault, capture_output=True, text=True)


def test_finish_cli_accepts_full_description_and_rejects_unrelated_session(tmp_path):
    script = cli_vault(tmp_path)
    topic = {"id": "youtube", "domain": "system-design", "title": "YouTube", "prompt": "Design YouTube."}
    unrelated = write_session(tmp_path, "Bitly", "Design Bitly")
    described = write_session(tmp_path, "YouTube", "Design YouTube")
    rejected = run_finish_cli(script, tmp_path, topic,
                              "Learning/Practice/System-Design/Solutions/Bitly/progress.md")
    assert rejected.returncode == 1
    assert rejected.stderr == "practice-review: Session topic does not match review title\n"
    assert "Traceback" not in rejected.stderr
    assert "round_id" not in review.read_note(unrelated)[0]
    assert not (tmp_path / "Learning/Practice/Review/Items/youtube.md").exists()
    accepted = run_finish_cli(script, tmp_path, topic,
                              "Learning/Practice/System-Design/Solutions/YouTube/progress.md")
    assert accepted.returncode == 0, accepted.stderr
    assert json.loads(accepted.stdout)["review_count"] == 1
    assert review.read_note(described)[0]["tags"] == ["system-design/done"]


def test_finish_cli_reports_missing_domain_without_traceback(tmp_path):
    script = cli_vault(tmp_path)
    result = run_finish_cli(script, tmp_path, {"id": "two-sum", "title": "Two Sum", "prompt": "Find two numbers."})
    assert result.returncode == 1
    assert result.stderr == "practice-review: domain must be a lowercase slug, such as lc-1071\n"
    assert "Traceback" not in result.stderr
    assert result.stdout == ""

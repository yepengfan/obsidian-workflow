"""Scheduling tests for the practice-review CLI.

Run: python -m pytest scripts/practice-review/test_review.py
"""

from datetime import date

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

    queue = review.due(date(2026, 11, 23), INTERVALS)
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
    assert review.show("lc-1", INTERVALS)["next_review"] == "2026-11-25"
    assert record(date(2026, 11, 25), "independent", "a3")["next_review"] == "2026-12-02"

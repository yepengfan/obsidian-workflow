"""Scheduling tests for the practice-review CLI.

Run: python -m pytest scripts/practice-review/test_review.py
"""

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import pytest
import yaml

import design_profile
import review

FIXTURE = json.loads((Path(__file__).parent / "fixtures/design-rounds.json").read_text(encoding="utf-8"))

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


def test_design_rounds_follow_the_shared_completion_schedule(vault):
    path = write_item(vault, domain="system-design")
    seen = set()
    for step in FIXTURE["rounds"]:
        payload = {
            "attempt_id": step["attempt_id"], "outcome": step["outcome"], "reflection": "ok",
        }
        result = review.record(
            "lc-1", payload, date.fromisoformat(step["date"]),
            FIXTURE["intervals"], FIXTURE["retry_days"], True,
        )
        assert result["recorded"] is True
        assert result["completed_design_rounds"] == step["completed_design_rounds"]
        assert result["stage"] == step["stage"]
        assert result["status"] == step["status"]
        assert result["next_review"] == step["next_review"]
        if step["attempt_id"] == "r3":
            duplicate = review.record(
                "lc-1", payload, date.fromisoformat(step["date"]),
                FIXTURE["intervals"], FIXTURE["retry_days"], True,
            )
            assert duplicate["recorded"] is False
            assert duplicate["completed_design_rounds"] == step["completed_design_rounds"]
        seen.add(step["attempt_id"])
    metadata, body = read_item(path)
    assert metadata["status"] == "archived"
    assert sum(line.startswith("### ") for line in body.splitlines()) == len(FIXTURE["rounds"])
    assert len(seen) == len(FIXTURE["rounds"])


def test_system_design_can_omit_outcome_and_still_advance(vault):
    write_item(vault, domain="system-design")
    result = review.record(
        "lc-1", {"attempt_id": "r1", "reflection": "ok"}, date(2026, 11, 21), INTERVALS, RETRY, True,
    )
    assert result["recorded"] is True
    assert result["next_review"] == "2026-11-22"
    assert result["last_outcome"] == "completed"
    assert result["completed_design_rounds"] == 1


def test_concurrent_design_registration_counts_each_attempt_once(vault):
    write_item(vault, domain="system-design")

    def save(attempt):
        return review.record(
            "lc-1", {"attempt_id": attempt, "outcome": "assisted", "reflection": "ok"},
            date(2026, 11, 21), INTERVALS, RETRY, True,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        duplicates = list(pool.map(save, ["same", "same"]))
    assert sorted(item["recorded"] for item in duplicates) == [False, True]
    metadata, _ = read_item(vault / "Learning/Practice/Review/Items/lc-1.md")
    assert metadata["review_count"] == 1
    assert metadata["attempt_ids"] == ["same"]

    with ThreadPoolExecutor(max_workers=2) as pool:
        distinct = list(pool.map(save, ["left", "right"]))
    assert all(item["recorded"] for item in distinct)
    metadata, _ = read_item(vault / "Learning/Practice/Review/Items/lc-1.md")
    assert metadata["review_count"] == 3
    assert sorted(metadata["attempt_ids"]) == ["left", "right", "same"]


def test_recalculate_moves_bitly_round_four_to_december_2(vault):
    path = vault / "Learning/Practice/Review/Items/sysd-url-shortener.md"
    review.write_note(path, {
        "id": "sysd-url-shortener", "domain": "system-design", "title": "Design a URL Shortener (Bitly)",
        "status": "active", "prompt": "Design Bitly.", "review_count": 3, "stage": 1,
        "completed_design_rounds": 3, "last_review": date(2026, 11, 25),
        "next_review": date(2026, 11, 26), "last_outcome": "assisted",
        "attempt_ids": ["r1", "r2", "r3"],
    }, "# Design a URL Shortener (Bitly)\n")
    history = (
        "\n\n### 2026-11-21 · Round 1\n\n**assisted** · Next review 2026-11-22\n"
        "\n### 2026-11-22 · Round 2\n\n**assisted** · Next review 2026-11-25\n"
        "\n### 2026-11-25 · Round 3\n\n**assisted** · Next review 2026-11-26\n"
    )
    path.write_text(path.read_text(encoding="utf-8") + history, encoding="utf-8")
    preserved = path.read_text(encoding="utf-8").split("---", 2)[2]
    algorithm = vault / "Learning/Practice/Review/Items/lc-9.md"
    review.write_note(algorithm, {
        "id": "lc-9", "domain": "algorithm", "title": "LC 9", "status": "active",
        "prompt": "Keep.", "review_count": 1, "stage": 0, "last_review": date(2026, 11, 20),
        "next_review": date(2026, 11, 21), "attempt_ids": ["a"],
    }, "algorithm history stays\n")
    algorithm_bytes = algorithm.read_bytes()
    archived = vault / "Learning/Practice/Review/Items/sysd-archived.md"
    review.write_note(archived, {
        "id": "sysd-archived", "domain": "system-design", "title": "Old", "status": "archived",
        "prompt": "Old", "review_count": 6, "stage": 4, "completed_design_rounds": 6,
        "last_review": date(2026, 1, 1), "next_review": None, "attempt_ids": [],
    }, "historical event 2026-01-01\n")
    report = review.recalculate(INTERVALS, RETRY, True)
    assert report["updated"] == [{
        "id": "sysd-url-shortener", "next_review": "2026-12-02", "stage": 2,
        "completed_design_rounds": 3,
    }]
    metadata, _ = read_item(path)
    assert metadata["next_review"] == date(2026, 12, 2)
    assert path.read_text(encoding="utf-8").split("---", 2)[2] == preserved
    assert algorithm.read_bytes() == algorithm_bytes
    assert "historical event 2026-01-01" in archived.read_text(encoding="utf-8")
    assert review.recalculate(INTERVALS, RETRY, True)["unchanged"] == ["sysd-url-shortener"]


def _progress(vault, folder, text):
    path = vault / "Learning/Practice/System-Design/Solutions" / folder / "progress.md"
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_profile_links_shared_concepts_and_ignores_unrelated_ones(vault):
    _progress(vault, "Bitly-2026-11-25", """---
topic: Bitly
round_id: f4c30a79-791c-4ad3-9c4e-72b034576b15
review_item_id: sysd-url-shortener
tags: [system-design/done]
---
# Bitly

## Progress

Learner proposed cache expiration bounded by link expiry, then recorded HTTP cache headers after interviewer guidance.
""")
    _progress(vault, "Cache-2026-11-26", """---
topic: Cache
round_id: cache-round
review_item_id: sysd-cache
tags: [system-design/done]
---
# Cache

## Assessment

The learner explained cache expiry again, and repeated the browser-header gap.
""")
    bitly = design_profile.APPROVED_BACKFILL[-2:]
    other = {
        "progress": "Learning/Practice/System-Design/Solutions/Cache-2026-11-26/progress.md",
        "locator": "repeated the browser-header gap",
        "observation": {
            "observation_id": "cache-r1-expiry-01",
            "attempt_id": "cache-round",
            "concept_id": "cache.expiry",
            "performance": "weak",
            "summary": "Again needed help explaining browser cache headers.",
            "anchor": "Assessment",
            "date": "2026-11-26",
            "learner": True,
            "error_id": "cache.expiry.http-cache",
        },
    }
    unrelated = {
        "progress": "Learning/Practice/System-Design/Solutions/Cache-2026-11-26/progress.md",
        "locator": "this sentence is not in the note",
        "observation": {
            "observation_id": "cache-missing",
            "attempt_id": "cache-round",
            "concept_id": "storage.unrelated",
            "performance": "weak",
            "summary": "Not locatable.",
            "anchor": "Assessment",
            "date": "2026-11-26",
            "learner": True,
        },
    }
    first = design_profile.apply_backfill(vault, [*bitly, other, unrelated])
    assert first["applied"] == ["bitly-r3-expiry-01", "bitly-r3-expiry-02", "cache-r1-expiry-01"]
    assert first["skipped"] == [{
        "progress": unrelated["progress"], "reason": "locator missing",
    }]
    second = design_profile.apply_backfill(vault, [*bitly, other])
    assert second["applied"] == []
    assert set(second["unchanged"]) == {"bitly-r3-expiry-01", "bitly-r3-expiry-02", "cache-r1-expiry-01"}
    model = design_profile.rebuild(vault)
    again = design_profile.rebuild(vault)
    profile = (vault / "Learning/Practice/System-Design/Profile.md").read_text(encoding="utf-8")
    assert profile == design_profile.render_profile(again)
    assert model["concepts"]["cache.expiry"]["repeated"]
    assert "Bitly-2026-11-25/progress.md#Progress" in profile
    assert "storage.unrelated" not in profile
    selected = design_profile.outline(
        ["cache.expiry", "cache.invalidation", "scaling.sharding"], model,
    )
    rendered = json.dumps(selected)
    assert "storage.unrelated" not in rendered
    assert selected["follow_ups"][0]["concept_id"] == "cache.expiry"
    assert any(
        "Bitly-2026-11-25/progress.md#Progress" in link
        for link in selected["follow_ups"][0]["repeated"][0]["links"]
    )
    assert any(
        "Cache-2026-11-26/progress.md#Assessment" in link
        for link in selected["follow_ups"][0]["evidence"]
    )
    assert [item["concept_id"] for item in selected["uncovered"]] == [
        "cache.invalidation", "scaling.sharding",
    ]
    assert [item["concept_id"] for item in selected["core"]] == [
        "cache.expiry", "cache.invalidation", "scaling.sharding",
    ]


def test_profile_failure_keeps_the_round_and_observation_once(vault, monkeypatch):
    domain = "system-design"
    review_root = vault / "Learning/Practice/Review"
    monkeypatch.setattr(review, "REVIEW", review_root)
    (review_root / "Content").mkdir(parents=True)
    (review_root / "Content/system-design.md").touch()
    (vault / "flow.md").touch()
    path = _progress(vault, "Bitly-2026-11-25", "---\ntags: [system-design/wip]\ntopic: Bitly\n---\n# Bitly\n")
    topic = {
        "id": "sysd-url-shortener", "title": "Bitly", "domain": domain,
        "prompt": "Design Bitly.", "concept_ids": ["cache.expiry"],
    }
    attempt = {
        "attempt_id": "round-1", "outcome": "assisted", "reflection": "Bound the cache.",
        "concept_observations": [{
            "observation_id": "bitly-r3-expiry-01",
            "concept_id": "cache.expiry",
            "performance": "partial",
            "summary": "Proposed an upper bound on cache lifetime.",
            "anchor": "Progress",
        }],
    }
    args = (topic, attempt, path, date(2026, 11, 25), (INTERVALS, RETRY, {domain: "flow.md"}, True))
    original = design_profile.atomic_write

    def fail_once(target, text):
        raise OSError("index write failed")

    monkeypatch.setattr(design_profile, "atomic_write", fail_once)
    with pytest.raises(OSError, match="index write failed"):
        review.finish(*args)
    item = review_root / "Items/sysd-url-shortener.md"
    metadata, _ = review.read_note(item)
    assert metadata["review_count"] == 1
    assert metadata["attempt_ids"] == ["round-1"]
    progress = path.read_text(encoding="utf-8")
    assert [item["observation_id"] for item in design_profile.parse_fences(progress)] == ["bitly-r3-expiry-01"]
    assert "system-design/wip" in progress
    monkeypatch.setattr(design_profile, "atomic_write", original)
    receipt = review.finish(*args)
    assert receipt["review_count"] == 1
    assert receipt["recorded"] if "recorded" in receipt else receipt["verified"]
    rebuilt = (vault / "Learning/Practice/System-Design/Profile.md").read_text(encoding="utf-8")
    assert rebuilt.count("bitly-r3-expiry-01") == 1
    assert [item["observation_id"] for item in design_profile.parse_fences(path.read_text(encoding="utf-8"))] == ["bitly-r3-expiry-01"]


def test_round_six_summary_cites_existing_observations(vault, monkeypatch):
    domain = "system-design"
    review_root = vault / "Learning/Practice/Review"
    monkeypatch.setattr(review, "REVIEW", review_root)
    (review_root / "Content").mkdir(parents=True)
    (review_root / "Content/system-design.md").touch()
    (vault / "flow.md").touch()
    topic = {"id": "lc-1", "title": "LC 1 - Two Sum", "domain": domain, "prompt": "Find two numbers."}
    earlier = _progress(vault, "Bitly-2026-11-21", "---\ntags: [system-design/done]\nreview_item_id: lc-1\n---\n# Bitly\n")
    design_profile.atomic_write(earlier, earlier.read_text(encoding="utf-8") + (
        "\n## Assessment\n\n```practice-observations\n"
        + yaml.safe_dump([{
            "observation_id": "bitly-r1-sharding-01",
            "attempt_id": "ffb81e2f-2c17-4a91-9c42-5b6c9e0fd9a4",
            "concept_id": "scaling.sharding",
            "performance": "mastered",
            "summary": "Rejected sharding because one instance can handle the load.",
            "anchor": "Learner Reflections (Verbatim)",
            "date": "2026-11-21",
            "learner": True,
        }], allow_unicode=True, sort_keys=False)
        + "```\n"
    ))
    write_item(vault, domain=domain, completed_design_rounds=5, review_count=5, stage=4,
               last_review=date(2026, 11, 20), next_review=date(2027, 1, 19),
               attempt_ids=["r1", "r2", "r3", "r4", "r5"])
    closing = _progress(vault, "Bitly-2027-01-19", "---\ntags: [system-design/wip]\ntopic: Bitly\n---\n# Bitly\n")
    attempt = {"attempt_id": "r6", "outcome": "assisted", "reflection": "Close the topic."}
    receipt = review.finish(
        topic, attempt, closing, date(2027, 1, 19), (INTERVALS, RETRY, {domain: "flow.md"}, True),
    )
    assert receipt["status"] == "archived"
    assert receipt["next_review"] is None
    summary = closing.read_text(encoding="utf-8")
    assert summary.count("## Round summary") == 1
    assert "bitly-r1-sharding-01" not in summary.split("## Round summary")[0]
    assert "scaling.sharding" in summary.split("## Round summary")[1]
    review.finish(
        topic, attempt, closing, date(2027, 1, 19), (INTERVALS, RETRY, {domain: "flow.md"}, True),
    )
    assert closing.read_text(encoding="utf-8").count("## Round summary") == 1

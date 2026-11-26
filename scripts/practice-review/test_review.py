"""Scheduling tests for the practice-review CLI.

Run: python -m pytest scripts/practice-review/test_review.py
"""

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
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


def test_design_rounds_follow_the_shared_completion_schedule(vault):
    path = write_item(vault, domain="system-design")
    seen = set()
    for step in FIXTURE["rounds"]:
        payload = {
            "attempt_id": step["attempt_id"], "outcome": step["outcome"], "reflection": "ok",
        }
        def save(_):
            return review.record(
                "lc-1", payload, date.fromisoformat(step["date"]),
                FIXTURE["intervals"], FIXTURE["retry_days"], True,
            )

        with ThreadPoolExecutor(max_workers=step.get("concurrent_copies", 1)) as pool:
            receipts = list(pool.map(save, range(step.get("concurrent_copies", 1))))
        assert sum(receipt["recorded"] for receipt in receipts) == 1
        result = next(receipt for receipt in receipts if receipt["recorded"])
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
    topic = {"id": "lc-1", "title": "Bitly", "domain": domain, "prompt": "Design Bitly."}
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
    write_item(vault, domain=domain, title="Bitly", completed_design_rounds=5, review_count=5, stage=4,
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


@pytest.mark.parametrize("summary", [r"C:\uploads", r"literal \1 and \g<1> and \n"])
def test_observation_in_existing_assessment_preserves_literal_text(summary):
    observation = design_profile.normalize_stored({
        "observation_id": "literal", "attempt_id": "r1", "concept_id": "cache.expiry",
        "performance": "partial", "summary": summary, "anchor": "Assessment",
        "date": "2026-11-26",
    })
    updated = design_profile.upsert_observations("## Assessment\n\nExisting assessment\n", [observation])
    assert design_profile.parse_fences(updated) == [observation]
    assert "Existing assessment" in updated


@pytest.mark.parametrize("later_day", ["2026-11-26", "2026-11-27"])
def test_latest_answer_overrides_weak_evidence_without_discarding_it(vault, later_day):
    observations = [{
        "observation_id": "z-first", "attempt_id": "r1", "concept_id": "cache.expiry",
        "performance": "weak", "summary": "Needed help.", "anchor": "First answer",
        "date": "2026-11-26",
    }, {
        "observation_id": "a-later", "attempt_id": "r1", "concept_id": "cache.expiry",
        "performance": "mastered", "summary": "Explained the constraint.", "anchor": "Later answer",
        "date": later_day,
    }]
    _progress(vault, "Bitly", design_profile.render_fence(observations))
    model = design_profile.rebuild(vault)
    concept = model["concepts"]["cache.expiry"]
    assert concept["state"] == concept["latest"] == "mastered"
    assert [item["observation_id"] for item in concept["contrary"]] == ["z-first"]
    assert [item["observation_id"] for item in concept["observations"]] == ["z-first", "a-later"]
    assert concept["evidence"] == [concept["observations"][-1]["link"]]
    outline = review.question_outline(concept_ids=["cache.expiry"])
    assert not outline["follow_ups"]
    assert outline["spot_checks"][0]["evidence"] == concept["evidence"]
    summary = design_profile.round_summary(design_profile.collect(vault))
    assert "cache.expiry" in summary.split("### Mastered")[1].split("### Still weak")[0]
    assert "cache.expiry" not in summary.split("### Still weak")[1]
    assert design_profile.rebuild(vault) == model


def test_known_same_day_evidence_order_survives_cross_session_rebuild(vault):
    base = {
        "attempt_id": "r1", "concept_id": "cache.expiry", "summary": "Answer",
        "anchor": "Assessment", "date": "2026-11-26",
    }
    _progress(vault, "Z-early", design_profile.render_fence([
        {**base, "observation_id": "z-first", "performance": "weak", "evidence_order": 1},
    ]))
    _progress(vault, "A-late", design_profile.render_fence([
        {**base, "observation_id": "a-later", "attempt_id": "r2", "performance": "mastered", "evidence_order": 2},
    ]))
    model = design_profile.rebuild(vault)
    concept = model["concepts"]["cache.expiry"]
    assert concept["latest"] == "mastered"
    assert [item["evidence_order"] for item in concept["observations"]] == [1, 2]
    assert all("timestamp" not in item for item in concept["observations"])


def test_first_round_cli_outline_uses_topic_concepts_without_registration(vault, monkeypatch, capsys):
    monkeypatch.setattr(review, "load_config", lambda: (INTERVALS, RETRY, {}, True))
    monkeypatch.setattr("sys.argv", ["review.py", "outline", "--concept-ids", "cache.expiry", "id.counter"])
    review.main()
    outline = json.loads(capsys.readouterr().out)
    assert outline["concept_ids"] == ["cache.expiry", "id.counter"]
    assert [item["concept_id"] for item in outline["core"]] == outline["concept_ids"]
    assert [item["concept_id"] for item in outline["uncovered"]] == outline["concept_ids"]
    assert not list(review.ITEMS.glob("*.md"))
    path = write_item(vault, domain="system-design", concept_ids=outline["concept_ids"])
    assert review.question_outline("lc-1") == outline
    assert path.is_file()


@pytest.mark.parametrize("archive", [False, True])
def test_recalculate_six_legacy_completions_normalizes_lifecycle(vault, archive):
    history = "".join(
        f"\n### {step['date']} · Round {i}\n\n**{step['outcome']}** · Next review legacy\n"
        for i, step in enumerate(FIXTURE["rounds"], 1)
    )
    path = write_item(vault, domain="system-design", review_count=len(FIXTURE["rounds"]),
                      last_review=date(2027, 1, 19), next_review=date(2027, 1, 20), stage=1)
    metadata, _ = read_item(path)
    review.write_note(path, metadata, history)
    queue = review.due(date(2027, 1, 20), INTERVALS, RETRY, archive)
    assert not queue["upcoming"]
    assert not queue["unstarted"]
    shown = review.show("lc-1", INTERVALS, RETRY, archive)
    assert shown["status"] == "archived"
    report = review.recalculate(INTERVALS, RETRY, archive)
    assert len(report["updated"]) == 1
    metadata, body = read_item(path)
    assert metadata["status"] == "archived"
    assert metadata["completed_design_rounds"] == 6
    assert metadata["last_review"] == date(2027, 1, 19)
    assert metadata["archived_on"] == date(2027, 1, 19)
    assert metadata["next_review"] is None
    assert body == history
    assert not review.recalculate(INTERVALS, RETRY, archive)["updated"]


def test_design_completion_closes_at_round_six_for_other_interval_lengths(vault):
    for intervals in ([1, 3, 7], [1, 3, 7, 14, 60, 90]):
        item_id = f"sd-{len(intervals)}"
        path = vault / "Learning/Practice/Review/Items" / f"{item_id}.md"
        review.write_note(path, {
            "id": item_id, "domain": "system-design", "title": "Bitly",
            "status": "active", "prompt": "Design Bitly.", "review_count": 0,
            "stage": 0, "last_review": None, "next_review": None, "attempt_ids": [],
        }, "# Bitly\n\n## 练习记录\n")
        day = date(2026, 11, 20)
        for number in range(1, 6):
            result = review.record(item_id, {
                "attempt_id": f"r{number}", "outcome": "assisted", "reflection": "done",
            }, day, intervals, 1, False)
            day += timedelta(days=intervals[min(number - 1, len(intervals) - 1)])
            assert result["next_review"] == day.isoformat()
            assert result["status"] == "active"
            assert result["completed_design_rounds"] == number
        retry = review.record(item_id, {
            "attempt_id": "r6-retry", "outcome": "incomplete", "reflection": "not yet",
        }, day, intervals, 1, True)
        assert retry["status"] == "active"
        assert retry["completed_design_rounds"] == 5
        assert retry["next_review"] == (day + timedelta(days=1)).isoformat()
        final_day = day + timedelta(days=1)
        final = review.record(item_id, {
            "attempt_id": "r6", "outcome": "assisted", "reflection": "final",
        }, final_day, intervals, 1, False)
        assert final["status"] == "archived"
        assert final["next_review"] is None
        assert final["completed_design_rounds"] == 6
        saved, _ = read_item(path)
        assert saved["archived_on"] == final_day
    algorithm = review.schedule_round(
        4, date(2026, 12, 1), None, "independent", date(2026, 12, 2),
        [1, 3, 7, 14, 60], 1, False,
    )
    assert algorithm == (4, date(2027, 1, 31))


def test_round_six_summary_follows_the_fixed_round_not_the_interval_length(vault, monkeypatch):
    review_root = vault / "Learning/Practice/Review"
    monkeypatch.setattr(review, "REVIEW", review_root)
    (review_root / "Content").mkdir(exist_ok=True)
    (review_root / "Content/system-design.md").touch()
    (vault / "flow.md").touch()
    for intervals in ([1, 3, 7], [1, 3, 7, 14, 60, 90]):
        item_id = f"summary-{len(intervals)}"
        topic = {"id": item_id, "title": "Bitly", "domain": "system-design", "prompt": "Design Bitly."}
        config = (intervals, 1, {"system-design": "flow.md"}, False)
        day = date(2026, 11, 20)
        for number in range(1, 7):
            path = vault / "Learning/Practice/System-Design/Solutions" / f"{item_id}-r{number}" / "progress.md"
            path.parent.mkdir(parents=True)
            review.write_note(path, {"topic": "Bitly", "tags": ["system-design/wip"]}, "# Bitly\n")
            receipt = review.finish(
                topic, {"attempt_id": f"r{number}", "reflection": "done"}, path, day, config,
            )
            if number < 6:
                assert receipt["status"] == "active"
                assert "## Round summary" not in path.read_text(encoding="utf-8")
                day = date.fromisoformat(receipt["next_review"])
            else:
                assert receipt["status"] == "archived"
                assert receipt["attempt_completed_round"] == 6
                assert path.read_text(encoding="utf-8").count("## Round summary") == 1


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
    (script.parent / "design_profile.py").write_text(
        Path(design_profile.__file__).read_text(encoding="utf-8"), encoding="utf-8")
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

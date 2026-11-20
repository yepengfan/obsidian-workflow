from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest

from design_coaching import complete, mode


def test_guided_rounds_are_shared_and_overrides_are_local(tmp_path):
    log = tmp_path / "Log/coaching-rounds.md"
    first, second = str(uuid4()), str(uuid4())
    assert mode(log, "mock_interview")["default_mode"] == "guided"
    assert not log.exists()
    assert complete(log, first)["guided_rounds_remaining"] == 1
    assert not complete(log, first.upper())["added"]
    assert mode(log)["mode"] == "guided"
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(result["added"] for result in pool.map(lambda id_: complete(log, id_), [second, second])) == 1
    assert mode(log, "guided")["mode"] == "guided"
    assert mode(log)["mode"] == "mock_interview"
    assert not complete(log, str(uuid4()))["added"]
    assert log.read_text() == f"# System Design coaching rounds\n\n- {first}\n- {second}\n"


def test_preserves_an_unrecognized_note(tmp_path):
    log = tmp_path / "coaching-rounds.md"
    log.write_text("# Existing private note\n")
    with pytest.raises(ValueError):
        complete(log, str(uuid4()))
    assert log.read_text() == "# Existing private note\n"

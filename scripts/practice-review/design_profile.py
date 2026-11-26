"""Rebuild the System Design profile from assessment observations.

Observations in each session's progress note are the facts. Profile.md is a
replaceable index. Interviewer-supplied answers are not learner evidence.
"""

import os
import re
import tempfile
from datetime import date
from pathlib import Path

import yaml


CONCEPT_ID = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*")
OBSERVATION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
PERFORMANCES = {"mastered", "partial", "weak", "uncovered"}
EVIDENCED = {"mastered", "partial", "weak"}
FENCE = re.compile(r"```practice-observations\r?\n(.*?)```", re.DOTALL)
PROFILE_PATH = Path("Learning/Practice/System-Design/Profile.md")
SOLUTIONS = Path("Learning/Practice/System-Design/Solutions")

# Approved backfill. A row is written only when its locator is present in the
# named progress note, so an assessment that cannot be tied to an answer is left
# for a later session.
APPROVED_BACKFILL = [
    {
        "progress": "Learning/Practice/System-Design/Solutions/Bitly-2026-11-21/progress.md",
        "locator": "I wouldn't introduce sharding as the single instance can handle the load well.",
        "observation": {
            "observation_id": "bitly-r1-sharding-01",
            "attempt_id": "ffb81e2f-2c17-4a91-9c42-5b6c9e0fd9a4",
            "concept_id": "scaling.sharding",
            "performance": "mastered",
            "summary": "Rejected sharding because one database instance can handle the estimated load.",
            "anchor": "Learner Reflections (Verbatim)",
            "date": "2026-11-21",
            "learner": True,
        },
    },
    {
        "progress": "Learning/Practice/System-Design/Solutions/Bitly-2026-11-21/progress.md",
        "locator": "i would accept the temporary 404",
        "observation": {
            "observation_id": "bitly-r1-replica-01",
            "attempt_id": "ffb81e2f-2c17-4a91-9c42-5b6c9e0fd9a4",
            "concept_id": "consistency.replica-lag",
            "performance": "partial",
            "summary": "Accepted a temporary 404 after creation to avoid reading the primary on every miss.",
            "anchor": "Learner Reflections (Verbatim)",
            "date": "2026-11-21",
            "learner": True,
        },
    },
    {
        "progress": "Learning/Practice/System-Design/Solutions/Bitly-2026-11-22/progress.md",
        "locator": "the global counter is also a single point of failure",
        "observation": {
            "observation_id": "bitly-r2-counter-01",
            "attempt_id": "5b54cfd8-1e35-47d4-9364-dde670e7e732",
            "concept_id": "id.counter",
            "performance": "partial",
            "summary": "Identified the global counter as a single point of failure.",
            "anchor": "Learner statements from this round (not a formal final reflection)",
            "date": "2026-11-22",
            "learner": True,
        },
    },
    {
        "progress": "Learning/Practice/System-Design/Solutions/Bitly-2026-11-25/progress.md",
        "locator": "proposed cache expiration bounded by link expiry",
        "observation": {
            "observation_id": "bitly-r3-expiry-01",
            "attempt_id": "f4c30a79-791c-4ad3-9c4e-72b034576b15",
            "concept_id": "cache.expiry",
            "performance": "partial",
            "summary": "Proposed an upper bound on cache lifetime tied to the link expiry.",
            "anchor": "Progress",
            "date": "2026-11-25",
            "learner": True,
        },
    },
    {
        "progress": "Learning/Practice/System-Design/Solutions/Bitly-2026-11-25/progress.md",
        "locator": "HTTP cache headers after interviewer guidance",
        "observation": {
            "observation_id": "bitly-r3-expiry-02",
            "attempt_id": "f4c30a79-791c-4ad3-9c4e-72b034576b15",
            "concept_id": "cache.expiry",
            "performance": "weak",
            "summary": "Browser cache headers were added only after interviewer guidance.",
            "anchor": "Progress",
            "date": "2026-11-25",
            "learner": True,
            "error_id": "cache.expiry.http-cache",
        },
    },
]


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent,
            prefix=".profile-", suffix=".tmp", delete=False,
        ) as file:
            temporary = Path(file.name)
            file.write(text)
            file.flush()
            os.fsync(file.fileno())
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def parse_fences(text):
    observations = []
    for match in FENCE.finditer(text):
        loaded = yaml.safe_load(match.group(1))
        if loaded is None:
            continue
        if not isinstance(loaded, list):
            raise ValueError("practice observations must be a list")
        observations.extend(loaded)
    return observations


def _date_text(value):
    if isinstance(value, date):
        value = value.isoformat()
    elif hasattr(value, "isoformat") and not isinstance(value, str):
        value = value.isoformat()
    return str(value)


def _identifier(value, pattern, field):
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise ValueError(f"{field} is invalid")
    return value


def normalize_observation(raw, attempt_id, day):
    if not isinstance(raw, dict):
        raise ValueError("concept observation must be an object")
    observation = {
        "observation_id": _identifier(raw.get("observation_id"), OBSERVATION_ID, "observation_id"),
        "attempt_id": _identifier(raw.get("attempt_id", attempt_id), OBSERVATION_ID, "attempt_id"),
        "concept_id": _identifier(raw.get("concept_id"), CONCEPT_ID, "concept_id"),
        "performance": raw.get("performance"),
        "summary": raw.get("summary", ""),
        "anchor": raw.get("anchor", ""),
        "date": _date_text(raw.get("date", day)),
        "learner": raw.get("learner", True),
    }
    if observation["attempt_id"] != attempt_id:
        raise ValueError("observation attempt_id must match the round")
    if observation["performance"] not in PERFORMANCES:
        raise ValueError("performance must be mastered, partial, weak or uncovered")
    if not isinstance(observation["summary"], str) or not observation["summary"].strip():
        raise ValueError("observation summary must be a nonempty string")
    if not isinstance(observation["anchor"], str) or not observation["anchor"].strip():
        raise ValueError("observation anchor must be a nonempty string")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(observation["date"])):
        raise ValueError("observation date must use YYYY-MM-DD")
    if type(observation["learner"]) is not bool:
        raise ValueError("learner must be true or false")
    error_id = raw.get("error_id", "")
    if error_id:
        observation["error_id"] = _identifier(error_id, CONCEPT_ID, "error_id")
    return observation


def merge_observations(existing, incoming):
    merged = []
    index = {}
    for observation in [*existing, *incoming]:
        key = observation["observation_id"]
        previous = index.get(key)
        if previous is None:
            index[key] = len(merged)
            merged.append(observation)
        elif merged[previous] != observation:
            raise ValueError(f"observation {key} conflicts with a saved copy")
    return merged


def render_fence(observations):
    body = yaml.safe_dump(observations, allow_unicode=True, sort_keys=False)
    return f"```practice-observations\n{body}```\n"


def upsert_observations(body, incoming):
    if not incoming:
        return body
    existing = [normalize_stored(item) for item in parse_fences(body)]
    merged = merge_observations(existing, incoming)
    fence = render_fence(merged)
    matches = list(FENCE.finditer(body))
    if matches:
        updated = body[:matches[0].start()] + fence + body[matches[0].end():]
        return _drop_extra_fences(updated)
    block = f"## Assessment\n\n{fence}"
    if "## Assessment" in body:
        return re.sub(r"(## Assessment\s*\n)", r"\1\n" + fence, body, count=1)
    return body.rstrip() + "\n\n" + block


def _drop_extra_fences(text):
    seen = False

    def keep_first(match):
        nonlocal seen
        if seen:
            return ""
        seen = True
        return match.group(0)

    return FENCE.sub(keep_first, text)


def normalize_stored(raw):
    """Accept an observation already written into a progress note."""
    if not isinstance(raw, dict):
        raise ValueError("stored observation must be an object")
    return normalize_observation(raw, raw.get("attempt_id"), raw.get("date"))


def evidence_link(source, anchor):
    return f"[[{source}#{anchor}]]"


def collect(root):
    solutions = root / SOLUTIONS
    found = []
    if not solutions.is_dir():
        return found
    for path in sorted(solutions.glob("*/progress.md")):
        text = path.read_text(encoding="utf-8")
        source = path.relative_to(root).as_posix()
        for raw in parse_fences(text):
            observation = normalize_stored(raw)
            observation["source"] = source
            observation["link"] = evidence_link(source, observation["anchor"])
            found.append(observation)
    deduped = []
    seen = {}
    for observation in found:
        key = observation["observation_id"]
        previous = seen.get(key)
        comparable = {name: observation[name] for name in observation if name not in ("source", "link")}
        if previous is None:
            seen[key] = comparable
            deduped.append(observation)
        elif previous != comparable:
            raise ValueError(f"observation {key} conflicts across sessions")
    deduped.sort(key=lambda item: (item["concept_id"], item["date"], item["observation_id"]))
    return deduped


def _latest_state(observations):
    evidenced = [item for item in observations if item["learner"] and item["performance"] in EVIDENCED]
    if not evidenced:
        return "uncovered", "uncovered", None
    latest_date = max(item["date"] for item in evidenced)
    current = [item for item in evidenced if item["date"] == latest_date]
    performances = {item["performance"] for item in current}
    if "mastered" in performances and performances & {"partial", "weak"}:
        latest = "inconsistent"
    elif "partial" in performances:
        latest = "partial"
    elif "weak" in performances:
        latest = "weak"
    else:
        latest = "mastered"
    return latest, latest, latest_date


def build_model(observations):
    grouped = {}
    for observation in observations:
        if not observation["learner"]:
            continue
        grouped.setdefault(observation["concept_id"], []).append(observation)
    concepts = {}
    for concept_id, items in grouped.items():
        items = sorted(items, key=lambda item: (item["date"], item["observation_id"]))
        latest, _, last_observed = _latest_state(items)
        evidenced = [item for item in items if item["performance"] in EVIDENCED]
        latest_date = max((item["date"] for item in evidenced), default=None)
        current = [item for item in evidenced if item["date"] == latest_date]
        contrary = []
        state = latest
        if latest in EVIDENCED:
            mastered_now = latest == "mastered"
            for item in evidenced:
                if item["date"] == latest_date:
                    continue
                earlier_mastered = item["performance"] == "mastered"
                if earlier_mastered != mastered_now:
                    state = "inconsistent"
                    contrary.append(item)
        repeated = []
        by_error = {}
        for item in items:
            error_id = item.get("error_id")
            if error_id and item["performance"] in {"partial", "weak"}:
                by_error.setdefault(error_id, []).append(item)
        for error_id, matches in sorted(by_error.items()):
            attempts = {item["attempt_id"] for item in matches}
            if len(attempts) >= 2:
                repeated.append({
                    "error_id": error_id,
                    "links": [item["link"] for item in matches],
                })
        latest_links = [item["link"] for item in current] or [items[-1]["link"]]
        concepts[concept_id] = {
            "state": state,
            "latest": latest,
            "last_observed": last_observed or items[-1]["date"],
            "evidence": latest_links,
            "observations": items,
            "repeated": repeated,
            "contrary": contrary,
        }
    return {"concepts": concepts}


def render_profile(model):
    lines = [
        "---",
        "tags:",
        "  - system-design/profile",
        "generated: true",
        "---",
        "",
        "# System Design profile",
        "",
        "Rebuilt from session assessments. Edit those observations and rebuild this index; do not edit it by hand.",
        "",
    ]
    if not model["concepts"]:
        lines.append("No evidenced concepts yet.")
        lines.append("")
        return "\n".join(lines)
    for concept_id in sorted(model["concepts"]):
        concept = model["concepts"][concept_id]
        lines.extend([
            f"## {concept_id}",
            "",
            f"- State: {concept['state']}",
            f"- Latest conclusion: {concept['latest']}",
            f"- Last observed: {concept['last_observed']}",
        ])
        for link in concept["evidence"]:
            lines.append(f"- Evidence: {link}")
        lines.extend(["", "### Observations", ""])
        for item in concept["observations"]:
            lines.append(
                f"- {item['date']} · {item['observation_id']} · {item['performance']} · {item['summary']} · {item['link']}"
            )
        lines.extend(["", "### Repeated errors", ""])
        if concept["repeated"]:
            for item in concept["repeated"]:
                lines.append(f"- {item['error_id']}: {', '.join(item['links'])}")
        else:
            lines.append("None.")
        lines.extend(["", "### Contrary evidence", ""])
        if concept["contrary"]:
            for item in concept["contrary"]:
                lines.append(f"- {item['date']} · {item['performance']} · {item['link']}")
        else:
            lines.append("None.")
        lines.append("")
    return "\n".join(lines)


def rebuild(root):
    model = build_model(collect(root))
    text = render_profile(model)
    target = root / PROFILE_PATH
    previous = target.read_text(encoding="utf-8") if target.exists() else None
    if previous != text:
        atomic_write(target, text)
    return model


def outline(concept_ids, model):
    questions = []
    follow_ups = []
    uncovered = []
    spot_checks = []
    for concept_id in concept_ids:
        _identifier(concept_id, CONCEPT_ID, "concept_id")
        questions.append({
            "concept_id": concept_id,
            "phase": "core",
            "reason": "Ask this problem's concept before selecting follow-ups.",
        })
        concept = model["concepts"].get(concept_id)
        if concept is None or concept["latest"] == "uncovered":
            uncovered.append({
                "concept_id": concept_id,
                "phase": "uncovered",
                "reason": "No prior learner evidence. Use a first diagnostic question.",
                "evidence": [],
            })
        elif concept["state"] == "mastered" and concept["latest"] == "mastered":
            spot_checks.append({
                "concept_id": concept_id,
                "phase": "spot_check",
                "reason": "Latest evidence shows this concept is mastered. A variant can spot-check it.",
                "evidence": concept["evidence"],
            })
        else:
            follow_ups.append({
                "concept_id": concept_id,
                "phase": "follow_up",
                "reason": f"Latest conclusion is {concept['latest']}.",
                "evidence": concept["evidence"],
                "repeated": concept["repeated"],
            })
    return {
        "concept_ids": list(concept_ids),
        "core": questions,
        "follow_ups": follow_ups,
        "uncovered": uncovered,
        "spot_checks": spot_checks,
    }


def round_summary(observations):
    model = build_model(observations)
    lines = [
        "## Round summary",
        "",
        "This closing summary cites existing observations and is not a new observation.",
        "",
    ]
    mastered, weak, repeated = [], [], []
    for concept_id in sorted(model["concepts"]):
        concept = model["concepts"][concept_id]
        links = ", ".join(concept["evidence"])
        if concept["latest"] == "mastered" and concept["state"] == "mastered":
            mastered.append(f"- {concept_id}: {links}")
        if concept["latest"] in {"partial", "weak"} or concept["state"] == "inconsistent":
            weak.append(f"- {concept_id}: {concept['latest']} · {links}")
        for item in concept["repeated"]:
            repeated.append(f"- {concept_id} / {item['error_id']}: {', '.join(item['links'])}")
    lines.extend(["### Mastered", "", *(mastered or ["None."]), "", "### Still weak", "", *(weak or ["None."])])
    lines.extend(["", "### Repeated errors", "", *(repeated or ["None."]), ""])
    return "\n".join(lines)


def apply_backfill(root, entries=None):
    report = {"applied": [], "unchanged": [], "skipped": []}
    for entry in entries if entries is not None else APPROVED_BACKFILL:
        path = root / entry["progress"]
        if not path.is_file():
            report["skipped"].append({"progress": entry["progress"], "reason": "missing"})
            continue
        text = path.read_text(encoding="utf-8")
        if entry["locator"] not in text:
            report["skipped"].append({"progress": entry["progress"], "reason": "locator missing"})
            continue
        observation = normalize_stored(entry["observation"])
        existing = [normalize_stored(item) for item in parse_fences(text)]
        merged = merge_observations(existing, [observation])
        if merged == existing:
            report["unchanged"].append(entry["observation"]["observation_id"])
            continue
        atomic_write(path, upsert_observations(text, [observation]))
        report["applied"].append(entry["observation"]["observation_id"])
    return report

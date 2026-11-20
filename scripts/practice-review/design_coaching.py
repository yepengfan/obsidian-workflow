"""Read or advance the two-round System Design coaching introduction."""

import argparse
import fcntl
import json
import os
import tempfile
from pathlib import Path
from uuid import UUID

LOG = Path(__file__).resolve().parents[2] / "Learning/Practice/System-Design/Log/coaching-rounds.md"
HEADING = "# System Design coaching rounds\n\n"
INTRO_ROUNDS = 2
MODES = ("guided", "mock_interview")


def round_id(value):
    parsed = UUID(value)
    normalized = str(parsed)
    if normalized != value.lower() or (parsed.int not in (0, (1 << 128) - 1) and parsed.version not in range(1, 9)):
        raise ValueError("Use a hyphenated round UUID")
    return normalized


def read_ids(path):
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    if not text.startswith(HEADING):
        raise ValueError("Invalid coaching log heading")
    lines = text[len(HEADING):].rstrip().split("\n")
    if len(lines) > INTRO_ROUNDS or any(not line.startswith("- ") for line in lines):
        raise ValueError("Invalid coaching log entries")
    ids = [round_id(line[2:]) for line in lines]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate coaching round")
    return ids


def mode(path, override=None):
    remaining = INTRO_ROUNDS - len(read_ids(path))
    default = "guided" if remaining else "mock_interview"
    return {"default_mode": default, "mode": override or default, "guided_rounds_remaining": remaining}


def complete(path, attempt):
    attempt = round_id(attempt)
    path.parent.mkdir(parents=True, exist_ok=True)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        fcntl.flock(directory, fcntl.LOCK_EX)
        ids = read_ids(path)
        added = attempt not in ids and len(ids) < INTRO_ROUNDS
        if added:
            ids.append(attempt)
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as file:
                temporary = Path(file.name)
                try:
                    file.write((HEADING + "".join(f"- {item}\n" for item in ids)).encode())
                    file.flush()
                    os.fsync(file.fileno())
                    temporary.replace(path)
                finally:
                    temporary.unlink(missing_ok=True)
        return {"added": added, "guided_rounds_remaining": INTRO_ROUNDS - len(ids)}
    finally:
        os.close(directory)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("mode").add_argument("--override", choices=MODES)
    commands.add_parser("complete").add_argument("round_id")
    args = parser.parse_args()
    try:
        result = mode(LOG, args.override) if args.command == "mode" else complete(LOG, args.round_id)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()

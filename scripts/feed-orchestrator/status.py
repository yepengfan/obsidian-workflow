"""Feed status file management.

Writes Feeds/.feed-status.json atomically for Home.md polling.
Provides concurrent-run locking (refuses if running feeds < 15 min old).
"""

import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

StatusValue = Literal["pending", "running", "success", "skipped", "failed", "disabled"]

FEED_NAMES = ["ai-digest", "github-trending", "engineering-blogs", "cc-plugins"]


class StatusReporter:
    """Manages Feeds/.feed-status.json for live UI polling."""

    def __init__(self, vault_path: str | Path) -> None:
        self.vault_path = Path(vault_path)
        self.status_file = self.vault_path / "Feeds" / ".feed-status.json"
        self._state: dict[str, Any] = {}

    # ── Public API ──────────────────────────────────────────────────

    def check_concurrent_lock(self, max_age_seconds: int = 900) -> bool:
        """Return True if a run is already in progress (< max_age_seconds old)."""
        if not self.status_file.exists():
            return False
        try:
            data = json.loads(self.status_file.read_text())
            started = data.get("started_at", "")
            if not started:
                return False
            started_ts = datetime.fromisoformat(started).timestamp()
            age = time.time() - started_ts
            if age > max_age_seconds:
                return False  # Stale — safe to proceed
            # Check if any feed is still running
            feeds = data.get("feeds", {})
            return any(f.get("status") == "running" for f in feeds.values())
        except (json.JSONDecodeError, ValueError, KeyError):
            return False

    def write_initial(self) -> None:
        """Write initial status with all feeds as pending."""
        now = _now_iso()
        self._state = {
            "started_at": now,
            "completed_at": None,
            "feeds": {
                name: {
                    "status": "pending",
                    "started_at": None,
                    "completed_at": None,
                    "error": None,
                    "output_path": None,
                    "message": None,
                }
                for name in FEED_NAMES
            },
        }
        self._flush()

    def update_feed(
        self,
        feed_name: str,
        status: StatusValue,
        *,
        message: str | None = None,
        error: str | None = None,
        output_path: str | None = None,
    ) -> None:
        """Update a single feed's status."""
        feed = self._state.setdefault("feeds", {}).setdefault(feed_name, {})
        feed["status"] = status
        feed["message"] = message
        feed["error"] = error
        if status == "running" and not feed.get("started_at"):
            feed["started_at"] = _now_iso()
        if status in ("success", "skipped", "failed", "disabled"):
            feed["completed_at"] = _now_iso()
        if output_path:
            feed["output_path"] = output_path
        self._flush()

    def write_final(self, summary: str | None = None) -> None:
        """Mark the overall run as complete."""
        self._state["completed_at"] = _now_iso()
        if summary:
            self._state["summary"] = summary
        self._flush()

    def get_state(self) -> dict[str, Any]:
        """Return current state dict."""
        return dict(self._state)

    # ── Internals ───────────────────────────────────────────────────

    def _flush(self) -> None:
        """Atomic write: tmp file + rename."""
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=self.status_file.parent, suffix=".tmp", prefix=".status-"
        )
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(self._state, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.status_file)
        except Exception:
            # Clean up tmp file on failure
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

"""Reminders: attach a note/reminder to a profile that shows on load."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from stashenv.store import _stash_dir


def _reminders_path(project: str) -> Path:
    return _stash_dir(project) / "reminders.json"


def _load(project: str) -> dict:
    p = _reminders_path(project)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(project: str, data: dict) -> None:
    p = _reminders_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_reminder(project: str, profile: str, message: str) -> None:
    """Attach a reminder message to a profile."""
    data = _load(project)
    data[profile] = {
        "message": message,
        "created_at": datetime.utcnow().isoformat(),
    }
    _save(project, data)


def get_reminder(project: str, profile: str) -> Optional[dict]:
    """Return the reminder dict for a profile, or None."""
    return _load(project).get(profile)


def clear_reminder(project: str, profile: str) -> bool:
    """Remove a reminder. Returns True if one existed."""
    data = _load(project)
    if profile in data:
        del data[profile]
        _save(project, data)
        return True
    return False


def list_reminders(project: str) -> dict:
    """Return all reminders for a project keyed by profile name."""
    return _load(project)

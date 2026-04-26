"""schedule.py — manage scheduled rotation reminders for profiles.

Allows users to associate a rotation schedule (e.g. every 30 days) with a
profile so stashenv can warn when a profile is overdue for rotation.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir

# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------

def _schedule_path(project: str) -> Path:
    path = _stash_dir(project) / "schedules.json"
    return path


def _load(project: str) -> dict:
    p = _schedule_path(project)
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save(project: str, data: dict) -> None:
    p = _schedule_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def set_schedule(project: str, profile: str, days: int) -> datetime:
    """Set a rotation schedule for *profile* in *project*.

    Parameters
    ----------
    project:
        Project identifier (directory name).
    profile:
        Profile name to schedule.
    days:
        Number of days between expected rotations.

    Returns
    -------
    datetime
        The next rotation due date (UTC).
    """
    if days <= 0:
        raise ValueError("days must be a positive integer")

    now = datetime.now(timezone.utc)
    due = now + timedelta(days=days)

    data = _load(project)
    data[profile] = {
        "interval_days": days,
        "set_at": now.isoformat(),
        "due_at": due.isoformat(),
    }
    _save(project, data)
    return due


def get_schedule(project: str, profile: str) -> Optional[dict]:
    """Return the schedule entry for *profile*, or ``None`` if not set."""
    return _load(project).get(profile)


def clear_schedule(project: str, profile: str) -> bool:
    """Remove the rotation schedule for *profile*.

    Returns ``True`` if an entry existed and was removed, ``False`` otherwise.
    """
    data = _load(project)
    if profile in data:
        del data[profile]
        _save(project, data)
        return True
    return False


def is_overdue(project: str, profile: str) -> bool:
    """Return ``True`` if the profile's rotation is past its due date."""
    entry = get_schedule(project, profile)
    if entry is None:
        return False
    due = datetime.fromisoformat(entry["due_at"])
    return datetime.now(timezone.utc) > due


def list_schedules(project: str) -> list[dict]:
    """Return all scheduled profiles for *project*, sorted by due date."""
    data = _load(project)
    results = []
    for profile, entry in data.items():
        results.append({
            "profile": profile,
            "interval_days": entry["interval_days"],
            "set_at": entry["set_at"],
            "due_at": entry["due_at"],
            "overdue": datetime.now(timezone.utc) > datetime.fromisoformat(entry["due_at"]),
        })
    results.sort(key=lambda r: r["due_at"])
    return results

"""Profile quota management — limit the number of profiles per project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir, list_profiles

_DEFAULT_QUOTA = 20


def _quota_path(project: str) -> Path:
    return _stash_dir(project) / ".quota.json"


def _load(project: str) -> dict:
    p = _quota_path(project)
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save(project: str, data: dict) -> None:
    p = _quota_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_quota(project: str, limit: int) -> None:
    """Set the maximum number of profiles allowed for a project."""
    if limit < 1:
        raise ValueError("Quota limit must be at least 1.")
    data = _load(project)
    data["limit"] = limit
    _save(project, data)


def get_quota(project: str) -> Optional[int]:
    """Return the configured quota limit, or None if not set."""
    data = _load(project)
    return data.get("limit")


def clear_quota(project: str) -> bool:
    """Remove the quota limit for a project. Returns True if one existed."""
    data = _load(project)
    if "limit" not in data:
        return False
    del data["limit"]
    _save(project, data)
    return True


def check_quota(project: str) -> tuple[int, int, bool]:
    """Return (current_count, limit, within_quota).

    Uses _DEFAULT_QUOTA when no explicit limit is set.
    """
    profiles = list_profiles(project)
    current = len(profiles)
    limit = get_quota(project) or _DEFAULT_QUOTA
    return current, limit, current < limit


def enforce_quota(project: str) -> None:
    """Raise QuotaExceededError if the project is at or over its quota."""
    current, limit, ok = check_quota(project)
    if not ok:
        raise QuotaExceededError(
            f"Profile quota reached: {current}/{limit} profiles exist for '{project}'."
        )


class QuotaExceededError(Exception):
    pass

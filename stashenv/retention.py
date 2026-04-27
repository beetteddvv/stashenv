"""Retention policy: auto-delete snapshots/profiles older than N days."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir

_RETENTION_FILE = "retention.json"


def _retention_path(project: str) -> Path:
    return _stash_dir(project) / _RETENTION_FILE


def _load(project: str) -> dict:
    p = _retention_path(project)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(project: str, data: dict) -> None:
    p = _retention_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_retention(project: str, profile: str, days: int) -> None:
    """Set a retention policy of *days* days for *profile*."""
    if days <= 0:
        raise ValueError("Retention days must be a positive integer.")
    data = _load(project)
    data[profile] = {"days": days, "set_at": datetime.now(timezone.utc).isoformat()}
    _save(project, data)


def get_retention(project: str, profile: str) -> Optional[dict]:
    """Return the retention policy dict for *profile*, or None."""
    return _load(project).get(profile)


def clear_retention(project: str, profile: str) -> bool:
    """Remove the retention policy for *profile*. Returns True if one existed."""
    data = _load(project)
    if profile not in data:
        return False
    del data[profile]
    _save(project, data)
    return True


def list_retention(project: str) -> dict[str, dict]:
    """Return all retention policies for the project."""
    return dict(_load(project))


def is_expired(project: str, profile: str, reference: Optional[datetime] = None) -> bool:
    """Return True if *profile* has a retention policy and it has expired."""
    policy = get_retention(project, profile)
    if policy is None:
        return False
    set_at = datetime.fromisoformat(policy["set_at"])
    cutoff = set_at + timedelta(days=policy["days"])
    now = reference or datetime.now(timezone.utc)
    return now >= cutoff

"""Profile priority ranking — assign and query numeric priority levels."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir


def _priority_path(project: str) -> Path:
    return _stash_dir(project) / "priorities.json"


def _load(project: str) -> dict[str, int]:
    p = _priority_path(project)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(project: str, data: dict[str, int]) -> None:
    p = _priority_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_priority(project: str, profile: str, level: int) -> None:
    """Assign a numeric priority level to a profile (higher = more important)."""
    if level < 0:
        raise ValueError(f"Priority level must be non-negative, got {level}")
    data = _load(project)
    data[profile] = level
    _save(project, data)


def get_priority(project: str, profile: str) -> Optional[int]:
    """Return the priority level for a profile, or None if not set."""
    return _load(project).get(profile)


def remove_priority(project: str, profile: str) -> bool:
    """Remove priority for a profile. Returns True if it existed."""
    data = _load(project)
    if profile not in data:
        return False
    del data[profile]
    _save(project, data)
    return True


def list_priorities(project: str) -> list[tuple[str, int]]:
    """Return all profiles with priorities, sorted highest first."""
    data = _load(project)
    return sorted(data.items(), key=lambda x: x[1], reverse=True)


def top_profile(project: str) -> Optional[str]:
    """Return the profile with the highest priority, or None if none set."""
    ranked = list_priorities(project)
    return ranked[0][0] if ranked else None

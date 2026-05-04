"""Badge system — assign short status badges to profiles (e.g. 'stable', 'wip', 'deprecated')."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir

ALLOWED_BADGES = {"stable", "wip", "deprecated", "experimental", "review", "archived"}


def _badges_path(project: str) -> Path:
    return _stash_dir(project) / "badges.json"


def _load(project: str) -> dict:
    p = _badges_path(project)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(project: str, data: dict) -> None:
    p = _badges_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_badge(project: str, profile: str, badge: str) -> None:
    """Assign a badge to a profile. Raises ValueError for unknown badges."""
    badge = badge.strip().lower()
    if badge not in ALLOWED_BADGES:
        raise ValueError(f"Unknown badge '{badge}'. Allowed: {sorted(ALLOWED_BADGES)}")
    data = _load(project)
    data[profile] = badge
    _save(project, data)


def get_badge(project: str, profile: str) -> Optional[str]:
    """Return the badge for a profile, or None if not set."""
    return _load(project).get(profile)


def remove_badge(project: str, profile: str) -> bool:
    """Remove the badge from a profile. Returns True if one existed."""
    data = _load(project)
    if profile not in data:
        return False
    del data[profile]
    _save(project, data)
    return True


def list_badges(project: str) -> dict[str, str]:
    """Return a mapping of profile -> badge for all badged profiles."""
    return dict(_load(project))


def profiles_with_badge(project: str, badge: str) -> list[str]:
    """Return all profiles that have the given badge."""
    badge = badge.strip().lower()
    return [p for p, b in _load(project).items() if b == badge]

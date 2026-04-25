"""Profile grouping — assign profiles to named groups and query by group."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from stashenv.store import _stash_dir


def _groups_path(project: str) -> Path:
    return _stash_dir(project) / "groups.json"


def _load(project: str) -> Dict[str, List[str]]:
    path = _groups_path(project)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(project: str, data: Dict[str, List[str]]) -> None:
    path = _groups_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def add_to_group(project: str, group: str, profile: str) -> None:
    """Add *profile* to *group*, creating the group if needed."""
    data = _load(project)
    members = data.setdefault(group, [])
    if profile not in members:
        members.append(profile)
    _save(project, data)


def remove_from_group(project: str, group: str, profile: str) -> bool:
    """Remove *profile* from *group*. Returns True if it was present."""
    data = _load(project)
    members = data.get(group, [])
    if profile not in members:
        return False
    members.remove(profile)
    if not members:
        del data[group]
    _save(project, data)
    return True


def list_groups(project: str) -> List[str]:
    """Return all group names for the project."""
    return list(_load(project).keys())


def get_group_members(project: str, group: str) -> List[str]:
    """Return profiles belonging to *group* (empty list if group missing)."""
    return list(_load(project).get(group, []))


def get_profile_groups(project: str, profile: str) -> List[str]:
    """Return all groups that *profile* belongs to."""
    return [g for g, members in _load(project).items() if profile in members]


def delete_group(project: str, group: str) -> bool:
    """Delete an entire group. Returns True if it existed."""
    data = _load(project)
    if group not in data:
        return False
    del data[group]
    _save(project, data)
    return True

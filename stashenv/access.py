"""Per-profile access control: restrict which profiles can be loaded in which contexts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir


def _access_path(project: str) -> Path:
    return _stash_dir(project) / "access.json"


def _load(project: str) -> dict:
    p = _access_path(project)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(project: str, data: dict) -> None:
    p = _access_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_allowed_contexts(project: str, profile: str, contexts: list[str]) -> None:
    """Set the list of allowed contexts (e.g. 'ci', 'local', 'prod') for a profile."""
    data = _load(project)
    data[profile] = sorted(set(contexts))
    _save(project, data)


def get_allowed_contexts(project: str, profile: str) -> Optional[list[str]]:
    """Return allowed contexts for a profile, or None if unrestricted."""
    data = _load(project)
    return data.get(profile)


def remove_access_rule(project: str, profile: str) -> bool:
    """Remove access restrictions for a profile. Returns True if a rule existed."""
    data = _load(project)
    if profile not in data:
        return False
    del data[profile]
    _save(project, data)
    return True


def is_allowed(project: str, profile: str, context: str) -> bool:
    """Return True if the profile is accessible in the given context."""
    allowed = get_allowed_contexts(project, profile)
    if allowed is None:
        return True  # no restriction
    return context in allowed


def list_rules(project: str) -> dict[str, list[str]]:
    """Return all access rules for the project."""
    return dict(_load(project))

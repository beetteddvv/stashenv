"""Profile aliasing — map short names to full profile names."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir


def _aliases_path(project: str) -> Path:
    return _stash_dir(project) / "aliases.json"


def _load(project: str) -> dict[str, str]:
    p = _aliases_path(project)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(project: str, data: dict[str, str]) -> None:
    p = _aliases_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_alias(project: str, alias: str, profile: str) -> None:
    """Map *alias* to *profile* for the given project."""
    data = _load(project)
    data[alias] = profile
    _save(project, data)


def remove_alias(project: str, alias: str) -> bool:
    """Remove an alias. Returns True if it existed, False otherwise."""
    data = _load(project)
    if alias not in data:
        return False
    del data[alias]
    _save(project, data)
    return True


def resolve_alias(project: str, alias: str) -> Optional[str]:
    """Return the profile name for *alias*, or None if not set."""
    return _load(project).get(alias)


def list_aliases(project: str) -> dict[str, str]:
    """Return all alias -> profile mappings for the project."""
    return _load(project)


def clear_aliases(project: str) -> int:
    """Remove all aliases. Returns the number of aliases cleared."""
    data = _load(project)
    count = len(data)
    _save(project, {})
    return count

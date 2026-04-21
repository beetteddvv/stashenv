"""Tag profiles with arbitrary labels for easier organization and filtering."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from stashenv.store import _stash_dir


def _tags_path(project: str) -> Path:
    return _stash_dir(project) / "tags.json"


def _load_tags(project: str) -> Dict[str, List[str]]:
    path = _tags_path(project)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_tags(project: str, data: Dict[str, List[str]]) -> None:
    path = _tags_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def add_tag(project: str, profile: str, tag: str) -> None:
    """Add a tag to a profile. No-op if the tag already exists."""
    data = _load_tags(project)
    tags = data.setdefault(profile, [])
    if tag not in tags:
        tags.append(tag)
    _save_tags(project, data)


def remove_tag(project: str, profile: str, tag: str) -> None:
    """Remove a tag from a profile. No-op if the tag is not present."""
    data = _load_tags(project)
    if profile in data:
        data[profile] = [t for t in data[profile] if t != tag]
        if not data[profile]:
            del data[profile]
    _save_tags(project, data)


def get_tags(project: str, profile: str) -> List[str]:
    """Return the list of tags for a given profile."""
    return _load_tags(project).get(profile, [])


def profiles_with_tag(project: str, tag: str) -> List[str]:
    """Return all profiles that have the given tag."""
    data = _load_tags(project)
    return [profile for profile, tags in data.items() if tag in tags]


def clear_tags(project: str, profile: str) -> None:
    """Remove all tags from a profile."""
    data = _load_tags(project)
    if profile in data:
        del data[profile]
    _save_tags(project, data)

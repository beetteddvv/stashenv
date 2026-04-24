"""Mark profiles as favorites and retrieve them quickly."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from stashenv.store import _stash_dir


def _favorites_path(project: str) -> Path:
    return _stash_dir(project) / "favorites.json"


def _load(project: str) -> List[str]:
    path = _favorites_path(project)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save(project: str, favorites: List[str]) -> None:
    path = _favorites_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(favorites, indent=2))


def add_favorite(project: str, profile: str) -> None:
    """Mark a profile as a favorite. Idempotent."""
    favorites = _load(project)
    if profile not in favorites:
        favorites.append(profile)
        _save(project, favorites)


def remove_favorite(project: str, profile: str) -> bool:
    """Remove a profile from favorites. Returns True if it existed."""
    favorites = _load(project)
    if profile in favorites:
        favorites.remove(profile)
        _save(project, favorites)
        return True
    return False


def list_favorites(project: str) -> List[str]:
    """Return all favorited profiles for a project."""
    return _load(project)


def is_favorite(project: str, profile: str) -> bool:
    """Return True if the profile is marked as a favorite."""
    return profile in _load(project)


def clear_favorites(project: str) -> None:
    """Remove all favorites for a project."""
    _save(project, [])

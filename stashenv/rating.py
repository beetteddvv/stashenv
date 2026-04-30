"""Profile rating system — let users rate profiles 1-5 stars."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from stashenv.store import _stash_dir


def _ratings_path(project: str) -> Path:
    return _stash_dir(project) / "ratings.json"


def _load(project: str) -> dict:
    path = _ratings_path(project)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(project: str, data: dict) -> None:
    path = _ratings_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_rating(project: str, profile: str, stars: int) -> None:
    """Rate a profile 1–5 stars. Raises ValueError for out-of-range values."""
    if not (1 <= stars <= 5):
        raise ValueError(f"Rating must be between 1 and 5, got {stars}")
    data = _load(project)
    data[profile] = {
        "stars": stars,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _save(project, data)


def get_rating(project: str, profile: str) -> Optional[dict]:
    """Return the rating entry for a profile, or None if unrated."""
    return _load(project).get(profile)


def remove_rating(project: str, profile: str) -> bool:
    """Remove a profile's rating. Returns True if it existed."""
    data = _load(project)
    if profile not in data:
        return False
    del data[profile]
    _save(project, data)
    return True


def list_ratings(project: str) -> dict[str, int]:
    """Return a mapping of profile -> stars for all rated profiles."""
    data = _load(project)
    return {profile: entry["stars"] for profile, entry in data.items()}


def top_rated(project: str, n: int = 5) -> list[tuple[str, int]]:
    """Return the top-n rated profiles as (profile, stars) sorted descending."""
    rated = list_ratings(project)
    return sorted(rated.items(), key=lambda x: x[1], reverse=True)[:n]

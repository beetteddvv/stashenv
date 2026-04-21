"""Pin a specific profile as the default for a project."""

from __future__ import annotations

import json
from pathlib import Path

from stashenv.store import _stash_dir


def _pin_path(project: str) -> Path:
    return _stash_dir(project) / ".pinned"


def pin_profile(project: str, profile: str) -> None:
    """Set *profile* as the pinned default for *project*."""
    path = _pin_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"profile": profile}), encoding="utf-8")


def unpin_profile(project: str) -> None:
    """Remove the pinned profile for *project* (no-op if none set)."""
    path = _pin_path(project)
    if path.exists():
        path.unlink()


def get_pinned(project: str) -> str | None:
    """Return the currently pinned profile name, or *None* if not set."""
    path = _pin_path(project)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("profile")


def is_pinned(project: str, profile: str) -> bool:
    """Return True if *profile* is the pinned default for *project*."""
    return get_pinned(project) == profile

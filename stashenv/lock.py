"""Profile locking — prevent accidental overwrites of pinned profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from stashenv.store import _stash_dir


def _lock_path(project: str) -> Path:
    return _stash_dir(project) / ".locked"


def lock_profile(project: str, profile: str) -> None:
    """Mark *profile* as locked so save/delete commands refuse to touch it."""
    path = _lock_path(project)
    locked = _read_locked(path)
    if profile not in locked:
        locked.append(profile)
        _write_locked(path, locked)


def unlock_profile(project: str, profile: str) -> None:
    """Remove the lock on *profile*."""
    path = _lock_path(project)
    locked = _read_locked(path)
    if profile in locked:
        locked.remove(profile)
        _write_locked(path, locked)


def is_locked(project: str, profile: str) -> bool:
    """Return True if *profile* is currently locked."""
    return profile in _read_locked(_lock_path(project))


def list_locked(project: str) -> List[str]:
    """Return all locked profile names for *project*."""
    return list(_read_locked(_lock_path(project)))


def assert_not_locked(project: str, profile: str) -> None:
    """Raise RuntimeError if *profile* is locked."""
    if is_locked(project, profile):
        raise RuntimeError(
            f"Profile '{profile}' is locked. Unlock it first with `stashenv lock unlock`."
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_locked(path: Path) -> List[str]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write_locked(path: Path, locked: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(locked)))

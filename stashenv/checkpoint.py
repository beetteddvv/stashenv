"""Checkpoint support: save and restore named restore-points for a profile."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir, load_profile, save_profile


def _checkpoint_dir(project: str, profile: str) -> Path:
    d = _stash_dir(project) / "checkpoints" / profile
    d.mkdir(parents=True, exist_ok=True)
    return d


def _checkpoint_path(project: str, profile: str, name: str) -> Path:
    return _checkpoint_dir(project, profile) / f"{name}.json"


def create_checkpoint(
    project: str,
    profile: str,
    password: str,
    name: Optional[str] = None,
) -> str:
    """Snapshot current profile state into a checkpoint. Returns checkpoint name."""
    env = load_profile(project, profile, password)
    if name is None:
        name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    data = {
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "env": env,
    }
    _checkpoint_path(project, profile, name).write_text(json.dumps(data, indent=2))
    return name


def restore_checkpoint(
    project: str,
    profile: str,
    name: str,
    password: str,
) -> dict[str, str]:
    """Restore profile from a checkpoint. Returns the restored env dict."""
    path = _checkpoint_path(project, profile, name)
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint '{name}' not found for profile '{profile}'.")
    data = json.loads(path.read_text())
    env: dict[str, str] = data["env"]
    save_profile(project, profile, env, password)
    return env


def list_checkpoints(project: str, profile: str) -> list[str]:
    """Return checkpoint names sorted oldest-first."""
    d = _checkpoint_dir(project, profile)
    return sorted(p.stem for p in d.glob("*.json"))


def delete_checkpoint(project: str, profile: str, name: str) -> bool:
    """Delete a checkpoint. Returns True if it existed."""
    path = _checkpoint_path(project, profile, name)
    if path.exists():
        path.unlink()
        return True
    return False


def get_checkpoint(project: str, profile: str, name: str) -> dict:
    """Return raw checkpoint metadata + env dict."""
    path = _checkpoint_path(project, profile, name)
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint '{name}' not found for profile '{profile}'.")
    return json.loads(path.read_text())

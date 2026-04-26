"""Attach human-readable labels (display names) to profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir


def _labels_path(project: str) -> Path:
    return _stash_dir(project) / "labels.json"


def _load(project: str) -> dict:
    p = _labels_path(project)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(project: str, data: dict) -> None:
    p = _labels_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_label(project: str, profile: str, label: str) -> None:
    """Attach a display label to *profile*."""
    data = _load(project)
    data[profile] = label.strip()
    _save(project, data)


def get_label(project: str, profile: str) -> Optional[str]:
    """Return the label for *profile*, or None if not set."""
    return _load(project).get(profile)


def remove_label(project: str, profile: str) -> bool:
    """Remove the label for *profile*. Returns True if a label existed."""
    data = _load(project)
    if profile not in data:
        return False
    del data[profile]
    _save(project, data)
    return True


def list_labels(project: str) -> dict[str, str]:
    """Return all profile -> label mappings for *project*."""
    return dict(_load(project))


def resolve_display_name(project: str, profile: str) -> str:
    """Return label if set, otherwise fall back to the profile name."""
    return get_label(project, profile) or profile

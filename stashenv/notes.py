"""Per-profile notes/annotations storage."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from stashenv.store import _stash_dir


def _notes_path(project: str) -> Path:
    return _stash_dir(project) / "notes.json"


def _load(project: str) -> dict:
    p = _notes_path(project)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(project: str, data: dict) -> None:
    p = _notes_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_note(project: str, profile: str, text: str) -> None:
    """Set or overwrite a note for a profile."""
    data = _load(project)
    data[profile] = {
        "text": text,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _save(project, data)


def get_note(project: str, profile: str) -> str | None:
    """Return the note text for a profile, or None if not set."""
    data = _load(project)
    entry = data.get(profile)
    return entry["text"] if entry else None


def get_note_entry(project: str, profile: str) -> dict | None:
    """Return the full note entry (text + updated_at) or None."""
    return _load(project).get(profile)


def delete_note(project: str, profile: str) -> bool:
    """Delete a note. Returns True if it existed."""
    data = _load(project)
    if profile not in data:
        return False
    del data[profile]
    _save(project, data)
    return True


def list_notes(project: str) -> dict[str, str]:
    """Return {profile: text} for all profiles that have notes."""
    return {k: v["text"] for k, v in _load(project).items()}

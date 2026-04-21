"""Track profile load history per project."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from stashenv.store import _stash_dir


def _history_path(project: str) -> Path:
    return _stash_dir(project) / "history.json"


def record_load(project: str, profile: str) -> None:
    """Append a load event for the given profile."""
    path = _history_path(project)
    entries = _read_raw(path)
    entries.append({
        "profile": profile,
        "loaded_at": datetime.now(timezone.utc).isoformat(),
    })
    path.write_text(json.dumps(entries, indent=2))


def get_history(project: str, limit: Optional[int] = None) -> List[dict]:
    """Return load history, most recent first."""
    entries = _read_raw(_history_path(project))
    entries = list(reversed(entries))
    if limit is not None:
        entries = entries[:limit]
    return entries


def last_loaded(project: str) -> Optional[str]:
    """Return the name of the most recently loaded profile, or None."""
    entries = get_history(project, limit=1)
    return entries[0]["profile"] if entries else None


def clear_history(project: str) -> None:
    """Wipe the load history for a project."""
    path = _history_path(project)
    if path.exists():
        path.unlink()


def format_history(entries: List[dict]) -> str:
    lines = []
    for e in entries:
        ts = e.get("loaded_at", "unknown")
        profile = e.get("profile", "?")
        lines.append(f"  {ts}  {profile}")
    return "\n".join(lines) if lines else "  (no history)"


def _read_raw(path: Path) -> List[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return []

"""Profile expiry — set a TTL on a profile so it auto-warns when stale."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir


def _expiry_path(project: str) -> Path:
    return _stash_dir(project) / ".expiry.json"


def _load(project: str) -> dict:
    p = _expiry_path(project)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(project: str, data: dict) -> None:
    p = _expiry_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_expiry(project: str, profile: str, days: int) -> datetime:
    """Set an expiry *days* from now for *profile*. Returns the expiry datetime."""
    if days <= 0:
        raise ValueError("days must be a positive integer")
    expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    data = _load(project)
    data[profile] = expires_at.isoformat()
    _save(project, data)
    return expires_at


def get_expiry(project: str, profile: str) -> Optional[datetime]:
    """Return the expiry datetime for *profile*, or None if not set."""
    data = _load(project)
    raw = data.get(profile)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def clear_expiry(project: str, profile: str) -> bool:
    """Remove expiry for *profile*. Returns True if an entry existed."""
    data = _load(project)
    if profile not in data:
        return False
    del data[profile]
    _save(project, data)
    return True


def is_expired(project: str, profile: str) -> bool:
    """Return True if the profile has passed its expiry date."""
    exp = get_expiry(project, profile)
    if exp is None:
        return False
    return datetime.now(timezone.utc) > exp


def list_expiries(project: str) -> dict[str, datetime]:
    """Return all profile expiries as {profile: datetime}."""
    data = _load(project)
    return {k: datetime.fromisoformat(v) for k, v in data.items()}

"""Webhook notification support for stashenv events."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


def _webhook_path(project: str) -> Path:
    from stashenv.store import _stash_dir
    return _stash_dir(project) / "webhooks.json"


def _load(project: str) -> dict:
    p = _webhook_path(project)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(project: str, data: dict) -> None:
    p = _webhook_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_webhook(project: str, event: str, url: str) -> None:
    """Register a webhook URL for a given event type."""
    data = _load(project)
    data[event] = {"url": url, "registered_at": datetime.now(timezone.utc).isoformat()}
    _save(project, data)


def get_webhook(project: str, event: str) -> Optional[dict]:
    """Return webhook config for event, or None if not set."""
    return _load(project).get(event)


def remove_webhook(project: str, event: str) -> bool:
    """Remove webhook for event. Returns True if it existed."""
    data = _load(project)
    if event not in data:
        return False
    del data[event]
    _save(project, data)
    return True


def list_webhooks(project: str) -> dict[str, dict]:
    """Return all registered webhooks for the project."""
    return _load(project)


def fire_webhook(project: str, event: str, payload: dict) -> bool:
    """Send a POST request to the webhook URL for the event.
    Returns True if successful, False if no webhook or request fails."""
    entry = get_webhook(project, event)
    if not entry:
        return False
    url = entry["url"]
    body = json.dumps({"event": event, "project": project, **payload}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5):
            pass
        return True
    except Exception:
        return False

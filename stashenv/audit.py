"""Simple audit log for stashenv profile operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def _audit_path(project: str) -> Path:
    base = Path.home() / ".stashenv" / project
    base.mkdir(parents=True, exist_ok=True)
    return base / "audit.log"


def record(project: str, action: str, profile: str, detail: str = "") -> None:
    """Append a single audit entry as a JSON line."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "profile": profile,
        "detail": detail,
        "user": os.environ.get("USER", "unknown"),
    }
    with _audit_path(project).open("a") as fh:
        fh.write(json.dumps(entry) + "\n")


def read_log(project: str) -> list[dict]:
    """Return all audit entries for a project (oldest first)."""
    path = _audit_path(project)
    if not path.exists():
        return []
    entries = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def clear_log(project: str) -> None:
    """Wipe the audit log for a project."""
    path = _audit_path(project)
    if path.exists():
        path.unlink()


def format_log(entries: list[dict]) -> str:
    """Human-readable table of audit entries."""
    if not entries:
        return "(no audit entries)"
    lines = []
    for e in entries:
        detail = f" ({e['detail']})" if e.get("detail") else ""
        lines.append(f"{e['ts']}  {e['user']:12s}  {e['action']:10s}  {e['profile']}{detail}")
    return "\n".join(lines)

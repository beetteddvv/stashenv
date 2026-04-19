"""Snapshot: capture and restore .env file state at a point in time."""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Optional
from stashenv.store import _stash_dir, load_profile, save_profile


def _snapshot_dir(project: str) -> Path:
    d = _stash_dir(project) / "snapshots"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _snapshot_path(project: str, name: str) -> Path:
    return _snapshot_dir(project) / f"{name}.snap.json"


def create_snapshot(project: str, profile: str, password: str, label: Optional[str] = None) -> str:
    """Save an encrypted snapshot of profile. Returns snapshot name."""
    data = load_profile(project, profile, password)
    ts = int(time.time())
    snap_name = label if label else f"{profile}_{ts}"
    meta = {"profile": profile, "timestamp": ts, "label": snap_name}
    payload = json.dumps({"meta": meta, "env": data})
    save_profile(project, f"__snap__{snap_name}", payload, password)
    return snap_name


def restore_snapshot(project: str, snap_name: str, target_profile: str, password: str) -> None:
    """Restore a snapshot into target_profile."""
    raw = load_profile(project, f"__snap__{snap_name}", password)
    parsed = json.loads(raw)
    save_profile(project, target_profile, parsed["env"], password)


def list_snapshots(project: str) -> list[dict]:
    """List snapshot metadata stored as special profiles."""
    snap_dir = _stash_dir(project)
    results = []
    for p in snap_dir.glob("__snap__*.enc"):
        name = p.stem.replace("__snap__", "")
        results.append({"snap_name": name})
    return results


def delete_snapshot(project: str, snap_name: str) -> None:
    path = _stash_dir(project) / f"__snap__{snap_name}.enc"
    if not path.exists():
        raise FileNotFoundError(f"Snapshot '{snap_name}' not found.")
    path.unlink()

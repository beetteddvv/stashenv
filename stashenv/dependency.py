"""Track dependencies between profiles (e.g. profile B extends profile A)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from stashenv.store import _stash_dir


def _deps_path(project: str) -> Path:
    return _stash_dir(project) / "dependencies.json"


def _load(project: str) -> Dict[str, List[str]]:
    p = _deps_path(project)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(project: str, data: Dict[str, List[str]]) -> None:
    p = _deps_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def add_dependency(project: str, profile: str, depends_on: str) -> None:
    """Record that *profile* depends on *depends_on*."""
    if profile == depends_on:
        raise ValueError("A profile cannot depend on itself.")
    data = _load(project)
    deps = data.setdefault(profile, [])
    if depends_on not in deps:
        deps.append(depends_on)
    _save(project, data)


def remove_dependency(project: str, profile: str, depends_on: str) -> bool:
    """Remove a dependency. Returns True if it existed."""
    data = _load(project)
    deps = data.get(profile, [])
    if depends_on in deps:
        deps.remove(depends_on)
        if not deps:
            data.pop(profile, None)
        _save(project, data)
        return True
    return False


def get_dependencies(project: str, profile: str) -> List[str]:
    """Return direct dependencies of *profile*."""
    return list(_load(project).get(profile, []))


def get_dependents(project: str, profile: str) -> List[str]:
    """Return profiles that directly depend on *profile*."""
    data = _load(project)
    return [p for p, deps in data.items() if profile in deps]


def clear_dependencies(project: str, profile: str) -> None:
    """Remove all dependencies for *profile*."""
    data = _load(project)
    data.pop(profile, None)
    _save(project, data)


def resolve_order(project: str, profile: str) -> List[str]:
    """Return a topologically sorted load order ending with *profile*.

    Raises ValueError on circular dependencies.
    """
    data = _load(project)
    visited: List[str] = []
    visiting: set = set()

    def visit(p: str) -> None:
        if p in visiting:
            raise ValueError(f"Circular dependency detected involving '{p}'.")
        if p in visited:
            return
        visiting.add(p)
        for dep in data.get(p, []):
            visit(dep)
        visiting.discard(p)
        visited.append(p)

    visit(profile)
    return visited

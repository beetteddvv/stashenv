"""Pipeline support for chaining profile operations.

Allows defining a sequence of stashenv operations (load, validate,
template-check, switch) that run in order for a given project/profile.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from stashenv.store import _stash_dir


def _pipeline_path(project: str) -> Path:
    d = _stash_dir(project) / "pipelines"
    d.mkdir(parents=True, exist_ok=True)
    return d


@dataclass
class PipelineStep:
    """A single step in a pipeline."""

    action: str  # e.g. "validate", "template_check", "switch", "snapshot"
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"action": self.action, "params": self.params}

    @classmethod
    def from_dict(cls, data: dict) -> "PipelineStep":
        return cls(action=data["action"], params=data.get("params", {}))


@dataclass
class Pipeline:
    """An ordered list of steps to execute against a profile."""

    name: str
    steps: list[PipelineStep] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"name": self.name, "steps": [s.to_dict() for s in self.steps]}

    @classmethod
    def from_dict(cls, data: dict) -> "Pipeline":
        steps = [PipelineStep.from_dict(s) for s in data.get("steps", [])]
        return cls(name=data["name"], steps=steps)


def save_pipeline(project: str, pipeline: Pipeline) -> None:
    """Persist a pipeline definition to disk."""
    path = _pipeline_path(project) / f"{pipeline.name}.json"
    path.write_text(json.dumps(pipeline.to_dict(), indent=2))


def load_pipeline(project: str, name: str) -> Pipeline:
    """Load a named pipeline. Raises FileNotFoundError if missing."""
    path = _pipeline_path(project) / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Pipeline '{name}' not found for project '{project}'")
    return Pipeline.from_dict(json.loads(path.read_text()))


def delete_pipeline(project: str, name: str) -> bool:
    """Delete a pipeline. Returns True if it existed, False otherwise."""
    path = _pipeline_path(project) / f"{name}.json"
    if path.exists():
        path.unlink()
        return True
    return False


def list_pipelines(project: str) -> list[str]:
    """Return sorted list of pipeline names for the project."""
    return sorted(p.stem for p in _pipeline_path(project).glob("*.json"))


def run_pipeline(
    project: str,
    name: str,
    profile: str,
    password: str,
    *,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Execute each step in a pipeline and return a results list.

    Each result dict has keys: ``step``, ``action``, ``ok``, ``detail``.
    On the first failure the remaining steps are skipped (status ``skipped``).
    """
    from stashenv.validate import validate_env
    from stashenv.store import load_profile
    from stashenv.snapshot import create_snapshot
    from stashenv.env_switch import switch_to_profile

    pipeline = load_pipeline(project, name)
    results: list[dict[str, Any]] = []
    failed = False

    for i, step in enumerate(pipeline.steps):
        if failed:
            results.append({"step": i, "action": step.action, "ok": None, "detail": "skipped"})
            continue

        try:
            if step.action == "validate":
                env = load_profile(project, profile, password)
                result = validate_env(env)
                ok = result.valid
                detail = str(result) if not ok else "ok"

            elif step.action == "snapshot":
                if not dry_run:
                    snap_name = create_snapshot(
                        project, profile, password,
                        label=step.params.get("label"),
                    )
                    detail = f"snapshot: {snap_name}"
                else:
                    detail = "dry-run: skipped"
                ok = True

            elif step.action == "switch":
                output_file = step.params.get("output", ".env")
                if not dry_run:
                    switch_to_profile(project, profile, password, output_path=output_file)
                    detail = f"written to {output_file}"
                else:
                    detail = "dry-run: skipped"
                ok = True

            else:
                ok = False
                detail = f"unknown action '{step.action}'"

        except Exception as exc:  # noqa: BLE001
            ok = False
            detail = str(exc)

        if not ok:
            failed = True

        results.append({"step": i, "action": step.action, "ok": ok, "detail": detail})

    return results

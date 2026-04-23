"""Password rotation for stashenv profiles."""

from pathlib import Path
from typing import Optional

from stashenv.store import (
    _stash_dir,
    list_profiles,
    load_profile,
    save_profile,
)
from stashenv.audit import record


class RotationError(Exception):
    pass


def rotate_profile(
    project: str,
    profile: str,
    old_password: str,
    new_password: str,
) -> None:
    """Re-encrypt a single profile with a new password."""
    try:
        env = load_profile(project, profile, old_password)
    except Exception as exc:
        raise RotationError(
            f"Could not decrypt '{profile}' with the old password: {exc}"
        ) from exc

    save_profile(project, profile, env, new_password)
    record(
        project,
        "rotate",
        profile,
        detail="password rotated",
    )


def rotate_all(
    project: str,
    old_password: str,
    new_password: str,
    *,
    stop_on_error: bool = True,
) -> dict[str, Optional[Exception]]:
    """Re-encrypt every profile in *project*.

    Returns a mapping of profile -> exception (None on success).
    """
    results: dict[str, Optional[Exception]] = {}
    for profile in list_profiles(project):
        try:
            rotate_profile(project, profile, old_password, new_password)
            results[profile] = None
        except RotationError as exc:
            results[profile] = exc
            if stop_on_error:
                raise
    return results

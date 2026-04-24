"""Clone a profile to a new project directory, optionally with a new password."""

from pathlib import Path
from stashenv.store import load_profile, save_profile, _stash_dir


class CloneError(Exception):
    pass


def clone_profile(
    src_project: str,
    src_profile: str,
    src_password: str,
    dst_project: str,
    dst_profile: str,
    dst_password: str | None = None,
) -> Path:
    """Clone a profile from one project to another.

    If dst_password is None, the source password is reused.
    Returns the path of the newly written profile file.
    """
    try:
        env = load_profile(src_project, src_profile, src_password)
    except FileNotFoundError:
        raise CloneError(
            f"Source profile '{src_profile}' not found in project '{src_project}'."
        )
    except Exception as exc:
        raise CloneError(f"Failed to read source profile: {exc}") from exc

    effective_password = dst_password if dst_password is not None else src_password

    dst_dir = _stash_dir(dst_project)
    dst_dir.mkdir(parents=True, exist_ok=True)

    dst_path = save_profile(dst_project, dst_profile, env, effective_password)
    return dst_path


def clone_all_profiles(
    src_project: str,
    src_password: str,
    dst_project: str,
    dst_password: str | None = None,
) -> list[str]:
    """Clone every profile from src_project into dst_project.

    Returns the list of cloned profile names.
    """
    src_dir = _stash_dir(src_project)
    if not src_dir.exists():
        raise CloneError(f"Source project '{src_project}' has no stash directory.")

    profiles = [p.stem for p in src_dir.glob("*.enc")]
    if not profiles:
        raise CloneError(f"No profiles found in project '{src_project}'.")

    cloned: list[str] = []
    for name in profiles:
        clone_profile(
            src_project, name, src_password, dst_project, name, dst_password
        )
        cloned.append(name)

    return cloned

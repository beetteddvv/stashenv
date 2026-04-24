"""Switch between profiles by writing vars to a .env file or current env."""

from pathlib import Path
from typing import Optional

from stashenv.store import load_profile, list_profiles
from stashenv.export import parse_dotenv, write_dotenv_file
from stashenv.history import record_load
from stashenv.lock import is_locked
from stashenv.pin import get_pinned


class SwitchError(Exception):
    pass


def switch_to_profile(
    project: str,
    profile: str,
    password: str,
    target_file: Optional[Path] = None,
) -> dict:
    """Load a profile and optionally write it to a .env file.

    Returns the parsed key/value dict.
    Raises SwitchError if the profile is locked or missing.
    """
    available = list_profiles(project)
    if profile not in available:
        raise SwitchError(f"Profile '{profile}' not found for project '{project}'.")

    if is_locked(project, profile):
        raise SwitchError(
            f"Profile '{profile}' is locked and cannot be switched to."
        )

    raw = load_profile(project, profile, password)
    env = parse_dotenv(raw)

    if target_file is not None:
        write_dotenv_file(env, Path(target_file))

    record_load(project, profile)
    return env


def switch_to_pinned(
    project: str,
    password: str,
    target_file: Optional[Path] = None,
) -> tuple[str, dict]:
    """Switch to the pinned profile for the project.

    Returns (profile_name, env_dict).
    Raises SwitchError if no profile is pinned.
    """
    pinned = get_pinned(project)
    if pinned is None:
        raise SwitchError(f"No profile is pinned for project '{project}'.")
    env = switch_to_profile(project, pinned, password, target_file)
    return pinned, env

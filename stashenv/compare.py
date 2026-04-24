"""Compare two named profiles and show their differences."""

from typing import Optional
from stashenv.store import load_profile, list_profiles
from stashenv.diff import diff_envs, format_diff, DiffEntry
from stashenv.export import parse_dotenv


class CompareError(Exception):
    pass


def compare_profiles(
    project: str,
    profile_a: str,
    profile_b: str,
    password: str,
    show_unchanged: bool = False,
    password_b: Optional[str] = None,
) -> list[DiffEntry]:
    """Load two profiles and return their diff entries.

    Both profiles are decrypted with *password* unless *password_b* is given,
    in which case profile_b uses that password instead.
    """
    available = list_profiles(project)
    if profile_a not in available:
        raise CompareError(f"Profile '{profile_a}' not found in project '{project}'.")
    if profile_b not in available:
        raise CompareError(f"Profile '{profile_b}' not found in project '{project}'.")

    raw_a = load_profile(project, profile_a, password)
    raw_b = load_profile(project, profile_b, password_b or password)

    env_a = parse_dotenv(raw_a)
    env_b = parse_dotenv(raw_b)

    return diff_envs(env_a, env_b, show_unchanged=show_unchanged)


def compare_summary(entries: list[DiffEntry]) -> dict:
    """Return a small summary dict for quick inspection."""
    added = sum(1 for e in entries if e.status == "added")
    removed = sum(1 for e in entries if e.status == "removed")
    changed = sum(1 for e in entries if e.status == "changed")
    unchanged = sum(1 for e in entries if e.status == "unchanged")
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
        "total": added + removed + changed + unchanged,
    }

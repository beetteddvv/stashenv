"""Search across profiles for keys or values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from stashenv.store import list_profiles, load_profile
from stashenv.export import parse_dotenv


@dataclass
class SearchMatch:
    profile: str
    key: str
    value: str

    def __str__(self) -> str:
        return f"[{self.profile}] {self.key}={self.value}"


def search_profiles(
    project: str,
    password: str,
    *,
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    exact: bool = False,
) -> list[SearchMatch]:
    """Search all profiles in a project for matching keys or values.

    At least one of key_pattern or value_pattern must be provided.
    If exact=True, matches are case-sensitive full-string comparisons.
    Otherwise, a case-insensitive substring match is used.
    """
    if key_pattern is None and value_pattern is None:
        raise ValueError("Provide at least one of key_pattern or value_pattern.")

    def _matches(text: str, pattern: str) -> bool:
        if exact:
            return text == pattern
        return pattern.lower() in text.lower()

    results: list[SearchMatch] = []

    for profile in list_profiles(project):
        try:
            raw = load_profile(project, profile, password)
        except Exception:
            continue

        env = parse_dotenv(raw)

        for key, value in env.items():
            key_ok = key_pattern is None or _matches(key, key_pattern)
            value_ok = value_pattern is None or _matches(value, value_pattern)
            if key_ok and value_ok:
                results.append(SearchMatch(profile=profile, key=key, value=value))

    return results

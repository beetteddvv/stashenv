"""Helpers to integrate pin awareness into the main load workflow."""

from __future__ import annotations

import click

from stashenv.pin import get_pinned


def resolve_profile(project: str, profile: str | None) -> str:
    """Return *profile* if given, else the pinned default, else raise.

    Raises :class:`click.UsageError` if neither is available.
    """
    if profile:
        return profile

    pinned = get_pinned(project)
    if pinned:
        click.echo(f"Using pinned default profile: '{pinned}'")
        return pinned

    raise click.UsageError(
        f"No profile specified and no pinned default set for project '{project}'. "
        "Run 'stashenv pin set <project> <profile>' to set a default."
    )


def profile_display_name(project: str, profile: str) -> str:
    """Return a display string that marks pinned profiles with a star."""
    pinned = get_pinned(project)
    marker = " *" if profile == pinned else ""
    return f"{profile}{marker}"


def annotate_profiles(project: str, profiles: list[str]) -> list[str]:
    """Return profile names annotated with a '*' next to the pinned one."""
    return [profile_display_name(project, p) for p in profiles]

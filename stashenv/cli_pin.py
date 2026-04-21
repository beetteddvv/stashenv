"""CLI commands for managing pinned (default) profiles."""

from __future__ import annotations

import click

from stashenv.pin import get_pinned, is_pinned, pin_profile, unpin_profile


@click.group("pin")
def pin() -> None:
    """Manage the pinned default profile for a project."""


@pin.command("set")
@click.argument("project")
@click.argument("profile")
def set_cmd(project: str, profile: str) -> None:
    """Pin PROFILE as the default for PROJECT."""
    pin_profile(project, profile)
    click.echo(f"Pinned '{profile}' as default for project '{project}'.")


@pin.command("unset")
@click.argument("project")
def unset_cmd(project: str) -> None:
    """Remove the pinned default for PROJECT."""
    current = get_pinned(project)
    if current is None:
        click.echo(f"No pinned profile for project '{project}'.")
        return
    unpin_profile(project)
    click.echo(f"Unpinned '{current}' from project '{project}'.")


@pin.command("show")
@click.argument("project")
def show_cmd(project: str) -> None:
    """Show the pinned default profile for PROJECT."""
    current = get_pinned(project)
    if current is None:
        click.echo(f"No pinned profile for project '{project}'.")
    else:
        click.echo(f"Pinned profile: {current}")


@pin.command("check")
@click.argument("project")
@click.argument("profile")
def check_cmd(project: str, profile: str) -> None:
    """Exit 0 if PROFILE is pinned for PROJECT, else exit 1."""
    if is_pinned(project, profile):
        click.echo(f"'{profile}' is the pinned default.")
    else:
        current = get_pinned(project)
        msg = f"'{profile}' is NOT pinned."
        if current:
            msg += f" Current pin: '{current}'."
        click.echo(msg, err=True)
        raise SystemExit(1)


@pin.command("list")
def list_cmd() -> None:
    """List all projects that have a pinned profile."""
    from stashenv.pin import list_pinned

    pins = list_pinned()
    if not pins:
        click.echo("No pinned profiles found.")
        return
    for project, profile in sorted(pins.items()):
        click.echo(f"{project}: {profile}")

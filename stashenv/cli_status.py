"""CLI commands for `stashenv status`."""

import click
from pathlib import Path

from stashenv.env_status import get_status
from stashenv.store import list_profiles


@click.group()
def status():
    """Show status information for a project."""


@status.command("show")
@click.argument("project")
@click.option("--cwd", default=None, help="Directory to check for .env file.")
def show_cmd(project: str, cwd):
    """Print a status summary for PROJECT."""
    path = Path(cwd) if cwd else None
    s = get_status(project, cwd=path)
    click.echo(str(s))


@status.command("profiles")
@click.argument("project")
def profiles_cmd(project: str):
    """List all profiles for PROJECT with lock/expiry indicators."""
    from stashenv.lock import is_locked
    from stashenv.expire import is_expired
    from stashenv.pin import get_pinned

    profiles = list_profiles(project)
    pinned = get_pinned(project)

    if not profiles:
        click.echo("No profiles found.")
        return

    for p in profiles:
        tags = []
        if p == pinned:
            tags.append("pinned")
        if is_locked(project, p):
            tags.append("locked")
        if is_expired(project, p):
            tags.append("expired")
        suffix = f"  [{', '.join(tags)}]" if tags else ""
        click.echo(f"  {p}{suffix}")


@status.command("quick")
@click.argument("project")
def quick_cmd(project: str):
    """One-line status: pinned profile and profile count."""
    from stashenv.pin import get_pinned

    profiles = list_profiles(project)
    pinned = get_pinned(project)
    pinned_str = pinned or "(none)"
    click.echo(f"{project}: {len(profiles)} profile(s), pinned={pinned_str}")

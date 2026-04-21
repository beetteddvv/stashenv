"""CLI commands for profile locking — prevent accidental overwrites."""

import click
from stashenv.lock import (
    lock_profile,
    unlock_profile,
    is_locked,
    list_locked,
    LockError,
)


@click.group("lock")
def lock():
    """Lock or unlock profiles to prevent accidental changes."""


@lock.command("on")
@click.argument("project")
@click.argument("profile")
def lock_cmd(project: str, profile: str):
    """Lock a profile so it cannot be overwritten or deleted."""
    try:
        lock_profile(project, profile)
        click.echo(f"🔒 Locked '{profile}' in project '{project}'.")
    except LockError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@lock.command("off")
@click.argument("project")
@click.argument("profile")
def unlock_cmd(project: str, profile: str):
    """Unlock a previously locked profile."""
    try:
        unlock_profile(project, profile)
        click.echo(f"🔓 Unlocked '{profile}' in project '{project}'.")
    except LockError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@lock.command("status")
@click.argument("project")
@click.argument("profile")
def status_cmd(project: str, profile: str):
    """Check whether a profile is currently locked."""
    locked = is_locked(project, profile)
    state = "locked 🔒" if locked else "unlocked 🔓"
    click.echo(f"Profile '{profile}' in project '{project}' is {state}.")


@lock.command("list")
@click.argument("project")
def list_cmd(project: str):
    """List all locked profiles for a project."""
    locked = list_locked(project)
    if not locked:
        click.echo(f"No locked profiles in project '{project}'.")
        return
    click.echo(f"Locked profiles in '{project}':")
    for name in sorted(locked):
        click.echo(f"  🔒 {name}")

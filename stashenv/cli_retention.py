"""CLI commands for managing profile retention policies."""

import click

from stashenv.retention import (
    clear_retention,
    get_retention,
    is_expired,
    list_retention,
    set_retention,
)


@click.group("retention")
def retention() -> None:
    """Manage auto-expiry retention policies for profiles."""


@retention.command("set")
@click.argument("project")
@click.argument("profile")
@click.argument("days", type=int)
def set_cmd(project: str, profile: str, days: int) -> None:
    """Set a retention policy of DAYS days for PROFILE."""
    try:
        set_retention(project, profile, days)
        click.echo(f"Retention policy set: '{profile}' expires after {days} day(s).")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@retention.command("show")
@click.argument("project")
@click.argument("profile")
def show_cmd(project: str, profile: str) -> None:
    """Show the retention policy for PROFILE."""
    policy = get_retention(project, profile)
    if policy is None:
        click.echo(f"No retention policy set for '{profile}'.")
    else:
        expired = is_expired(project, profile)
        status = "EXPIRED" if expired else "active"
        click.echo(
            f"Profile '{profile}': {policy['days']} day(s), set at {policy['set_at']} [{status}]"
        )


@retention.command("clear")
@click.argument("project")
@click.argument("profile")
def clear_cmd(project: str, profile: str) -> None:
    """Remove the retention policy for PROFILE."""
    removed = clear_retention(project, profile)
    if removed:
        click.echo(f"Retention policy cleared for '{profile}'.")
    else:
        click.echo(f"No retention policy found for '{profile}'.")


@retention.command("list")
@click.argument("project")
def list_cmd(project: str) -> None:
    """List all retention policies for PROJECT."""
    policies = list_retention(project)
    if not policies:
        click.echo("No retention policies set.")
        return
    for profile, policy in policies.items():
        expired = is_expired(project, profile)
        status = "EXPIRED" if expired else "active"
        click.echo(f"  {profile}: {policy['days']}d [{status}]")

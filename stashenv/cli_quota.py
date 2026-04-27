"""CLI commands for managing per-project profile quotas."""

import click

from stashenv.quota import (
    QuotaExceededError,
    check_quota,
    clear_quota,
    get_quota,
    set_quota,
)


@click.group()
def quota():
    """Manage profile quotas for a project."""


@quota.command("set")
@click.argument("project")
@click.argument("limit", type=int)
def set_cmd(project: str, limit: int):
    """Set the maximum number of profiles for PROJECT."""
    try:
        set_quota(project, limit)
        click.echo(f"Quota for '{project}' set to {limit} profiles.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@quota.command("show")
@click.argument("project")
def show_cmd(project: str):
    """Show the quota limit for PROJECT."""
    limit = get_quota(project)
    if limit is None:
        click.echo(f"No explicit quota set for '{project}' (default: 20).")
    else:
        click.echo(f"Quota for '{project}': {limit} profiles.")


@quota.command("clear")
@click.argument("project")
def clear_cmd(project: str):
    """Remove the quota limit for PROJECT, reverting to the default."""
    removed = clear_quota(project)
    if removed:
        click.echo(f"Quota for '{project}' cleared.")
    else:
        click.echo(f"No quota was set for '{project}'.")


@quota.command("check")
@click.argument("project")
def check_cmd(project: str):
    """Report current usage vs quota for PROJECT."""
    current, limit, ok = check_quota(project)
    status = "OK" if ok else "EXCEEDED"
    click.echo(f"[{status}] {current}/{limit} profiles used for '{project}'.")
    if not ok:
        raise SystemExit(1)

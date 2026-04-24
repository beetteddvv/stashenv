"""CLI commands for switching between env profiles."""

import click
from pathlib import Path

from stashenv.env_switch import switch_to_profile, switch_to_pinned, SwitchError
from stashenv.pin import get_pinned


@click.group()
def switch():
    """Switch the active .env profile."""


@switch.command("to")
@click.argument("project")
@click.argument("profile")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password")
@click.option(
    "--output",
    "-o",
    default=".env",
    show_default=True,
    help="Target .env file to write",
)
def to_cmd(project: str, profile: str, password: str, output: str):
    """Switch to a named profile, writing vars to OUTPUT file."""
    try:
        env = switch_to_profile(project, profile, password, Path(output))
        click.echo(
            f"Switched to profile '{profile}' ({len(env)} keys) -> {output}"
        )
    except SwitchError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@switch.command("pinned")
@click.argument("project")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password")
@click.option(
    "--output",
    "-o",
    default=".env",
    show_default=True,
    help="Target .env file to write",
)
def pinned_cmd(project: str, password: str, output: str):
    """Switch to the pinned profile for PROJECT."""
    pinned = get_pinned(project)
    if pinned is None:
        click.echo(f"No profile is pinned for project '{project}'.", err=True)
        raise SystemExit(1)
    try:
        profile, env = switch_to_pinned(project, password, Path(output))
        click.echo(
            f"Switched to pinned profile '{profile}' ({len(env)} keys) -> {output}"
        )
    except SwitchError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

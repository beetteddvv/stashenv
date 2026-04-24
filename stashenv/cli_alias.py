"""CLI commands for managing profile aliases."""

import click

from stashenv.alias import (
    set_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    clear_aliases,
)


@click.group("alias")
def alias() -> None:
    """Manage short-name aliases for profiles."""


@alias.command("set")
@click.argument("alias_name")
@click.argument("profile")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def set_cmd(alias_name: str, profile: str, project: str) -> None:
    """Create or update an alias pointing to a profile."""
    set_alias(project, alias_name, profile)
    click.echo(f"Alias '{alias_name}' -> '{profile}' saved.")


@alias.command("remove")
@click.argument("alias_name")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def remove_cmd(alias_name: str, project: str) -> None:
    """Remove an alias."""
    removed = remove_alias(project, alias_name)
    if removed:
        click.echo(f"Alias '{alias_name}' removed.")
    else:
        click.echo(f"No alias named '{alias_name}' found.", err=True)


@alias.command("show")
@click.argument("alias_name")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def show_cmd(alias_name: str, project: str) -> None:
    """Show which profile an alias points to."""
    target = resolve_alias(project, alias_name)
    if target is None:
        click.echo(f"No alias named '{alias_name}'.", err=True)
    else:
        click.echo(target)


@alias.command("list")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def list_cmd(project: str) -> None:
    """List all aliases for the project."""
    mapping = list_aliases(project)
    if not mapping:
        click.echo("No aliases defined.")
        return
    for alias_name, profile in sorted(mapping.items()):
        click.echo(f"{alias_name:20s} -> {profile}")


@alias.command("clear")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.confirmation_option(prompt="Remove all aliases for this project?")
def clear_cmd(project: str) -> None:
    """Remove all aliases for the project."""
    n = clear_aliases(project)
    click.echo(f"Cleared {n} alias(es).")

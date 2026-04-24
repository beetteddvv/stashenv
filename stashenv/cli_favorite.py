"""CLI commands for managing favorite profiles."""

import click

from stashenv.favorite import (
    add_favorite,
    remove_favorite,
    list_favorites,
    is_favorite,
    clear_favorites,
)


@click.group()
def favorite() -> None:
    """Manage favorite profiles."""


@favorite.command("add")
@click.argument("project")
@click.argument("profile")
def add_cmd(project: str, profile: str) -> None:
    """Mark PROFILE as a favorite in PROJECT."""
    add_favorite(project, profile)
    click.echo(f"Added '{profile}' to favorites for '{project}'.")


@favorite.command("remove")
@click.argument("project")
@click.argument("profile")
def remove_cmd(project: str, profile: str) -> None:
    """Remove PROFILE from favorites in PROJECT."""
    removed = remove_favorite(project, profile)
    if removed:
        click.echo(f"Removed '{profile}' from favorites for '{project}'.")
    else:
        click.echo(f"'{profile}' was not in favorites for '{project}'.")


@favorite.command("list")
@click.argument("project")
def list_cmd(project: str) -> None:
    """List all favorite profiles for PROJECT."""
    favs = list_favorites(project)
    if not favs:
        click.echo(f"No favorites set for '{project}'.")
    else:
        for name in favs:
            click.echo(name)


@favorite.command("check")
@click.argument("project")
@click.argument("profile")
def check_cmd(project: str, profile: str) -> None:
    """Check whether PROFILE is a favorite in PROJECT."""
    if is_favorite(project, profile):
        click.echo(f"'{profile}' is a favorite.")
    else:
        click.echo(f"'{profile}' is NOT a favorite.")


@favorite.command("clear")
@click.argument("project")
@click.confirmation_option(prompt="Clear all favorites?")
def clear_cmd(project: str) -> None:
    """Remove all favorites for PROJECT."""
    clear_favorites(project)
    click.echo(f"All favorites cleared for '{project}'.")

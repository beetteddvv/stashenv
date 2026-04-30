"""CLI commands for profile ratings."""

import click
from stashenv.rating import set_rating, get_rating, remove_rating, list_ratings, top_rated


@click.group("rating")
def rating():
    """Rate and browse profiles by star rating."""


@rating.command("set")
@click.argument("project")
@click.argument("profile")
@click.argument("stars", type=int)
def set_cmd(project: str, profile: str, stars: int):
    """Set a star rating (1-5) for a profile."""
    try:
        set_rating(project, profile, stars)
        click.echo(f"Rated '{profile}' {stars} star(s).")
    except ValueError as e:
        raise click.ClickException(str(e))


@rating.command("show")
@click.argument("project")
@click.argument("profile")
def show_cmd(project: str, profile: str):
    """Show the rating for a profile."""
    entry = get_rating(project, profile)
    if entry is None:
        click.echo(f"'{profile}' has not been rated.")
    else:
        click.echo(f"{profile}: {'★' * entry['stars']}{'☆' * (5 - entry['stars'])} ({entry['stars']}/5)")
        click.echo(f"  updated: {entry['updated_at']}")


@rating.command("remove")
@click.argument("project")
@click.argument("profile")
def remove_cmd(project: str, profile: str):
    """Remove the rating for a profile."""
    removed = remove_rating(project, profile)
    if removed:
        click.echo(f"Rating removed for '{profile}'.")
    else:
        click.echo(f"No rating found for '{profile}'.")


@rating.command("list")
@click.argument("project")
def list_cmd(project: str):
    """List all rated profiles."""
    ratings = list_ratings(project)
    if not ratings:
        click.echo("No profiles have been rated.")
        return
    for profile, stars in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
        click.echo(f"  {profile}: {'★' * stars}{'☆' * (5 - stars)}")


@rating.command("top")
@click.argument("project")
@click.option("--n", default=5, show_default=True, help="Number of results.")
def top_cmd(project: str, n: int):
    """Show top-rated profiles."""
    results = top_rated(project, n)
    if not results:
        click.echo("No rated profiles found.")
        return
    for i, (profile, stars) in enumerate(results, 1):
        click.echo(f"  {i}. {profile} — {'★' * stars}{'☆' * (5 - stars)}")

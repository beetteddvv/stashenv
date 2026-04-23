"""CLI commands for searching across profiles."""

import click

from stashenv.search import search_profiles


@click.group()
def search() -> None:
    """Search across env profiles."""


@search.command("keys")
@click.argument("project")
@click.argument("pattern")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--exact", is_flag=True, default=False, help="Exact match instead of substring.")
def keys_cmd(project: str, pattern: str, password: str, exact: bool) -> None:
    """Find profiles containing a key matching PATTERN."""
    matches = search_profiles(project, password, key_pattern=pattern, exact=exact)
    if not matches:
        click.echo("No matches found.")
        return
    for m in matches:
        click.echo(str(m))


@search.command("values")
@click.argument("project")
@click.argument("pattern")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--exact", is_flag=True, default=False, help="Exact match instead of substring.")
def values_cmd(project: str, pattern: str, password: str, exact: bool) -> None:
    """Find profiles containing a value matching PATTERN."""
    matches = search_profiles(project, password, value_pattern=pattern, exact=exact)
    if not matches:
        click.echo("No matches found.")
        return
    for m in matches:
        click.echo(str(m))


@search.command("all")
@click.argument("project")
@click.option("--key", "key_pattern", default=None, help="Filter by key pattern.")
@click.option("--value", "value_pattern", default=None, help="Filter by value pattern.")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--exact", is_flag=True, default=False)
def all_cmd(
    project: str,
    key_pattern: str,
    value_pattern: str,
    password: str,
    exact: bool,
) -> None:
    """Search profiles by key and/or value pattern."""
    if not key_pattern and not value_pattern:
        raise click.UsageError("Provide at least --key or --value.")
    matches = search_profiles(
        project, password, key_pattern=key_pattern, value_pattern=value_pattern, exact=exact
    )
    if not matches:
        click.echo("No matches found.")
        return
    for m in matches:
        click.echo(str(m))

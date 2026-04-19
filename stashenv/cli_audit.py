"""CLI commands for the audit log feature."""

import click
from stashenv.audit import read_log, clear_log, format_log


@click.group()
def audit():
    """View or manage the audit log for a project."""


@audit.command("show")
@click.argument("project")
@click.option("--last", default=0, help="Show only the last N entries.")
def show_cmd(project: str, last: int):
    """Print audit log entries for PROJECT."""
    entries = read_log(project)
    if last > 0:
        entries = entries[-last:]
    click.echo(format_log(entries))


@audit.command("clear")
@click.argument("project")
@click.confirmation_option(prompt="This will permanently delete the audit log. Continue?")
def clear_cmd(project: str):
    """Delete the audit log for PROJECT."""
    clear_log(project)
    click.echo(f"Audit log cleared for '{project}'.")


@audit.command("count")
@click.argument("project")
def count_cmd(project: str):
    """Print the number of audit entries for PROJECT."""
    n = len(read_log(project))
    click.echo(f"{n} audit entry/entries for '{project}'.")

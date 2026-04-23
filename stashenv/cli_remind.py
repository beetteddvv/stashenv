"""CLI commands for managing profile reminders."""

import click
from stashenv.remind import set_reminder, get_reminder, clear_reminder, list_reminders


@click.group("remind")
def remind():
    """Attach reminder notes to profiles."""


@remind.command("set")
@click.argument("project")
@click.argument("profile")
@click.argument("message")
def set_cmd(project: str, profile: str, message: str):
    """Set a reminder message for PROFILE in PROJECT."""
    set_reminder(project, profile, message)
    click.echo(f"Reminder set for '{profile}'.")


@remind.command("show")
@click.argument("project")
@click.argument("profile")
def show_cmd(project: str, profile: str):
    """Show the reminder for PROFILE in PROJECT."""
    entry = get_reminder(project, profile)
    if entry is None:
        click.echo(f"No reminder set for '{profile}'.")
    else:
        click.echo(f"[{entry['created_at']}] {entry['message']}")


@remind.command("clear")
@click.argument("project")
@click.argument("profile")
def clear_cmd(project: str, profile: str):
    """Remove the reminder for PROFILE in PROJECT."""
    removed = clear_reminder(project, profile)
    if removed:
        click.echo(f"Reminder for '{profile}' cleared.")
    else:
        click.echo(f"No reminder found for '{profile}'.")


@remind.command("list")
@click.argument("project")
def list_cmd(project: str):
    """List all reminders for PROJECT."""
    reminders = list_reminders(project)
    if not reminders:
        click.echo("No reminders set.")
        return
    for profile, entry in reminders.items():
        click.echo(f"  {profile}: {entry['message']}  (set {entry['created_at']})")

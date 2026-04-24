"""CLI commands for managing per-profile notes."""

import click

from stashenv.notes import set_note, get_note_entry, delete_note, list_notes


@click.group()
def notes():
    """Attach notes/annotations to profiles."""


@notes.command("set")
@click.argument("project")
@click.argument("profile")
@click.argument("text")
def set_cmd(project: str, profile: str, text: str):
    """Set a note for a profile."""
    set_note(project, profile, text)
    click.echo(f"Note saved for '{profile}'.")


@notes.command("show")
@click.argument("project")
@click.argument("profile")
def show_cmd(project: str, profile: str):
    """Show the note for a profile."""
    entry = get_note_entry(project, profile)
    if entry is None:
        click.echo(f"No note set for '{profile}'.")
        return
    click.echo(f"{entry['text']}")
    click.echo(f"  (updated {entry['updated_at']})")


@notes.command("delete")
@click.argument("project")
@click.argument("profile")
def delete_cmd(project: str, profile: str):
    """Delete the note for a profile."""
    removed = delete_note(project, profile)
    if removed:
        click.echo(f"Note for '{profile}' deleted.")
    else:
        click.echo(f"No note found for '{profile}'.")


@notes.command("list")
@click.argument("project")
def list_cmd(project: str):
    """List all profiles that have notes."""
    all_notes = list_notes(project)
    if not all_notes:
        click.echo("No notes stored.")
        return
    for profile, text in all_notes.items():
        snippet = text[:60] + "..." if len(text) > 60 else text
        click.echo(f"  {profile}: {snippet}")

"""CLI commands for snapshot management."""
import click
from stashenv.snapshot import create_snapshot, restore_snapshot, list_snapshots, delete_snapshot


@click.group("snapshot")
def snapshot():
    """Manage profile snapshots."""


@snapshot.command("create")
@click.argument("project")
@click.argument("profile")
@click.option("--label", default=None, help="Optional snapshot label.")
@click.password_option(prompt="Password")
def create_cmd(project, profile, label, password):
    """Create a snapshot of a profile."""
    try:
        name = create_snapshot(project, profile, password, label=label)
        click.echo(f"Snapshot '{name}' created.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot.command("restore")
@click.argument("project")
@click.argument("snap_name")
@click.argument("target_profile")
@click.password_option(prompt="Password")
def restore_cmd(project, snap_name, target_profile, password):
    """Restore a snapshot into a profile."""
    try:
        restore_snapshot(project, snap_name, target_profile, password)
        click.echo(f"Restored snapshot '{snap_name}' into '{target_profile}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot.command("list")
@click.argument("project")
def list_cmd(project):
    """List all snapshots for a project."""
    snaps = list_snapshots(project)
    if not snaps:
        click.echo("No snapshots found.")
    for s in snaps:
        click.echo(s["snap_name"])


@snapshot.command("delete")
@click.argument("project")
@click.argument("snap_name")
def delete_cmd(project, snap_name):
    """Delete a snapshot."""
    try:
        delete_snapshot(project, snap_name)
        click.echo(f"Snapshot '{snap_name}' deleted.")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

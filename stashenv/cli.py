"""CLI entry point for stashenv."""

import sys
from pathlib import Path
import click
from stashenv.store import save_profile, load_profile, list_profiles, delete_profile


PROJECT_DIR = Path.cwd()


@click.group()
def cli():
    """stashenv — securely store and switch .env profiles."""


@cli.command("save")
@click.argument("name")
@click.option("--file", "env_file", default=".env", show_default=True, help="Path to .env file to stash.")
@click.password_option(prompt="Encryption password")
def save(name, env_file, password):
    """Save current .env as a named profile."""
    path = Path(env_file)
    if not path.exists():
        click.echo(f"Error: '{env_file}' not found.", err=True)
        sys.exit(1)
    save_profile(PROJECT_DIR, name, path.read_text(), password)
    click.echo(f"Profile '{name}' saved.")


@cli.command("load")
@click.argument("name")
@click.option("--out", default=".env", show_default=True, help="Output .env file path.")
@click.option("--password", prompt=True, hide_input=True)
def load(name, out, password):
    """Load a named profile into .env."""
    try:
        content = load_profile(PROJECT_DIR, name, password)
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    except Exception:
        click.echo("Error: decryption failed — wrong password?", err=True)
        sys.exit(1)
    Path(out).write_text(content)
    click.echo(f"Profile '{name}' loaded into '{out}'.")


@cli.command("list")
def list_cmd():
    """List saved profiles."""
    profiles = list_profiles(PROJECT_DIR)
    if not profiles:
        click.echo("No profiles found.")
    for p in profiles:
        click.echo(f"  {p}")


@cli.command("delete")
@click.argument("name")
def delete(name):
    """Delete a named profile."""
    try:
        delete_profile(PROJECT_DIR, name)
        click.echo(f"Profile '{name}' deleted.")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()

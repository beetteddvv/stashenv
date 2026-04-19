import click
from stashenv.store import save_profile, load_profile, list_profiles, delete_profile
from stashenv.cli_audit import audit
from stashenv.cli_template import template
from stashenv.cli_snapshot import snapshot


@click.group()
def cli():
    """stashenv — securely manage .env profiles."""


@cli.command()
@click.argument("project")
@click.argument("profile")
@click.argument("envfile", type=click.Path(exists=True))
@click.password_option()
def save(project, profile, envfile, password):
    """Save an .env file as a named profile."""
    with open(envfile) as f:
        data = f.read()
    save_profile(project, profile, data, password)
    click.echo(f"Profile '{profile}' saved for project '{project}'.")


@cli.command()
@click.argument("project")
@click.argument("profile")
@click.option("--out", default=".env", show_default=True)
@click.password_option(confirmation_prompt=False)
def load(project, profile, out, password):
    """Load a profile into an .env file."""
    data = load_profile(project, profile, password)
    with open(out, "w") as f:
        f.write(data)
    click.echo(f"Profile '{profile}' written to '{out}'.")


@cli.command(name="list")
@click.argument("project")
def list_cmd(project):
    """List profiles for a project."""
    profiles = list_profiles(project)
    if not profiles:
        click.echo("No profiles found.")
    for p in profiles:
        click.echo(p)


@cli.command()
@click.argument("project")
@click.argument("profile")
def delete(project, profile):
    """Delete a profile."""
    try:
        delete_profile(project, profile)
        click.echo(f"Profile '{profile}' deleted.")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


cli.add_command(audit)
cli.add_command(template)
cli.add_command(snapshot)

"""CLI commands for importing/exporting stashenv profile bundles."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv.import_export import export_profile, export_all, import_bundle


@click.group()
def transfer():
    """Import and export profile bundles."""


@transfer.command("export")
@click.argument("project")
@click.argument("profile")
@click.argument("dest", type=click.Path())
@click.password_option("--password", "-p", prompt="Stash password", confirmation_prompt=False)
@click.option("--bundle-password", "-b", default=None, help="Separate password for the bundle (defaults to stash password).")
def export_cmd(project, profile, dest, password, bundle_password):
    """Export a single PROFILE from PROJECT to a bundle file."""
    out = export_profile(project, profile, password, Path(dest), bundle_password)
    click.echo(f"Exported '{profile}' → {out}")


@transfer.command("export-all")
@click.argument("project")
@click.argument("dest", type=click.Path())
@click.password_option("--password", "-p", prompt="Stash password", confirmation_prompt=False)
@click.option("--bundle-password", "-b", default=None, help="Separate password for the bundle.")
def export_all_cmd(project, dest, password, bundle_password):
    """Export ALL profiles from PROJECT into one bundle file."""
    out = export_all(project, password, Path(dest), bundle_password)
    click.echo(f"All profiles from '{project}' exported → {out}")


@transfer.command("import")
@click.argument("src", type=click.Path(exists=True))
@click.password_option("--password", "-p", prompt="Stash password", confirmation_prompt=False)
@click.option("--bundle-password", "-b", default=None, help="Password used when bundle was created.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing profiles.")
def import_cmd(src, password, bundle_password, overwrite):
    """Import profiles from a bundle file into the local stash."""
    try:
        names = import_bundle(Path(src), password, bundle_password, overwrite=overwrite)
        for name in names:
            click.echo(f"  ✓ imported '{name}'")
        click.echo(f"Done — {len(names)} profile(s) imported.")
    except FileExistsError as exc:
        raise click.ClickException(str(exc))
    except Exception as exc:
        raise click.ClickException(f"Import failed: {exc}")

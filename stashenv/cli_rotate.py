"""CLI commands for password rotation."""

import click

from stashenv.rotate import RotationError, rotate_all, rotate_profile


@click.group("rotate")
def rotate() -> None:
    """Rotate encryption passwords for profiles."""


@rotate.command("profile")
@click.argument("project")
@click.argument("profile")
@click.option(
    "--old-password",
    prompt=True,
    hide_input=True,
    help="Current password.",
)
@click.option(
    "--new-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="New password.",
)
def profile_cmd(
    project: str, profile: str, old_password: str, new_password: str
) -> None:
    """Rotate the password for a single PROFILE in PROJECT."""
    try:
        rotate_profile(project, profile, old_password, new_password)
        click.echo(f"✓ Rotated password for '{profile}'.")
    except RotationError as exc:
        raise click.ClickException(str(exc)) from exc


@rotate.command("all")
@click.argument("project")
@click.option("--old-password", prompt=True, hide_input=True)
@click.option(
    "--new-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
)
@click.option(
    "--keep-going",
    is_flag=True,
    default=False,
    help="Continue even if some profiles fail.",
)
def all_cmd(project: str, old_password: str, new_password: str, keep_going: bool) -> None:
    """Rotate the password for ALL profiles in PROJECT."""
    try:
        results = rotate_all(
            project, old_password, new_password, stop_on_error=not keep_going
        )
    except RotationError as exc:
        raise click.ClickException(str(exc)) from exc

    ok = [p for p, e in results.items() if e is None]
    failed = {p: e for p, e in results.items() if e is not None}

    for p in ok:
        click.echo(f"  ✓ {p}")
    for p, exc in failed.items():
        click.echo(f"  ✗ {p}: {exc}", err=True)

    if failed:
        raise click.ClickException(f"{len(failed)} profile(s) failed to rotate.")
    click.echo(f"\nRotated {len(ok)} profile(s) successfully.")

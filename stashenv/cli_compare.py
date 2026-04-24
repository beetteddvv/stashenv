"""CLI commands for comparing two profiles."""

import click
from stashenv.compare import compare_profiles, compare_summary, CompareError
from stashenv.diff import format_diff


@click.group()
def compare():
    """Compare two env profiles."""


@compare.command("diff")
@click.argument("project")
@click.argument("profile_a")
@click.argument("profile_b")
@click.password_option("--password", "-p", prompt="Password", help="Decryption password.")
@click.option("--password-b", default=None, help="Separate password for profile B.")
@click.option("--show-unchanged", is_flag=True, default=False, help="Include unchanged keys.")
def diff_cmd(project, profile_a, profile_b, password, password_b, show_unchanged):
    """Show line-by-line diff between PROFILE_A and PROFILE_B."""
    try:
        entries = compare_profiles(
            project,
            profile_a,
            profile_b,
            password,
            show_unchanged=show_unchanged,
            password_b=password_b,
        )
    except CompareError as exc:
        raise click.ClickException(str(exc))

    if not entries:
        click.echo("No differences found.")
        return

    click.echo(format_diff(entries))


@compare.command("summary")
@click.argument("project")
@click.argument("profile_a")
@click.argument("profile_b")
@click.password_option("--password", "-p", prompt="Password", help="Decryption password.")
@click.option("--password-b", default=None, help="Separate password for profile B.")
def summary_cmd(project, profile_a, profile_b, password, password_b):
    """Print a short summary of differences between two profiles."""
    try:
        entries = compare_profiles(
            project,
            profile_a,
            profile_b,
            password,
            show_unchanged=True,
            password_b=password_b,
        )
    except CompareError as exc:
        raise click.ClickException(str(exc))

    s = compare_summary(entries)
    click.echo(
        f"added={s['added']}  removed={s['removed']}  "
        f"changed={s['changed']}  unchanged={s['unchanged']}  total={s['total']}"
    )

"""CLI commands for template checking."""

import click
from pathlib import Path

from stashenv.store import load_profile, _stash_dir
from stashenv.export import parse_dotenv
from stashenv.template import parse_template, check_profile_against_template


@click.group("template")
def template():
    """Check profiles against a .env.template."""


@template.command("check")
@click.argument("profile")
@click.option("--project", default=None, help="Project name (default: cwd name)")
@click.option(
    "--template",
    "template_path",
    default=".env.template",
    show_default=True,
    help="Path to template file",
)
@click.option("--password", prompt=True, hide_input=True)
def check_cmd(profile: str, project: str, template_path: str, password: str):
    """Check PROFILE against a template file for missing/extra keys."""
    proj = project or Path.cwd().name
    tpl = Path(template_path)
    if not tpl.exists():
        raise click.ClickException(f"Template file not found: {tpl}")

    try:
        raw = load_profile(proj, profile, password)
    except Exception as e:
        raise click.ClickException(str(e))

    env = parse_dotenv(raw)
    keys = parse_template(tpl)
    result = check_profile_against_template(env, keys)

    click.echo(str(result))
    if not result.ok:
        raise SystemExit(1)


@template.command("list-required")
@click.option(
    "--template",
    "template_path",
    default=".env.template",
    show_default=True,
)
def list_required_cmd(template_path: str):
    """List all keys required by the template."""
    tpl = Path(template_path)
    if not tpl.exists():
        raise click.ClickException(f"Template file not found: {tpl}")
    keys = parse_template(tpl)
    if not keys:
        click.echo("No keys found in template.")
    for k in keys:
        click.echo(k)

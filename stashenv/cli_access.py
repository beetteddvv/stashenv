"""CLI commands for managing profile access control."""

import click

from stashenv.access import (
    set_allowed_contexts,
    get_allowed_contexts,
    remove_access_rule,
    is_allowed,
    list_rules,
)


@click.group()
def access() -> None:
    """Manage per-profile access control rules."""


@access.command("allow")
@click.argument("project")
@click.argument("profile")
@click.argument("contexts", nargs=-1, required=True)
def allow_cmd(project: str, profile: str, contexts: tuple[str, ...]) -> None:
    """Set allowed contexts for PROFILE in PROJECT."""
    set_allowed_contexts(project, profile, list(contexts))
    ctx_list = ", ".join(sorted(contexts))
    click.echo(f"Access for '{profile}' restricted to: {ctx_list}")


@access.command("show")
@click.argument("project")
@click.argument("profile")
def show_cmd(project: str, profile: str) -> None:
    """Show allowed contexts for PROFILE in PROJECT."""
    allowed = get_allowed_contexts(project, profile)
    if allowed is None:
        click.echo(f"'{profile}' is unrestricted (no access rule set).")
    else:
        click.echo(f"Allowed contexts for '{profile}': {', '.join(allowed)}")


@access.command("remove")
@click.argument("project")
@click.argument("profile")
def remove_cmd(project: str, profile: str) -> None:
    """Remove access restrictions from PROFILE in PROJECT."""
    removed = remove_access_rule(project, profile)
    if removed:
        click.echo(f"Access rule for '{profile}' removed.")
    else:
        click.echo(f"No access rule found for '{profile}'.")


@access.command("check")
@click.argument("project")
@click.argument("profile")
@click.argument("context")
def check_cmd(project: str, profile: str, context: str) -> None:
    """Check whether PROFILE is accessible in CONTEXT."""
    if is_allowed(project, profile, context):
        click.echo(f"✓ '{profile}' is allowed in context '{context}'.")
    else:
        click.echo(f"✗ '{profile}' is NOT allowed in context '{context}'.")
        raise SystemExit(1)


@access.command("list")
@click.argument("project")
def list_cmd(project: str) -> None:
    """List all access rules for PROJECT."""
    rules = list_rules(project)
    if not rules:
        click.echo("No access rules defined.")
        return
    for profile, contexts in sorted(rules.items()):
        click.echo(f"  {profile}: {', '.join(contexts)}")

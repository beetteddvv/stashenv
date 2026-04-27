"""CLI commands for managing webhooks."""

import click
from stashenv.webhook import set_webhook, get_webhook, remove_webhook, list_webhooks, fire_webhook


@click.group()
def webhook():
    """Manage webhook notifications for profile events."""


@webhook.command("set")
@click.argument("project")
@click.argument("event")
@click.argument("url")
def set_cmd(project: str, event: str, url: str):
    """Register a webhook URL for EVENT in PROJECT."""
    set_webhook(project, event, url)
    click.echo(f"Webhook set for event '{event}' -> {url}")


@webhook.command("show")
@click.argument("project")
@click.argument("event")
def show_cmd(project: str, event: str):
    """Show the webhook URL registered for EVENT."""
    entry = get_webhook(project, event)
    if entry is None:
        click.echo(f"No webhook registered for event '{event}'.")
    else:
        click.echo(f"URL: {entry['url']}")
        click.echo(f"Registered at: {entry['registered_at']}")


@webhook.command("remove")
@click.argument("project")
@click.argument("event")
def remove_cmd(project: str, event: str):
    """Remove the webhook for EVENT."""
    removed = remove_webhook(project, event)
    if removed:
        click.echo(f"Webhook for '{event}' removed.")
    else:
        click.echo(f"No webhook found for '{event}'.")


@webhook.command("list")
@click.argument("project")
def list_cmd(project: str):
    """List all registered webhooks for PROJECT."""
    hooks = list_webhooks(project)
    if not hooks:
        click.echo("No webhooks registered.")
        return
    for event, entry in hooks.items():
        click.echo(f"  {event}: {entry['url']}")


@webhook.command("fire")
@click.argument("project")
@click.argument("event")
@click.option("--data", default="{}", help="JSON payload string")
def fire_cmd(project: str, event: str, data: str):
    """Manually fire the webhook for EVENT."""
    import json
    try:
        payload = json.loads(data)
    except json.JSONDecodeError:
        click.echo("Invalid JSON payload.", err=True)
        raise SystemExit(1)
    ok = fire_webhook(project, event, payload)
    if ok:
        click.echo(f"Webhook for '{event}' fired successfully.")
    else:
        click.echo(f"Failed to fire webhook for '{event}' (not set or request error).")

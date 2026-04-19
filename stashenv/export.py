"""Utilities for exporting and importing .env profiles as plain text."""

from __future__ import annotations

import os
from pathlib import Path


def parse_dotenv(text: str) -> dict[str, str]:
    """Parse a .env file text into a key/value dict."""
    env: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip optional surrounding quotes
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        if key:
            env[key] = value
    return env


def render_dotenv(env: dict[str, str]) -> str:
    """Render a key/value dict as .env file text."""
    lines = []
    for key, value in env.items():
        # Quote values that contain spaces or special characters
        if any(c in value for c in (" ", "#", "'", '"')):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def read_dotenv_file(path: str | Path) -> dict[str, str]:
    """Read and parse a .env file from disk."""
    text = Path(path).read_text(encoding="utf-8")
    return parse_dotenv(text)


def write_dotenv_file(path: str | Path, env: dict[str, str]) -> None:
    """Write a key/value dict to a .env file on disk."""
    Path(path).write_text(render_dotenv(env), encoding="utf-8")


def apply_to_current_env(env: dict[str, str]) -> None:
    """Set the given key/value pairs in the current process environment."""
    for key, value in env.items():
        os.environ[key] = value

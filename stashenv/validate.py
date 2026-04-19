"""Validation helpers for .env profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        for e in self.errors:
            lines.append(f"  ERROR   {e}")
        for w in self.warnings:
            lines.append(f"  WARNING {w}")
        return "\n".join(lines) if lines else "  OK"


_INVALID_KEY_CHARS = set(" \t-")


def _valid_key(key: str) -> bool:
    if not key:
        return False
    if key[0].isdigit():
        return False
    return not any(c in _INVALID_KEY_CHARS for c in key)


def validate_env(env: dict[str, str]) -> ValidationResult:
    """Validate a parsed env dict and return a ValidationResult."""
    errors: list[str] = []
    warnings: list[str] = []

    for key, value in env.items():
        if not _valid_key(key):
            errors.append(f"Invalid key name: {key!r}")
        if not value:
            warnings.append(f"Empty value for key: {key!r}")
        if "\n" in value:
            errors.append(f"Newline in value for key: {key!r}")

    if not env:
        warnings.append("Profile is empty")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def validate_file(path: str) -> ValidationResult:
    """Read a .env file from disk and validate it."""
    from stashenv.export import read_dotenv_file
    env = read_dotenv_file(path)
    return validate_env(env)

"""Profile storage: save, load, list, and delete encrypted .env profiles."""

import os
from pathlib import Path
from stashenv.crypto import encrypt, decrypt

STASH_DIR_NAME = ".stashenv"


def _stash_dir(project_dir: Path) -> Path:
    d = project_dir / STASH_DIR_NAME
    d.mkdir(exist_ok=True)
    return d


def _profile_path(project_dir: Path, name: str) -> Path:
    return _stash_dir(project_dir) / f"{name}.enc"


def save_profile(project_dir: Path, name: str, env_content: str, password: str) -> None:
    """Encrypt and save an env profile by name."""
    payload = encrypt(env_content, password)
    path = _profile_path(project_dir, name)
    path.write_bytes(payload)


def load_profile(project_dir: Path, name: str, password: str) -> str:
    """Load and decrypt an env profile by name."""
    path = _profile_path(project_dir, name)
    if not path.exists():
        raise FileNotFoundError(f"Profile '{name}' not found.")
    return decrypt(path.read_bytes(), password)


def list_profiles(project_dir: Path) -> list[str]:
    """Return a list of stored profile names."""
    stash = _stash_dir(project_dir)
    return [p.stem for p in sorted(stash.glob("*.enc"))]


def delete_profile(project_dir: Path, name: str) -> None:
    """Delete a stored profile."""
    path = _profile_path(project_dir, name)
    if not path.exists():
        raise FileNotFoundError(f"Profile '{name}' not found.")
    path.unlink()

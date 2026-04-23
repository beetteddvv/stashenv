"""Import and export profiles to/from portable encrypted bundles."""

from __future__ import annotations

import json
import base64
from pathlib import Path
from typing import Optional

from stashenv.store import save_profile, load_profile, list_profiles
from stashenv.crypto import encrypt, decrypt


BUNDLE_VERSION = 1


def export_profile(
    project: str,
    profile: str,
    password: str,
    dest: Path,
    bundle_password: Optional[str] = None,
) -> Path:
    """Export a single profile to a .stashbundle file at *dest*.

    The bundle is a JSON envelope holding the re-encrypted ciphertext so it
    can be shared independently of the local stash directory.
    """
    bundle_password = bundle_password or password
    plaintext = load_profile(project, profile, password)
    ciphertext = encrypt(plaintext.encode(), bundle_password)
    bundle = {
        "version": BUNDLE_VERSION,
        "project": project,
        "profile": profile,
        "data": base64.b64encode(ciphertext).decode(),
    }
    dest = Path(dest)
    dest.write_text(json.dumps(bundle, indent=2))
    return dest


def export_all(
    project: str,
    password: str,
    dest: Path,
    bundle_password: Optional[str] = None,
) -> Path:
    """Export every profile in *project* into a single multi-profile bundle."""
    bundle_password = bundle_password or password
    profiles_data = {}
    for name in list_profiles(project):
        plaintext = load_profile(project, name, password)
        ciphertext = encrypt(plaintext.encode(), bundle_password)
        profiles_data[name] = base64.b64encode(ciphertext).decode()

    bundle = {
        "version": BUNDLE_VERSION,
        "project": project,
        "profiles": profiles_data,
    }
    dest = Path(dest)
    dest.write_text(json.dumps(bundle, indent=2))
    return dest


def import_bundle(
    src: Path,
    password: str,
    bundle_password: Optional[str] = None,
    overwrite: bool = False,
) -> list[str]:
    """Import profiles from a bundle file.  Returns list of imported names."""
    bundle_password = bundle_password or password
    bundle = json.loads(Path(src).read_text())
    if bundle.get("version") != BUNDLE_VERSION:
        raise ValueError(f"Unsupported bundle version: {bundle.get('version')}")

    project = bundle["project"]
    imported: list[str] = []

    if "profiles" in bundle:
        items = bundle["profiles"].items()
    else:
        items = [(bundle["profile"], bundle["data"])]

    existing = set(list_profiles(project))
    for name, encoded in items:
        if name in existing and not overwrite:
            raise FileExistsError(
                f"Profile '{name}' already exists. Use overwrite=True to replace."
            )
        ciphertext = base64.b64decode(encoded)
        plaintext = decrypt(ciphertext, bundle_password).decode()
        save_profile(project, name, plaintext, password)
        imported.append(name)

    return imported

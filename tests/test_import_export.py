"""Tests for stashenv.import_export."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stashenv.import_export import export_profile, export_all, import_bundle
from stashenv.store import save_profile, load_profile, list_profiles


PROJECT = "ie_test_project"
PASSWORD = "hunter2"
BUNDLE_PW = "b0ndl3pw"


@pytest.fixture(autouse=True)
def _clean(tmp_path, monkeypatch):
    """Redirect stash dir to a temp location for each test."""
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path / "stash"))
    yield


def _seed(profile: str, content: str = "KEY=value\nOTHER=123\n"):
    save_profile(PROJECT, profile, content, PASSWORD)


# ---------------------------------------------------------------------------
# export_profile
# ---------------------------------------------------------------------------

def test_export_creates_file(tmp_path):
    _seed("prod")
    out = export_profile(PROJECT, "prod", PASSWORD, tmp_path / "prod.stashbundle")
    assert out.exists()


def test_export_bundle_is_valid_json(tmp_path):
    _seed("prod")
    out = export_profile(PROJECT, "prod", PASSWORD, tmp_path / "prod.stashbundle")
    data = json.loads(out.read_text())
    assert data["project"] == PROJECT
    assert data["profile"] == "prod"
    assert "data" in data


def test_export_with_separate_bundle_password(tmp_path):
    _seed("prod")
    out = export_profile(PROJECT, "prod", PASSWORD, tmp_path / "prod.stashbundle", bundle_password=BUNDLE_PW)
    names = import_bundle(out, PASSWORD, bundle_password=BUNDLE_PW)
    assert "prod" in names


# ---------------------------------------------------------------------------
# export_all / import_bundle (multi-profile)
# ---------------------------------------------------------------------------

def test_export_all_contains_all_profiles(tmp_path):
    _seed("dev")
    _seed("staging")
    out = export_all(PROJECT, PASSWORD, tmp_path / "all.stashbundle")
    data = json.loads(out.read_text())
    assert set(data["profiles"].keys()) == {"dev", "staging"}


def test_import_restores_profiles(tmp_path):
    _seed("dev", "A=1\n")
    _seed("staging", "A=2\n")
    bundle = export_all(PROJECT, PASSWORD, tmp_path / "all.stashbundle")

    # wipe originals by importing into a fresh stash dir
    import stashenv.store as store_mod
    import stashenv.import_export as ie_mod
    orig_dir = store_mod._stash_dir

    fresh = tmp_path / "fresh_stash"
    store_mod._stash_dir = lambda p: fresh / p  # type: ignore[assignment]
    ie_mod.save_profile = store_mod.save_profile  # rebind
    ie_mod.list_profiles = store_mod.list_profiles

    try:
        names = import_bundle(bundle, PASSWORD)
        assert set(names) == {"dev", "staging"}
    finally:
        store_mod._stash_dir = orig_dir


def test_import_raises_on_existing_without_overwrite(tmp_path):
    _seed("prod")
    bundle = export_profile(PROJECT, "prod", PASSWORD, tmp_path / "p.stashbundle")
    with pytest.raises(FileExistsError):
        import_bundle(bundle, PASSWORD)


def test_import_overwrite_replaces_profile(tmp_path):
    _seed("prod", "OLD=1\n")
    bundle = export_profile(PROJECT, "prod", PASSWORD, tmp_path / "p.stashbundle")
    # change stored value
    save_profile(PROJECT, "prod", "NEW=99\n", PASSWORD)
    import_bundle(bundle, PASSWORD, overwrite=True)
    result = load_profile(PROJECT, "prod", PASSWORD)
    assert "OLD=1" in result


def test_wrong_bundle_password_raises(tmp_path):
    _seed("prod")
    bundle = export_profile(PROJECT, "prod", PASSWORD, tmp_path / "p.stashbundle", bundle_password=BUNDLE_PW)
    with pytest.raises(Exception):
        import_bundle(bundle, PASSWORD, bundle_password="wrongpw")

"""Tests for profile save/load/list/delete operations."""

import pytest
from pathlib import Path
from stashenv.store import save_profile, load_profile, list_profiles, delete_profile

PASSWORD = "s3cr3t!"
SAMPLE_ENV = "API_KEY=abc123\nDEBUG=true\n"


@pytest.fixture()
def project(tmp_path):
    return tmp_path


def test_save_and_load(project):
    save_profile(project, "dev", SAMPLE_ENV, PASSWORD)
    result = load_profile(project, "dev", PASSWORD)
    assert result == SAMPLE_ENV


def test_wrong_password_raises(project):
    save_profile(project, "dev", SAMPLE_ENV, PASSWORD)
    with pytest.raises(Exception):
        load_profile(project, "dev", "wrongpassword")


def test_list_profiles(project):
    assert list_profiles(project) == []
    save_profile(project, "dev", SAMPLE_ENV, PASSWORD)
    save_profile(project, "prod", SAMPLE_ENV, PASSWORD)
    assert sorted(list_profiles(project)) == ["dev", "prod"]


def test_delete_profile(project):
    save_profile(project, "staging", SAMPLE_ENV, PASSWORD)
    delete_profile(project, "staging")
    assert "staging" not in list_profiles(project)


def test_load_missing_raises(project):
    with pytest.raises(FileNotFoundError):
        load_profile(project, "ghost", PASSWORD)


def test_delete_missing_raises(project):
    with pytest.raises(FileNotFoundError):
        delete_profile(project, "ghost")


def test_encrypted_file_is_not_plaintext(project):
    save_profile(project, "dev", SAMPLE_ENV, PASSWORD)
    raw = (project / ".stashenv" / "dev.enc").read_bytes()
    assert b"API_KEY" not in raw


def test_overwrite_profile(project):
    """Saving a profile twice with new content should update the stored value."""
    save_profile(project, "dev", SAMPLE_ENV, PASSWORD)
    updated_env = "API_KEY=xyz999\nDEBUG=false\n"
    save_profile(project, "dev", updated_env, PASSWORD)
    result = load_profile(project, "dev", PASSWORD)
    assert result == updated_env

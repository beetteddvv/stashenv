"""Tests for stashenv.clone."""

import pytest
from stashenv.clone import clone_profile, clone_all_profiles, CloneError
from stashenv.store import save_profile, load_profile, list_profiles

SRC = "clone_src_project"
DST = "clone_dst_project"
PASS = "hunter2"
NEW_PASS = "newpass99"

ENV = {"APP_ENV": "staging", "DB_HOST": "localhost"}


@pytest.fixture(autouse=True)
def cleanup():
    yield
    from stashenv.store import _stash_dir
    import shutil
    for proj in (SRC, DST):
        d = _stash_dir(proj)
        if d.exists():
            shutil.rmtree(d)


def _seed(project=SRC, profile="default", env=None, password=PASS):
    save_profile(project, profile, env or ENV, password)


def test_clone_creates_dst_profile():
    _seed()
    clone_profile(SRC, "default", PASS, DST, "copy")
    profiles = list_profiles(DST)
    assert "copy" in profiles


def test_clone_preserves_data():
    _seed()
    clone_profile(SRC, "default", PASS, DST, "copy")
    result = load_profile(DST, "copy", PASS)
    assert result == ENV


def test_clone_with_new_password():
    _seed()
    clone_profile(SRC, "default", PASS, DST, "copy", dst_password=NEW_PASS)
    result = load_profile(DST, "copy", NEW_PASS)
    assert result == ENV


def test_clone_new_password_old_password_fails():
    _seed()
    clone_profile(SRC, "default", PASS, DST, "copy", dst_password=NEW_PASS)
    with pytest.raises(Exception):
        load_profile(DST, "copy", PASS)


def test_clone_missing_src_raises():
    with pytest.raises(CloneError, match="not found"):
        clone_profile(SRC, "ghost", PASS, DST, "copy")


def test_clone_all_profiles():
    _seed(profile="alpha")
    _seed(profile="beta")
    cloned = clone_all_profiles(SRC, PASS, DST)
    assert set(cloned) == {"alpha", "beta"}
    assert set(list_profiles(DST)) >= {"alpha", "beta"}


def test_clone_all_missing_project_raises():
    with pytest.raises(CloneError, match="no stash directory"):
        clone_all_profiles("nonexistent_xyz", PASS, DST)


def test_clone_all_empty_project_raises():
    from stashenv.store import _stash_dir
    _stash_dir(SRC).mkdir(parents=True, exist_ok=True)
    with pytest.raises(CloneError, match="No profiles found"):
        clone_all_profiles(SRC, PASS, DST)

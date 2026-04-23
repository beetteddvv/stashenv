"""Tests for stashenv.rotate."""

import pytest

from stashenv.rotate import RotationError, rotate_all, rotate_profile
from stashenv.store import load_profile, save_profile


PROJECT = "test_rotate_project"
OLD_PW = "old-secret"
NEW_PW = "new-secret"


@pytest.fixture(autouse=True)
def _clean(tmp_path, monkeypatch):
    """Redirect stash dir to a temp location."""
    import stashenv.store as store
    import stashenv.audit as audit

    monkeypatch.setattr(store, "_stash_dir", lambda p: tmp_path / p)
    monkeypatch.setattr(audit, "_audit_path", lambda p: tmp_path / f"{p}_audit.json")


def _seed(profile: str, env: dict, password: str = OLD_PW) -> None:
    save_profile(PROJECT, profile, env, password)


def test_rotate_profile_allows_new_password():
    _seed("dev", {"KEY": "val"})
    rotate_profile(PROJECT, "dev", OLD_PW, NEW_PW)
    env = load_profile(PROJECT, "dev", NEW_PW)
    assert env == {"KEY": "val"}


def test_rotate_profile_old_password_no_longer_works():
    _seed("dev", {"KEY": "val"})
    rotate_profile(PROJECT, "dev", OLD_PW, NEW_PW)
    with pytest.raises(Exception):
        load_profile(PROJECT, "dev", OLD_PW)


def test_rotate_profile_wrong_old_password_raises():
    _seed("dev", {"KEY": "val"})
    with pytest.raises(RotationError):
        rotate_profile(PROJECT, "dev", "wrong", NEW_PW)


def test_rotate_all_rotates_every_profile():
    _seed("dev", {"A": "1"})
    _seed("prod", {"B": "2"})
    results = rotate_all(PROJECT, OLD_PW, NEW_PW)
    assert all(e is None for e in results.values())
    assert load_profile(PROJECT, "dev", NEW_PW) == {"A": "1"}
    assert load_profile(PROJECT, "prod", NEW_PW) == {"B": "2"}


def test_rotate_all_stop_on_error():
    _seed("dev", {"A": "1"}, password=OLD_PW)
    # seed 'staging' with a *different* password so rotation will fail
    _seed("staging", {"C": "3"}, password="other-pw")
    with pytest.raises(RotationError):
        rotate_all(PROJECT, OLD_PW, NEW_PW, stop_on_error=True)


def test_rotate_all_keep_going_on_error():
    _seed("dev", {"A": "1"}, password=OLD_PW)
    _seed("staging", {"C": "3"}, password="other-pw")
    results = rotate_all(PROJECT, OLD_PW, NEW_PW, stop_on_error=False)
    assert results["dev"] is None
    assert isinstance(results["staging"], RotationError)

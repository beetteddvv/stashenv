"""Tests for stashenv.lock"""

import pytest

from stashenv.lock import (
    lock_profile,
    unlock_profile,
    is_locked,
    list_locked,
    assert_not_locked,
)
from stashenv.store import save_profile


PROJECT = "test_lock_project"
PASSWORD = "hunter2"


@pytest.fixture(autouse=True)
def clean_up():
    """Remove lock file and any saved profiles after each test."""
    from stashenv.store import _stash_dir

    yield

    stash = _stash_dir(PROJECT)
    lock_file = stash / ".locked"
    if lock_file.exists():
        lock_file.unlink()


def test_lock_makes_profile_locked():
    lock_profile(PROJECT, "prod")
    assert is_locked(PROJECT, "prod")


def test_unlock_removes_lock():
    lock_profile(PROJECT, "prod")
    unlock_profile(PROJECT, "prod")
    assert not is_locked(PROJECT, "prod")


def test_unlocking_nonexistent_lock_is_noop():
    # Should not raise
    unlock_profile(PROJECT, "ghost")
    assert not is_locked(PROJECT, "ghost")


def test_list_locked_returns_all_locked():
    lock_profile(PROJECT, "prod")
    lock_profile(PROJECT, "staging")
    locked = list_locked(PROJECT)
    assert "prod" in locked
    assert "staging" in locked


def test_list_locked_empty_when_none():
    assert list_locked(PROJECT) == []


def test_locking_twice_does_not_duplicate():
    lock_profile(PROJECT, "prod")
    lock_profile(PROJECT, "prod")
    assert list_locked(PROJECT).count("prod") == 1


def test_assert_not_locked_raises_when_locked():
    lock_profile(PROJECT, "prod")
    with pytest.raises(RuntimeError, match="locked"):
        assert_not_locked(PROJECT, "prod")


def test_assert_not_locked_passes_when_unlocked():
    # Should not raise
    assert_not_locked(PROJECT, "dev")


def test_other_profiles_unaffected():
    lock_profile(PROJECT, "prod")
    assert not is_locked(PROJECT, "dev")

"""Tests for stashenv.retention."""

from datetime import datetime, timedelta, timezone

import pytest

from stashenv.retention import (
    clear_retention,
    get_retention,
    is_expired,
    list_retention,
    set_retention,
)

PROJECT = "test_retention_proj"


@pytest.fixture(autouse=True)
def cleanup():
    from stashenv.store import _stash_dir
    import shutil

    yield
    path = _stash_dir(PROJECT)
    if path.exists():
        shutil.rmtree(path)


def test_set_and_get_retention():
    set_retention(PROJECT, "dev", 30)
    policy = get_retention(PROJECT, "dev")
    assert policy is not None
    assert policy["days"] == 30
    assert "set_at" in policy


def test_get_missing_retention_returns_none():
    assert get_retention(PROJECT, "nonexistent") is None


def test_set_zero_days_raises():
    with pytest.raises(ValueError, match="positive"):
        set_retention(PROJECT, "dev", 0)


def test_set_negative_days_raises():
    with pytest.raises(ValueError):
        set_retention(PROJECT, "dev", -5)


def test_set_overwrites_existing():
    set_retention(PROJECT, "dev", 10)
    set_retention(PROJECT, "dev", 60)
    policy = get_retention(PROJECT, "dev")
    assert policy["days"] == 60


def test_clear_retention_returns_true_when_existed():
    set_retention(PROJECT, "staging", 7)
    assert clear_retention(PROJECT, "staging") is True
    assert get_retention(PROJECT, "staging") is None


def test_clear_retention_returns_false_when_missing():
    assert clear_retention(PROJECT, "ghost") is False


def test_list_retention_returns_all():
    set_retention(PROJECT, "dev", 14)
    set_retention(PROJECT, "prod", 90)
    policies = list_retention(PROJECT)
    assert "dev" in policies
    assert "prod" in policies
    assert policies["dev"]["days"] == 14


def test_is_expired_false_for_fresh_policy():
    set_retention(PROJECT, "dev", 30)
    assert is_expired(PROJECT, "dev") is False


def test_is_expired_true_when_past_cutoff():
    set_retention(PROJECT, "dev", 1)
    future = datetime.now(timezone.utc) + timedelta(days=2)
    assert is_expired(PROJECT, "dev", reference=future) is True


def test_is_expired_false_when_no_policy():
    assert is_expired(PROJECT, "no_policy_profile") is False

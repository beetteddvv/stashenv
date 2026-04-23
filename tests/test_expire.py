"""Tests for stashenv.expire."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from stashenv.expire import (
    clear_expiry,
    get_expiry,
    is_expired,
    list_expiries,
    set_expiry,
)


PROJECT = "test_expire_project"


@pytest.fixture(autouse=True)
def cleanup(tmp_path, monkeypatch):
    """Redirect stash dir to a temp location."""
    import stashenv.expire as expire_mod
    import stashenv.store as store_mod

    monkeypatch.setattr(store_mod, "_stash_dir", lambda proj: tmp_path / proj)
    monkeypatch.setattr(expire_mod, "_stash_dir", lambda proj: tmp_path / proj)
    yield


def test_set_expiry_returns_future_datetime():
    exp = set_expiry(PROJECT, "prod", days=7)
    assert isinstance(exp, datetime)
    assert exp > datetime.now(timezone.utc)


def test_get_expiry_matches_set_value():
    set_expiry(PROJECT, "prod", days=3)
    exp = get_expiry(PROJECT, "prod")
    assert exp is not None
    assert exp > datetime.now(timezone.utc)


def test_get_expiry_returns_none_when_not_set():
    assert get_expiry(PROJECT, "nonexistent") is None


def test_clear_expiry_returns_true_when_existed():
    set_expiry(PROJECT, "staging", days=1)
    assert clear_expiry(PROJECT, "staging") is True
    assert get_expiry(PROJECT, "staging") is None


def test_clear_expiry_returns_false_when_not_set():
    assert clear_expiry(PROJECT, "ghost") is False


def test_is_expired_false_for_future():
    set_expiry(PROJECT, "dev", days=30)
    assert is_expired(PROJECT, "dev") is False


def test_is_expired_true_for_past():
    set_expiry(PROJECT, "old", days=1)
    # Patch now() to be in the far future
    future = datetime(2099, 1, 1, tzinfo=timezone.utc)
    with patch("stashenv.expire.datetime") as mock_dt:
        mock_dt.now.return_value = future
        mock_dt.fromisoformat = datetime.fromisoformat
        assert is_expired(PROJECT, "old") is True


def test_is_expired_false_when_no_expiry_set():
    assert is_expired(PROJECT, "noexpiry") is False


def test_list_expiries_returns_all():
    set_expiry(PROJECT, "alpha", days=5)
    set_expiry(PROJECT, "beta", days=10)
    result = list_expiries(PROJECT)
    assert "alpha" in result
    assert "beta" in result
    assert isinstance(result["alpha"], datetime)


def test_set_expiry_raises_on_non_positive_days():
    with pytest.raises(ValueError):
        set_expiry(PROJECT, "prod", days=0)
    with pytest.raises(ValueError):
        set_expiry(PROJECT, "prod", days=-5)

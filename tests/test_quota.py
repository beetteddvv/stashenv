"""Tests for stashenv.quota."""

import pytest

from stashenv.quota import (
    QuotaExceededError,
    _DEFAULT_QUOTA,
    check_quota,
    clear_quota,
    enforce_quota,
    get_quota,
    set_quota,
)
from stashenv.store import save_profile

PROJECT = "quota-test-project"
PASSWORD = "testpass"


@pytest.fixture(autouse=True)
def cleanup(tmp_path, monkeypatch):
    import stashenv.quota as q_mod
    import stashenv.store as s_mod

    monkeypatch.setattr(q_mod, "_stash_dir", lambda p: tmp_path / p)
    monkeypatch.setattr(s_mod, "_stash_dir", lambda p: tmp_path / p)
    yield


def test_set_and_get_quota():
    set_quota(PROJECT, 5)
    assert get_quota(PROJECT) == 5


def test_get_missing_quota_returns_none():
    assert get_quota(PROJECT) is None


def test_set_quota_zero_raises():
    with pytest.raises(ValueError):
        set_quota(PROJECT, 0)


def test_set_quota_negative_raises():
    with pytest.raises(ValueError):
        set_quota(PROJECT, -3)


def test_clear_quota_returns_true_when_existed():
    set_quota(PROJECT, 10)
    assert clear_quota(PROJECT) is True
    assert get_quota(PROJECT) is None


def test_clear_quota_returns_false_when_not_set():
    assert clear_quota(PROJECT) is False


def test_check_quota_uses_default_when_not_set():
    current, limit, ok = check_quota(PROJECT)
    assert limit == _DEFAULT_QUOTA
    assert ok is True


def test_check_quota_reflects_profile_count():
    save_profile(PROJECT, "alpha", {"K": "1"}, PASSWORD)
    save_profile(PROJECT, "beta", {"K": "2"}, PASSWORD)
    set_quota(PROJECT, 3)
    current, limit, ok = check_quota(PROJECT)
    assert current == 2
    assert limit == 3
    assert ok is True


def test_enforce_quota_raises_when_exceeded():
    save_profile(PROJECT, "p1", {"A": "1"}, PASSWORD)
    save_profile(PROJECT, "p2", {"A": "2"}, PASSWORD)
    set_quota(PROJECT, 2)
    with pytest.raises(QuotaExceededError):
        enforce_quota(PROJECT)


def test_enforce_quota_passes_when_under_limit():
    save_profile(PROJECT, "only", {"X": "y"}, PASSWORD)
    set_quota(PROJECT, 5)
    enforce_quota(PROJECT)  # should not raise

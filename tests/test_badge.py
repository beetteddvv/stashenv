"""Tests for stashenv.badge."""

from __future__ import annotations

import pytest

from stashenv.badge import (
    ALLOWED_BADGES,
    get_badge,
    list_badges,
    profiles_with_badge,
    remove_badge,
    set_badge,
)
from stashenv.store import _stash_dir

PROJECT = "test_badge_project"


@pytest.fixture(autouse=True)
def cleanup(tmp_path, monkeypatch):
    import stashenv.badge as badge_mod
    import stashenv.store as store_mod

    monkeypatch.setattr(store_mod, "_stash_dir", lambda p: tmp_path / p)
    monkeypatch.setattr(badge_mod, "_stash_dir", lambda p: tmp_path / p)
    yield


def test_set_and_get_badge():
    set_badge(PROJECT, "prod", "stable")
    assert get_badge(PROJECT, "prod") == "stable"


def test_get_missing_badge_returns_none():
    assert get_badge(PROJECT, "nonexistent") is None


def test_set_overwrites_existing():
    set_badge(PROJECT, "prod", "wip")
    set_badge(PROJECT, "prod", "stable")
    assert get_badge(PROJECT, "prod") == "stable"


def test_invalid_badge_raises():
    with pytest.raises(ValueError, match="Unknown badge"):
        set_badge(PROJECT, "prod", "unknown_badge")


def test_badge_is_lowercased():
    set_badge(PROJECT, "dev", "WIP")
    assert get_badge(PROJECT, "dev") == "wip"


def test_remove_badge_returns_true_when_existed():
    set_badge(PROJECT, "staging", "review")
    assert remove_badge(PROJECT, "staging") is True
    assert get_badge(PROJECT, "staging") is None


def test_remove_badge_returns_false_when_missing():
    assert remove_badge(PROJECT, "ghost") is False


def test_list_badges_returns_all():
    set_badge(PROJECT, "prod", "stable")
    set_badge(PROJECT, "dev", "wip")
    result = list_badges(PROJECT)
    assert result == {"prod": "stable", "dev": "wip"}


def test_profiles_with_badge_filters_correctly():
    set_badge(PROJECT, "prod", "stable")
    set_badge(PROJECT, "staging", "stable")
    set_badge(PROJECT, "dev", "wip")
    stable = profiles_with_badge(PROJECT, "stable")
    assert set(stable) == {"prod", "staging"}


def test_all_allowed_badges_accepted():
    for i, badge in enumerate(ALLOWED_BADGES):
        set_badge(PROJECT, f"profile_{i}", badge)
        assert get_badge(PROJECT, f"profile_{i}") == badge

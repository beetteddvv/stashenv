"""Tests for stashenv.pin."""

from __future__ import annotations

import pytest

from stashenv.pin import (
    get_pinned,
    is_pinned,
    pin_profile,
    unpin_profile,
)


PROJECT = "test_pin_project"


@pytest.fixture(autouse=True)
def cleanup():
    unpin_profile(PROJECT)
    yield
    unpin_profile(PROJECT)


def test_pin_sets_profile():
    pin_profile(PROJECT, "production")
    assert get_pinned(PROJECT) == "production"


def test_get_pinned_returns_none_when_not_set():
    assert get_pinned(PROJECT) is None


def test_unpin_clears_profile():
    pin_profile(PROJECT, "staging")
    unpin_profile(PROJECT)
    assert get_pinned(PROJECT) is None


def test_unpin_is_noop_when_nothing_pinned():
    # Should not raise
    unpin_profile(PROJECT)
    assert get_pinned(PROJECT) is None


def test_is_pinned_true():
    pin_profile(PROJECT, "dev")
    assert is_pinned(PROJECT, "dev") is True


def test_is_pinned_false_different_profile():
    pin_profile(PROJECT, "dev")
    assert is_pinned(PROJECT, "prod") is False


def test_is_pinned_false_nothing_pinned():
    assert is_pinned(PROJECT, "dev") is False


def test_pin_overwrites_previous():
    pin_profile(PROJECT, "alpha")
    pin_profile(PROJECT, "beta")
    assert get_pinned(PROJECT) == "beta"

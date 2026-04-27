"""Tests for stashenv.priority"""

import pytest

from stashenv.priority import (
    set_priority,
    get_priority,
    remove_priority,
    list_priorities,
    top_profile,
)
from stashenv.store import _stash_dir

PROJECT = "test_priority_project"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    p = _stash_dir(PROJECT) / "priorities.json"
    if p.exists():
        p.unlink()


def test_set_and_get_priority():
    set_priority(PROJECT, "prod", 10)
    assert get_priority(PROJECT, "prod") == 10


def test_get_missing_priority_returns_none():
    assert get_priority(PROJECT, "nonexistent") is None


def test_set_overwrites_existing():
    set_priority(PROJECT, "staging", 5)
    set_priority(PROJECT, "staging", 20)
    assert get_priority(PROJECT, "staging") == 20


def test_negative_priority_raises():
    with pytest.raises(ValueError, match="non-negative"):
        set_priority(PROJECT, "dev", -1)


def test_remove_priority_returns_true_when_existed():
    set_priority(PROJECT, "dev", 3)
    assert remove_priority(PROJECT, "dev") is True
    assert get_priority(PROJECT, "dev") is None


def test_remove_priority_returns_false_when_missing():
    assert remove_priority(PROJECT, "ghost") is False


def test_list_priorities_sorted_highest_first():
    set_priority(PROJECT, "dev", 1)
    set_priority(PROJECT, "prod", 100)
    set_priority(PROJECT, "staging", 50)
    ranked = list_priorities(PROJECT)
    names = [name for name, _ in ranked]
    assert names == ["prod", "staging", "dev"]


def test_list_priorities_empty():
    assert list_priorities(PROJECT) == []


def test_top_profile_returns_highest():
    set_priority(PROJECT, "dev", 2)
    set_priority(PROJECT, "prod", 99)
    assert top_profile(PROJECT) == "prod"


def test_top_profile_returns_none_when_empty():
    assert top_profile(PROJECT) is None


def test_zero_priority_is_valid():
    set_priority(PROJECT, "archive", 0)
    assert get_priority(PROJECT, "archive") == 0

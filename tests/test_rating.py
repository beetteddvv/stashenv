"""Tests for stashenv.rating"""

import pytest
from stashenv.rating import (
    set_rating,
    get_rating,
    remove_rating,
    list_ratings,
    top_rated,
)
from stashenv.store import _stash_dir

PROJECT = "test-rating-project"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    path = _stash_dir(PROJECT) / "ratings.json"
    if path.exists():
        path.unlink()


def test_set_and_get_rating():
    set_rating(PROJECT, "dev", 4)
    entry = get_rating(PROJECT, "dev")
    assert entry is not None
    assert entry["stars"] == 4
    assert "updated_at" in entry


def test_get_missing_rating_returns_none():
    result = get_rating(PROJECT, "nonexistent")
    assert result is None


def test_set_overwrites_existing():
    set_rating(PROJECT, "dev", 3)
    set_rating(PROJECT, "dev", 5)
    assert get_rating(PROJECT, "dev")["stars"] == 5


def test_invalid_rating_below_range():
    with pytest.raises(ValueError, match="between 1 and 5"):
        set_rating(PROJECT, "dev", 0)


def test_invalid_rating_above_range():
    with pytest.raises(ValueError, match="between 1 and 5"):
        set_rating(PROJECT, "dev", 6)


def test_remove_rating_returns_true_when_existed():
    set_rating(PROJECT, "dev", 2)
    assert remove_rating(PROJECT, "dev") is True
    assert get_rating(PROJECT, "dev") is None


def test_remove_rating_returns_false_when_missing():
    assert remove_rating(PROJECT, "ghost") is False


def test_list_ratings_returns_all():
    set_rating(PROJECT, "dev", 5)
    set_rating(PROJECT, "staging", 3)
    ratings = list_ratings(PROJECT)
    assert ratings["dev"] == 5
    assert ratings["staging"] == 3


def test_top_rated_sorted_descending():
    set_rating(PROJECT, "dev", 5)
    set_rating(PROJECT, "staging", 3)
    set_rating(PROJECT, "prod", 4)
    results = top_rated(PROJECT, 3)
    stars = [s for _, s in results]
    assert stars == sorted(stars, reverse=True)


def test_top_rated_respects_n():
    for i, name in enumerate(["a", "b", "c", "d", "e"], start=1):
        set_rating(PROJECT, name, i)
    results = top_rated(PROJECT, 2)
    assert len(results) == 2

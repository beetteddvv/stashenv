"""Tests for stashenv.favorite."""

from __future__ import annotations

import pytest

from stashenv.favorite import (
    add_favorite,
    remove_favorite,
    list_favorites,
    is_favorite,
    clear_favorites,
)


PROJECT = "test_fav_project"


@pytest.fixture(autouse=True)
def cleanup():
    clear_favorites(PROJECT)
    yield
    clear_favorites(PROJECT)


def test_add_favorite_creates_entry():
    add_favorite(PROJECT, "dev")
    assert "dev" in list_favorites(PROJECT)


def test_add_favorite_is_idempotent():
    add_favorite(PROJECT, "dev")
    add_favorite(PROJECT, "dev")
    assert list_favorites(PROJECT).count("dev") == 1


def test_add_multiple_favorites():
    add_favorite(PROJECT, "dev")
    add_favorite(PROJECT, "staging")
    favs = list_favorites(PROJECT)
    assert "dev" in favs
    assert "staging" in favs


def test_remove_favorite_returns_true_when_existed():
    add_favorite(PROJECT, "dev")
    result = remove_favorite(PROJECT, "dev")
    assert result is True
    assert "dev" not in list_favorites(PROJECT)


def test_remove_favorite_returns_false_when_missing():
    result = remove_favorite(PROJECT, "nonexistent")
    assert result is False


def test_is_favorite_true():
    add_favorite(PROJECT, "prod")
    assert is_favorite(PROJECT, "prod") is True


def test_is_favorite_false():
    assert is_favorite(PROJECT, "prod") is False


def test_list_favorites_empty_when_none_set():
    assert list_favorites(PROJECT) == []


def test_clear_favorites_removes_all():
    add_favorite(PROJECT, "dev")
    add_favorite(PROJECT, "staging")
    clear_favorites(PROJECT)
    assert list_favorites(PROJECT) == []

"""Tests for stashenv.group."""

import pytest

from stashenv.group import (
    add_to_group,
    delete_group,
    get_group_members,
    get_profile_groups,
    list_groups,
    remove_from_group,
)


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """Redirect stash dir to a temp location."""
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path))
    return "myproject"


def test_add_creates_group(project):
    add_to_group(project, "staging", "profile_a")
    assert "staging" in list_groups(project)


def test_add_is_idempotent(project):
    add_to_group(project, "staging", "profile_a")
    add_to_group(project, "staging", "profile_a")
    assert get_group_members(project, "staging").count("profile_a") == 1


def test_add_multiple_profiles(project):
    add_to_group(project, "prod", "p1")
    add_to_group(project, "prod", "p2")
    members = get_group_members(project, "prod")
    assert "p1" in members
    assert "p2" in members


def test_remove_profile_returns_true(project):
    add_to_group(project, "dev", "alice")
    result = remove_from_group(project, "dev", "alice")
    assert result is True
    assert "alice" not in get_group_members(project, "dev")


def test_remove_missing_profile_returns_false(project):
    result = remove_from_group(project, "dev", "ghost")
    assert result is False


def test_empty_group_is_pruned(project):
    add_to_group(project, "temp", "only_one")
    remove_from_group(project, "temp", "only_one")
    assert "temp" not in list_groups(project)


def test_get_profile_groups(project):
    add_to_group(project, "a", "shared")
    add_to_group(project, "b", "shared")
    groups = get_profile_groups(project, "shared")
    assert "a" in groups
    assert "b" in groups


def test_get_profile_groups_empty_when_none(project):
    assert get_profile_groups(project, "orphan") == []


def test_delete_group_returns_true(project):
    add_to_group(project, "old", "p")
    assert delete_group(project, "old") is True
    assert "old" not in list_groups(project)


def test_delete_missing_group_returns_false(project):
    assert delete_group(project, "nonexistent") is False


def test_list_groups_empty_initially(project):
    assert list_groups(project) == []

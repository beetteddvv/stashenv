"""Tests for stashenv.tag module."""

import pytest

from stashenv.tag import add_tag, remove_tag, get_tags, profiles_with_tag, clear_tags


@pytest.fixture
def project(tmp_path, monkeypatch):
    """Isolate stash directory to a temp path."""
    import stashenv.store as store
    import stashenv.tag as tag_mod

    monkeypatch.setattr(store, "_stash_dir", lambda p: tmp_path / p)
    monkeypatch.setattr(tag_mod, "_stash_dir", lambda p: tmp_path / p)
    return "myproject"


def test_add_tag_creates_entry(project):
    add_tag(project, "dev", "active")
    assert "active" in get_tags(project, "dev")


def test_add_tag_is_idempotent(project):
    add_tag(project, "dev", "active")
    add_tag(project, "dev", "active")
    assert get_tags(project, "dev").count("active") == 1


def test_add_multiple_tags(project):
    add_tag(project, "staging", "ci")
    add_tag(project, "staging", "review")
    tags = get_tags(project, "staging")
    assert "ci" in tags
    assert "review" in tags


def test_remove_tag(project):
    add_tag(project, "dev", "active")
    add_tag(project, "dev", "local")
    remove_tag(project, "dev", "active")
    tags = get_tags(project, "dev")
    assert "active" not in tags
    assert "local" in tags


def test_remove_tag_noop_if_missing(project):
    add_tag(project, "dev", "local")
    remove_tag(project, "dev", "nonexistent")  # should not raise
    assert get_tags(project, "dev") == ["local"]


def test_remove_last_tag_cleans_up_profile(project):
    add_tag(project, "dev", "only")
    remove_tag(project, "dev", "only")
    assert get_tags(project, "dev") == []


def test_profiles_with_tag(project):
    add_tag(project, "dev", "active")
    add_tag(project, "staging", "active")
    add_tag(project, "prod", "stable")
    result = profiles_with_tag(project, "active")
    assert "dev" in result
    assert "staging" in result
    assert "prod" not in result


def test_profiles_with_tag_returns_empty_when_none(project):
    assert profiles_with_tag(project, "ghost") == []


def test_clear_tags(project):
    add_tag(project, "dev", "a")
    add_tag(project, "dev", "b")
    clear_tags(project, "dev")
    assert get_tags(project, "dev") == []


def test_get_tags_unknown_profile_returns_empty(project):
    assert get_tags(project, "noprofile") == []

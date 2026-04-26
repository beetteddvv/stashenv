"""Tests for stashenv.access module."""

import pytest

from stashenv.access import (
    set_allowed_contexts,
    get_allowed_contexts,
    remove_access_rule,
    is_allowed,
    list_rules,
)


PROJECT = "test-access-project"


@pytest.fixture(autouse=True)
def cleanup(tmp_path, monkeypatch):
    import stashenv.access as mod
    import stashenv.store as store_mod

    monkeypatch.setattr(store_mod, "_stash_dir", lambda p: tmp_path / p)
    monkeypatch.setattr(mod, "_stash_dir", lambda p: tmp_path / p)
    yield


def test_set_and_get_allowed_contexts():
    set_allowed_contexts(PROJECT, "prod", ["ci", "prod"])
    result = get_allowed_contexts(PROJECT, "prod")
    assert result == ["ci", "prod"]


def test_get_missing_rule_returns_none():
    result = get_allowed_contexts(PROJECT, "nonexistent")
    assert result is None


def test_set_deduplicates_contexts():
    set_allowed_contexts(PROJECT, "staging", ["ci", "ci", "local"])
    result = get_allowed_contexts(PROJECT, "staging")
    assert result == ["ci", "local"]


def test_is_allowed_when_no_rule():
    assert is_allowed(PROJECT, "dev", "local") is True
    assert is_allowed(PROJECT, "dev", "prod") is True


def test_is_allowed_with_matching_context():
    set_allowed_contexts(PROJECT, "prod", ["ci", "prod"])
    assert is_allowed(PROJECT, "prod", "prod") is True


def test_is_not_allowed_with_wrong_context():
    set_allowed_contexts(PROJECT, "prod", ["ci", "prod"])
    assert is_allowed(PROJECT, "prod", "local") is False


def test_remove_access_rule_returns_true_when_existed():
    set_allowed_contexts(PROJECT, "staging", ["local"])
    assert remove_access_rule(PROJECT, "staging") is True


def test_remove_access_rule_returns_false_when_missing():
    assert remove_access_rule(PROJECT, "ghost") is False


def test_remove_makes_profile_unrestricted():
    set_allowed_contexts(PROJECT, "dev", ["ci"])
    remove_access_rule(PROJECT, "dev")
    assert get_allowed_contexts(PROJECT, "dev") is None
    assert is_allowed(PROJECT, "dev", "local") is True


def test_list_rules_returns_all():
    set_allowed_contexts(PROJECT, "alpha", ["local"])
    set_allowed_contexts(PROJECT, "beta", ["ci", "prod"])
    rules = list_rules(PROJECT)
    assert "alpha" in rules
    assert "beta" in rules
    assert rules["alpha"] == ["local"]


def test_list_rules_empty_project():
    rules = list_rules("totally-new-project-xyz")
    assert rules == {}

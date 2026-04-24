"""Tests for stashenv.alias."""

import pytest

from stashenv.alias import (
    set_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    clear_aliases,
)


@pytest.fixture()
def project(tmp_path):
    return str(tmp_path)


def test_set_and_resolve(project):
    set_alias(project, "prod", "production")
    assert resolve_alias(project, "prod") == "production"


def test_resolve_missing_returns_none(project):
    assert resolve_alias(project, "nonexistent") is None


def test_set_overwrites_existing(project):
    set_alias(project, "prod", "production")
    set_alias(project, "prod", "prod-v2")
    assert resolve_alias(project, "prod") == "prod-v2"


def test_remove_alias_returns_true_when_existed(project):
    set_alias(project, "staging", "staging-env")
    result = remove_alias(project, "staging")
    assert result is True
    assert resolve_alias(project, "staging") is None


def test_remove_alias_returns_false_when_missing(project):
    result = remove_alias(project, "ghost")
    assert result is False


def test_list_aliases_returns_all(project):
    set_alias(project, "dev", "development")
    set_alias(project, "prod", "production")
    mapping = list_aliases(project)
    assert mapping == {"dev": "development", "prod": "production"}


def test_list_aliases_empty_project(project):
    assert list_aliases(project) == {}


def test_clear_aliases_returns_count(project):
    set_alias(project, "a", "alpha")
    set_alias(project, "b", "beta")
    count = clear_aliases(project)
    assert count == 2


def test_clear_aliases_removes_all(project):
    set_alias(project, "a", "alpha")
    clear_aliases(project)
    assert list_aliases(project) == {}


def test_clear_aliases_on_empty_project_returns_zero(project):
    assert clear_aliases(project) == 0

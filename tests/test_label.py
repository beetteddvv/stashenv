"""Tests for stashenv.label."""

import pytest

from stashenv.label import (
    set_label,
    get_label,
    remove_label,
    list_labels,
    resolve_display_name,
)
from stashenv.store import _stash_dir


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """Redirect stash dir to a temp location and return a project name."""
    import stashenv.store as store_mod
    import stashenv.label as label_mod

    monkeypatch.setattr(store_mod, "_stash_dir", lambda p: tmp_path / p)
    monkeypatch.setattr(label_mod, "_stash_dir", lambda p: tmp_path / p)
    return "myproject"


def test_set_and_get_label(project):
    set_label(project, "prod", "Production")
    assert get_label(project, "prod") == "Production"


def test_get_missing_label_returns_none(project):
    assert get_label(project, "nonexistent") is None


def test_set_overwrites_existing(project):
    set_label(project, "staging", "Staging")
    set_label(project, "staging", "Pre-Production")
    assert get_label(project, "staging") == "Pre-Production"


def test_set_strips_whitespace(project):
    set_label(project, "dev", "  Development  ")
    assert get_label(project, "dev") == "Development"


def test_remove_label_returns_true_when_existed(project):
    set_label(project, "prod", "Production")
    assert remove_label(project, "prod") is True
    assert get_label(project, "prod") is None


def test_remove_label_returns_false_when_missing(project):
    assert remove_label(project, "ghost") is False


def test_list_labels_returns_all(project):
    set_label(project, "prod", "Production")
    set_label(project, "dev", "Development")
    labels = list_labels(project)
    assert labels == {"prod": "Production", "dev": "Development"}


def test_list_labels_empty_project(project):
    assert list_labels(project) == {}


def test_resolve_display_name_uses_label(project):
    set_label(project, "prod", "Production")
    assert resolve_display_name(project, "prod") == "Production"


def test_resolve_display_name_falls_back_to_profile(project):
    assert resolve_display_name(project, "unlabeled") == "unlabeled"

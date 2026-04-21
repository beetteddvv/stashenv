"""Tests for stashenv.history"""

import pytest
from pathlib import Path

from stashenv.history import (
    record_load,
    get_history,
    last_loaded,
    clear_history,
    format_history,
    _history_path,
)


@pytest.fixture()
def project(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path))
    # patch _stash_dir so files land in tmp_path
    import stashenv.store as store_mod
    monkeypatch.setattr(store_mod, "_stash_dir", lambda p: tmp_path / p)
    import stashenv.history as hist_mod
    monkeypatch.setattr(hist_mod, "_stash_dir", lambda p: tmp_path / p)
    proj = "myproject"
    (tmp_path / proj).mkdir(parents=True, exist_ok=True)
    return proj


def test_record_and_retrieve(project):
    record_load(project, "dev")
    history = get_history(project)
    assert len(history) == 1
    assert history[0]["profile"] == "dev"


def test_history_most_recent_first(project):
    record_load(project, "dev")
    record_load(project, "staging")
    record_load(project, "prod")
    history = get_history(project)
    assert history[0]["profile"] == "prod"
    assert history[1]["profile"] == "staging"
    assert history[2]["profile"] == "dev"


def test_limit_parameter(project):
    for name in ["a", "b", "c", "d"]:
        record_load(project, name)
    history = get_history(project, limit=2)
    assert len(history) == 2
    assert history[0]["profile"] == "d"


def test_last_loaded_returns_most_recent(project):
    record_load(project, "dev")
    record_load(project, "prod")
    assert last_loaded(project) == "prod"


def test_last_loaded_empty_project(project):
    assert last_loaded(project) is None


def test_clear_history(project):
    record_load(project, "dev")
    clear_history(project)
    assert get_history(project) == []


def test_clear_history_no_file_is_noop(project):
    # should not raise if no history file exists
    clear_history(project)
    assert get_history(project) == []


def test_format_history_output(project):
    record_load(project, "dev")
    record_load(project, "prod")
    history = get_history(project)
    output = format_history(history)
    assert "prod" in output
    assert "dev" in output


def test_format_history_empty():
    output = format_history([])
    assert "no history" in output

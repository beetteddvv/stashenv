"""Tests for stashenv.notes."""

import pytest

from stashenv.notes import (
    set_note,
    get_note,
    get_note_entry,
    delete_note,
    list_notes,
)

PROJECT = "test_notes_project"


@pytest.fixture(autouse=True)
def cleanup(tmp_path, monkeypatch):
    import stashenv.notes as notes_mod
    import stashenv.store as store_mod

    monkeypatch.setattr(store_mod, "_stash_dir", lambda p: tmp_path / p)
    monkeypatch.setattr(notes_mod, "_stash_dir", lambda p: tmp_path / p)
    yield


def test_set_and_get_note():
    set_note(PROJECT, "dev", "Used for local development")
    assert get_note(PROJECT, "dev") == "Used for local development"


def test_get_missing_note_returns_none():
    assert get_note(PROJECT, "nonexistent") is None


def test_set_overwrites_existing_note():
    set_note(PROJECT, "dev", "old text")
    set_note(PROJECT, "dev", "new text")
    assert get_note(PROJECT, "dev") == "new text"


def test_get_note_entry_includes_updated_at():
    set_note(PROJECT, "staging", "Staging env")
    entry = get_note_entry(PROJECT, "staging")
    assert entry is not None
    assert entry["text"] == "Staging env"
    assert "updated_at" in entry


def test_delete_note_returns_true_when_existed():
    set_note(PROJECT, "prod", "Production")
    assert delete_note(PROJECT, "prod") is True
    assert get_note(PROJECT, "prod") is None


def test_delete_note_returns_false_when_missing():
    assert delete_note(PROJECT, "ghost") is False


def test_list_notes_returns_all():
    set_note(PROJECT, "dev", "dev note")
    set_note(PROJECT, "staging", "staging note")
    result = list_notes(PROJECT)
    assert result["dev"] == "dev note"
    assert result["staging"] == "staging note"


def test_list_notes_empty_project():
    assert list_notes(PROJECT) == {}

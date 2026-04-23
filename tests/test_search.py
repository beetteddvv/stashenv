"""Tests for stashenv.search."""

import pytest

from stashenv.store import save_profile
from stashenv.search import search_profiles, SearchMatch


PROJECT = "test_search_proj"
PASSWORD = "hunter2"


@pytest.fixture(autouse=True)
def _seed(tmp_path, monkeypatch):
    import stashenv.store as store_mod

    monkeypatch.setattr(store_mod, "_stash_dir", lambda p: tmp_path / p)

    save_profile(PROJECT, "dev", PASSWORD, "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n")
    save_profile(PROJECT, "prod", PASSWORD, "DB_HOST=prod.example.com\nDB_PORT=5432\nSECRET=xyz999\n")
    save_profile(PROJECT, "staging", PASSWORD, "DB_HOST=staging.internal\nAPI_KEY=mykey\n")


def test_search_by_key_pattern():
    matches = search_profiles(PROJECT, PASSWORD, key_pattern="DB_HOST")
    profiles = {m.profile for m in matches}
    assert profiles == {"dev", "prod", "staging"}


def test_search_by_value_pattern():
    matches = search_profiles(PROJECT, PASSWORD, value_pattern="5432")
    profiles = {m.profile for m in matches}
    assert profiles == {"dev", "prod"}


def test_search_by_key_and_value():
    matches = search_profiles(PROJECT, PASSWORD, key_pattern="SECRET", value_pattern="abc")
    assert len(matches) == 1
    assert matches[0].profile == "dev"
    assert matches[0].key == "SECRET"


def test_exact_match():
    matches = search_profiles(PROJECT, PASSWORD, key_pattern="db_host", exact=True)
    assert matches == []

    matches = search_profiles(PROJECT, PASSWORD, key_pattern="DB_HOST", exact=True)
    assert len(matches) == 3


def test_no_pattern_raises():
    with pytest.raises(ValueError, match="at least one"):
        search_profiles(PROJECT, PASSWORD)


def test_search_match_str():
    m = SearchMatch(profile="dev", key="FOO", value="bar")
    assert str(m) == "[dev] FOO=bar"


def test_wrong_password_skips_profile(tmp_path, monkeypatch):
    import stashenv.store as store_mod

    monkeypatch.setattr(store_mod, "_stash_dir", lambda p: tmp_path / p)
    save_profile("other", "alpha", "correct", "KEY=val\n")

    # wrong password — should return empty rather than raise
    matches = search_profiles("other", "wrong", key_pattern="KEY")
    assert matches == []

"""Tests for stashenv.compare."""

import pytest
from stashenv.store import save_profile
from stashenv.compare import compare_profiles, compare_summary, CompareError


PROJECT = "test_compare_project"
PASSWORD = "s3cr3t"


@pytest.fixture(autouse=True)
def _clean(tmp_path, monkeypatch):
    import stashenv.store as store_mod
    monkeypatch.setattr(store_mod, "_stash_dir", lambda p: tmp_path / p)
    import stashenv.compare as cmp_mod
    monkeypatch.setattr(cmp_mod, "load_profile", store_mod.load_profile)
    monkeypatch.setattr(cmp_mod, "list_profiles", store_mod.list_profiles)


def _seed(profile: str, content: str):
    save_profile(PROJECT, profile, content, PASSWORD)


def test_compare_detects_added_key():
    _seed("a", "FOO=bar\n")
    _seed("b", "FOO=bar\nBAZ=new\n")
    entries = compare_profiles(PROJECT, "a", "b", PASSWORD)
    statuses = {e.key: e.status for e in entries}
    assert statuses["BAZ"] == "added"


def test_compare_detects_removed_key():
    _seed("a", "FOO=bar\nOLD=gone\n")
    _seed("b", "FOO=bar\n")
    entries = compare_profiles(PROJECT, "a", "b", PASSWORD)
    statuses = {e.key: e.status for e in entries}
    assert statuses["OLD"] == "removed"


def test_compare_detects_changed_value():
    _seed("a", "FOO=bar\n")
    _seed("b", "FOO=baz\n")
    entries = compare_profiles(PROJECT, "a", "b", PASSWORD)
    statuses = {e.key: e.status for e in entries}
    assert statuses["FOO"] == "changed"


def test_unchanged_hidden_by_default():
    _seed("a", "FOO=bar\nBAZ=qux\n")
    _seed("b", "FOO=bar\nBAZ=qux\n")
    entries = compare_profiles(PROJECT, "a", "b", PASSWORD, show_unchanged=False)
    assert entries == []


def test_show_unchanged_includes_all_keys():
    _seed("a", "FOO=bar\n")
    _seed("b", "FOO=bar\n")
    entries = compare_profiles(PROJECT, "a", "b", PASSWORD, show_unchanged=True)
    assert any(e.key == "FOO" and e.status == "unchanged" for e in entries)


def test_missing_profile_raises():
    _seed("a", "FOO=bar\n")
    with pytest.raises(CompareError, match="ghost"):
        compare_profiles(PROJECT, "a", "ghost", PASSWORD)


def test_compare_summary_counts():
    _seed("a", "FOO=bar\nOLD=x\n")
    _seed("b", "FOO=changed\nNEW=y\n")
    entries = compare_profiles(PROJECT, "a", "b", PASSWORD, show_unchanged=True)
    s = compare_summary(entries)
    assert s["changed"] == 1
    assert s["added"] == 1
    assert s["removed"] == 1
    assert s["total"] == 3

"""Tests for stashenv.checkpoint."""

from __future__ import annotations

import pytest

from stashenv.checkpoint import (
    create_checkpoint,
    delete_checkpoint,
    get_checkpoint,
    list_checkpoints,
    restore_checkpoint,
)
from stashenv.store import save_profile

PROJECT = "test_checkpoint_project"
PROFILE = "dev"
PASSWORD = "s3cr3t"


@pytest.fixture(autouse=True)
def cleanup(tmp_path, monkeypatch):
    import stashenv.store as store_mod
    import stashenv.checkpoint as cp_mod

    monkeypatch.setattr(store_mod, "_stash_dir", lambda proj: tmp_path / proj)
    monkeypatch.setattr(cp_mod, "_stash_dir", lambda proj: tmp_path / proj)
    monkeypatch.setattr(cp_mod, "load_profile", lambda proj, prof, pw: store_mod.load_profile(proj, prof, pw))
    monkeypatch.setattr(cp_mod, "save_profile", lambda proj, prof, env, pw: store_mod.save_profile(proj, prof, env, pw))
    yield


def _seed(env: dict | None = None):
    save_profile(PROJECT, PROFILE, env or {"KEY": "value1", "OTHER": "abc"}, PASSWORD)


def test_create_checkpoint_returns_name():
    _seed()
    name = create_checkpoint(PROJECT, PROFILE, PASSWORD, name="cp1")
    assert name == "cp1"


def test_create_checkpoint_auto_name():
    _seed()
    name = create_checkpoint(PROJECT, PROFILE, PASSWORD)
    assert len(name) > 0
    assert "T" in name  # ISO-ish timestamp


def test_list_checkpoints_includes_created():
    _seed()
    create_checkpoint(PROJECT, PROFILE, PASSWORD, name="alpha")
    create_checkpoint(PROJECT, PROFILE, PASSWORD, name="beta")
    names = list_checkpoints(PROJECT, PROFILE)
    assert "alpha" in names
    assert "beta" in names


def test_list_checkpoints_sorted():
    _seed()
    create_checkpoint(PROJECT, PROFILE, PASSWORD, name="zzz")
    create_checkpoint(PROJECT, PROFILE, PASSWORD, name="aaa")
    names = list_checkpoints(PROJECT, PROFILE)
    assert names == sorted(names)


def test_restore_checkpoint_reverts_profile():
    _seed({"KEY": "original"})
    create_checkpoint(PROJECT, PROFILE, PASSWORD, name="snap1")
    save_profile(PROJECT, PROFILE, {"KEY": "modified"}, PASSWORD)
    restored = restore_checkpoint(PROJECT, PROFILE, "snap1", PASSWORD)
    assert restored["KEY"] == "original"


def test_restore_missing_checkpoint_raises():
    _seed()
    with pytest.raises(FileNotFoundError, match="no_such"):
        restore_checkpoint(PROJECT, PROFILE, "no_such", PASSWORD)


def test_delete_checkpoint_returns_true_when_existed():
    _seed()
    create_checkpoint(PROJECT, PROFILE, PASSWORD, name="to_del")
    assert delete_checkpoint(PROJECT, PROFILE, "to_del") is True
    assert "to_del" not in list_checkpoints(PROJECT, PROFILE)


def test_delete_missing_checkpoint_returns_false():
    _seed()
    assert delete_checkpoint(PROJECT, PROFILE, "ghost") is False


def test_get_checkpoint_contains_metadata():
    _seed({"FOO": "bar"})
    create_checkpoint(PROJECT, PROFILE, PASSWORD, name="meta_cp")
    data = get_checkpoint(PROJECT, PROFILE, "meta_cp")
    assert data["name"] == "meta_cp"
    assert "created_at" in data
    assert data["env"]["FOO"] == "bar"

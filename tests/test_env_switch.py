"""Tests for stashenv.env_switch."""

import pytest
from pathlib import Path

from stashenv.store import save_profile
from stashenv.env_switch import switch_to_profile, switch_to_pinned, SwitchError
from stashenv.lock import lock_profile
from stashenv.pin import pin_profile, unpin_profile

PROJECT = "test_switch_project"
PASSWORD = "s3cr3t"


@pytest.fixture(autouse=True)
def clean(tmp_path, monkeypatch):
    import stashenv.store as store_mod
    import stashenv.lock as lock_mod
    import stashenv.pin as pin_mod
    import stashenv.history as hist_mod

    stash = tmp_path / ".stashenv"
    monkeypatch.setattr(store_mod, "_stash_dir", lambda p: stash / p)
    monkeypatch.setattr(lock_mod, "_lock_path", lambda p: stash / p / ".locks.json")
    monkeypatch.setattr(pin_mod, "_pin_path", lambda p: stash / p / ".pin.json")
    monkeypatch.setattr(hist_mod, "_history_path", lambda p: stash / p / ".history.json")
    yield


def _seed(profile: str, content: str = "KEY=val\nOTHER=123"):
    save_profile(PROJECT, profile, content, PASSWORD)


def test_switch_returns_env_dict():
    _seed("dev")
    env = switch_to_profile(PROJECT, "dev", PASSWORD)
    assert env == {"KEY": "val", "OTHER": "123"}


def test_switch_writes_dotenv_file(tmp_path):
    _seed("dev")
    out = tmp_path / ".env"
    switch_to_profile(PROJECT, "dev", PASSWORD, out)
    assert out.exists()
    text = out.read_text()
    assert "KEY=val" in text


def test_switch_missing_profile_raises():
    with pytest.raises(SwitchError, match="not found"):
        switch_to_profile(PROJECT, "ghost", PASSWORD)


def test_switch_locked_profile_raises():
    _seed("staging")
    lock_profile(PROJECT, "staging")
    with pytest.raises(SwitchError, match="locked"):
        switch_to_profile(PROJECT, "staging", PASSWORD)


def test_switch_to_pinned_returns_profile_name():
    _seed("prod")
    pin_profile(PROJECT, "prod")
    name, env = switch_to_pinned(PROJECT, PASSWORD)
    assert name == "prod"
    assert "KEY" in env


def test_switch_to_pinned_no_pin_raises():
    unpin_profile(PROJECT)
    with pytest.raises(SwitchError, match="No profile is pinned"):
        switch_to_pinned(PROJECT, PASSWORD)

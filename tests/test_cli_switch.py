"""CLI tests for the switch command group."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from stashenv.cli_switch import switch
from stashenv.store import save_profile
from stashenv.pin import pin_profile

PROJECT = "cli_switch_proj"
PASSWORD = "pw"


@pytest.fixture()
def patch_stash(tmp_path, monkeypatch):
    import stashenv.store as store_mod
    import stashenv.lock as lock_mod
    import stashenv.pin as pin_mod
    import stashenv.history as hist_mod

    stash = tmp_path / ".stashenv"
    monkeypatch.setattr(store_mod, "_stash_dir", lambda p: stash / p)
    monkeypatch.setattr(lock_mod, "_lock_path", lambda p: stash / p / ".locks.json")
    monkeypatch.setattr(pin_mod, "_pin_path", lambda p: stash / p / ".pin.json")
    monkeypatch.setattr(hist_mod, "_history_path", lambda p: stash / p / ".history.json")
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def test_to_cmd_success(patch_stash, runner):
    out_file = patch_stash / "out.env"
    save_profile(PROJECT, "dev", "A=1\nB=2", PASSWORD)
    result = runner.invoke(
        switch, ["to", PROJECT, "dev", "--password", PASSWORD, "--output", str(out_file)]
    )
    assert result.exit_code == 0
    assert "Switched to profile 'dev'" in result.output
    assert out_file.exists()


def test_to_cmd_missing_profile(patch_stash, runner):
    result = runner.invoke(
        switch, ["to", PROJECT, "nope", "--password", PASSWORD]
    )
    assert result.exit_code == 1
    assert "Error" in result.output


def test_pinned_cmd_success(patch_stash, runner):
    out_file = patch_stash / "pinned.env"
    save_profile(PROJECT, "prod", "X=99", PASSWORD)
    pin_profile(PROJECT, "prod")
    result = runner.invoke(
        switch,
        ["pinned", PROJECT, "--password", PASSWORD, "--output", str(out_file)],
    )
    assert result.exit_code == 0
    assert "prod" in result.output


def test_pinned_cmd_no_pin(patch_stash, runner):
    result = runner.invoke(
        switch, ["pinned", PROJECT, "--password", PASSWORD]
    )
    assert result.exit_code == 1
    assert "No profile is pinned" in result.output

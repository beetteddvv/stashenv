"""Tests for the pin CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from stashenv.cli_pin import pin
from stashenv.pin import unpin_profile


PROJECT = "cli_pin_test_project"


@pytest.fixture(autouse=True)
def clean_pin():
    unpin_profile(PROJECT)
    yield
    unpin_profile(PROJECT)


@pytest.fixture
def runner():
    return CliRunner()


def test_set_and_show(runner):
    result = runner.invoke(pin, ["set", PROJECT, "production"])
    assert result.exit_code == 0
    assert "Pinned 'production'" in result.output

    result = runner.invoke(pin, ["show", PROJECT])
    assert result.exit_code == 0
    assert "production" in result.output


def test_show_nothing_pinned(runner):
    result = runner.invoke(pin, ["show", PROJECT])
    assert result.exit_code == 0
    assert "No pinned profile" in result.output


def test_unset_removes_pin(runner):
    runner.invoke(pin, ["set", PROJECT, "staging"])
    result = runner.invoke(pin, ["unset", PROJECT])
    assert result.exit_code == 0
    assert "Unpinned" in result.output


def test_unset_when_nothing_pinned(runner):
    result = runner.invoke(pin, ["unset", PROJECT])
    assert result.exit_code == 0
    assert "No pinned profile" in result.output


def test_check_passes_when_pinned(runner):
    runner.invoke(pin, ["set", PROJECT, "dev"])
    result = runner.invoke(pin, ["check", PROJECT, "dev"])
    assert result.exit_code == 0
    assert "pinned default" in result.output


def test_check_fails_when_not_pinned(runner):
    runner.invoke(pin, ["set", PROJECT, "dev"])
    result = runner.invoke(pin, ["check", PROJECT, "prod"])
    assert result.exit_code == 1
    assert "NOT pinned" in result.output

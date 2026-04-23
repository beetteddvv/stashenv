"""CLI tests for the remind command group."""

import pytest
from click.testing import CliRunner
from stashenv.cli_remind import remind
from stashenv.remind import _reminders_path


PROJECT = "__test_cli_remind__"


@pytest.fixture(autouse=True)
def clean():
    yield
    p = _reminders_path(PROJECT)
    if p.exists():
        p.unlink()


@pytest.fixture
def runner():
    return CliRunner()


def test_set_and_show(runner):
    result = runner.invoke(remind, ["set", PROJECT, "dev", "rotate soon"])
    assert result.exit_code == 0
    assert "set" in result.output.lower()

    result = runner.invoke(remind, ["show", PROJECT, "dev"])
    assert result.exit_code == 0
    assert "rotate soon" in result.output


def test_show_missing(runner):
    result = runner.invoke(remind, ["show", PROJECT, "nope"])
    assert result.exit_code == 0
    assert "No reminder" in result.output


def test_clear_existing(runner):
    runner.invoke(remind, ["set", PROJECT, "staging", "check this"])
    result = runner.invoke(remind, ["clear", PROJECT, "staging"])
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_clear_missing(runner):
    result = runner.invoke(remind, ["clear", PROJECT, "ghost"])
    assert result.exit_code == 0
    assert "No reminder found" in result.output


def test_list_shows_all(runner):
    runner.invoke(remind, ["set", PROJECT, "dev", "msg one"])
    runner.invoke(remind, ["set", PROJECT, "prod", "msg two"])
    result = runner.invoke(remind, ["list", PROJECT])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output


def test_list_empty(runner):
    result = runner.invoke(remind, ["list", PROJECT])
    assert result.exit_code == 0
    assert "No reminders" in result.output

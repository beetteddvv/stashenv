"""CLI tests for stashenv.cli_quota."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from stashenv.cli_quota import quota


@pytest.fixture
def runner():
    return CliRunner()


def _patch(func_name, **kwargs):
    return patch(f"stashenv.cli_quota.{func_name}", **kwargs)


def test_set_cmd_success(runner):
    with _patch("set_quota") as mock_set:
        result = runner.invoke(quota, ["set", "myproject", "10"])
    assert result.exit_code == 0
    assert "10" in result.output
    mock_set.assert_called_once_with("myproject", 10)


def test_set_cmd_invalid_limit(runner):
    with _patch("set_quota", side_effect=ValueError("must be at least 1")):
        result = runner.invoke(quota, ["set", "myproject", "0"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_show_cmd_with_limit(runner):
    with _patch("get_quota", return_value=7):
        result = runner.invoke(quota, ["show", "myproject"])
    assert result.exit_code == 0
    assert "7" in result.output


def test_show_cmd_no_limit(runner):
    with _patch("get_quota", return_value=None):
        result = runner.invoke(quota, ["show", "myproject"])
    assert result.exit_code == 0
    assert "No explicit quota" in result.output


def test_clear_cmd_existed(runner):
    with _patch("clear_quota", return_value=True):
        result = runner.invoke(quota, ["clear", "myproject"])
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_clear_cmd_not_set(runner):
    with _patch("clear_quota", return_value=False):
        result = runner.invoke(quota, ["clear", "myproject"])
    assert "No quota was set" in result.output


def test_check_cmd_within_quota(runner):
    with _patch("check_quota", return_value=(3, 10, True)):
        result = runner.invoke(quota, ["check", "myproject"])
    assert result.exit_code == 0
    assert "OK" in result.output
    assert "3/10" in result.output


def test_check_cmd_exceeded(runner):
    with _patch("check_quota", return_value=(10, 10, False)):
        result = runner.invoke(quota, ["check", "myproject"])
    assert result.exit_code == 1
    assert "EXCEEDED" in result.output

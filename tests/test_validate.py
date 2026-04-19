"""Tests for stashenv.validate."""
import pytest
from stashenv.validate import validate_env, ValidationResult


def test_valid_env_passes():
    result = validate_env({"FOO": "bar", "BAZ": "qux"})
    assert result.valid is True
    assert result.errors == []
    assert result.warnings == []


def test_empty_profile_warns():
    result = validate_env({})
    assert result.valid is True
    assert any("empty" in w.lower() for w in result.warnings)


def test_empty_value_warns():
    result = validate_env({"KEY": ""})
    assert result.valid is True
    assert any("KEY" in w for w in result.warnings)


def test_invalid_key_with_space():
    result = validate_env({"MY KEY": "val"})
    assert result.valid is False
    assert any("MY KEY" in e for e in result.errors)


def test_invalid_key_starts_with_digit():
    result = validate_env({"1FOO": "val"})
    assert result.valid is False
    assert any("1FOO" in e for e in result.errors)


def test_invalid_key_with_dash():
    result = validate_env({"MY-KEY": "val"})
    assert result.valid is False


def test_newline_in_value_is_error():
    result = validate_env({"FOO": "line1\nline2"})
    assert result.valid is False
    assert any("FOO" in e for e in result.errors)


def test_multiple_errors_collected():
    result = validate_env({"1BAD": "ok", "ALSO BAD": "val"})
    assert result.valid is False
    assert len(result.errors) == 2


def test_str_output_ok():
    result = validate_env({"A": "b"})
    assert str(result) == "  OK"


def test_str_output_errors_and_warnings():
    result = validate_env({"1BAD": ""})
    out = str(result)
    assert "ERROR" in out
    assert "WARNING" in out

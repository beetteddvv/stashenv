"""Tests for stashenv.export module."""

import os
from pathlib import Path

import pytest

from stashenv.export import (
    apply_to_current_env,
    parse_dotenv,
    read_dotenv_file,
    render_dotenv,
    write_dotenv_file,
)


def test_parse_basic():
    text = "FOO=bar\nBAZ=qux\n"
    assert parse_dotenv(text) == {"FOO": "bar", "BAZ": "qux"}


def test_parse_ignores_comments_and_blanks():
    text = "# comment\n\nFOO=bar\n"
    assert parse_dotenv(text) == {"FOO": "bar"}


def test_parse_strips_quotes():
    text = 'KEY="hello world"\nOTHER=\'simple\'\n'
    result = parse_dotenv(text)
    assert result["KEY"] == "hello world"
    assert result["OTHER"] == "simple"


def test_parse_ignores_lines_without_equals():
    text = "NODOTS\nFOO=bar\n"
    assert parse_dotenv(text) == {"FOO": "bar"}


def test_render_basic():
    env = {"FOO": "bar", "BAZ": "qux"}
    rendered = render_dotenv(env)
    parsed_back = parse_dotenv(rendered)
    assert parsed_back == env


def test_render_quotes_values_with_spaces():
    env = {"MSG": "hello world"}
    rendered = render_dotenv(env)
    assert '"' in rendered
    assert parse_dotenv(rendered) == env


def test_render_empty():
    assert render_dotenv({}) == ""


def test_read_write_roundtrip(tmp_path: Path):
    env_file = tmp_path / ".env"
    original = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"}
    write_dotenv_file(env_file, original)
    loaded = read_dotenv_file(env_file)
    assert loaded == original


def test_apply_to_current_env():
    env = {"STASHENV_TEST_KEY": "stashenv_test_value"}
    apply_to_current_env(env)
    assert os.environ.get("STASHENV_TEST_KEY") == "stashenv_test_value"
    # Cleanup
    del os.environ["STASHENV_TEST_KEY"]

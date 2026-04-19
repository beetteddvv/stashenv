import pytest
from pathlib import Path
from stashenv.template import parse_template, check_profile_against_template, TemplateCheckResult


@pytest.fixture
def template_file(tmp_path):
    content = """
# Database
DB_HOST=
DB_PORT=
DB_NAME=

# Auth
SECRET_KEY=
DEBUG=
"""
    p = tmp_path / ".env.template"
    p.write_text(content)
    return p


def test_parse_template_returns_keys(template_file):
    keys = parse_template(template_file)
    assert keys == ["DB_HOST", "DB_PORT", "DB_NAME", "SECRET_KEY", "DEBUG"]


def test_parse_template_ignores_comments_and_blanks(tmp_path):
    p = tmp_path / "t.template"
    p.write_text("# comment\n\nFOO=\nBAR=baz\n")
    assert parse_template(p) == ["FOO", "BAR"]


def test_parse_template_ignores_lines_without_equals(tmp_path):
    p = tmp_path / "t.template"
    p.write_text("JUST_A_WORD\nFOO=\n")
    assert parse_template(p) == ["FOO"]


def test_check_all_present():
    result = check_profile_against_template(
        {"FOO": "1", "BAR": "2"}, ["FOO", "BAR"]
    )
    assert result.ok
    assert result.missing == []
    assert result.extra == []


def test_check_missing_keys():
    result = check_profile_against_template({"FOO": "1"}, ["FOO", "BAR"])
    assert not result.ok
    assert result.missing == ["BAR"]


def test_check_extra_keys():
    result = check_profile_against_template(
        {"FOO": "1", "BAR": "2", "EXTRA": "x"}, ["FOO", "BAR"]
    )
    assert result.ok  # extra keys don't make it fail
    assert result.extra == ["EXTRA"]


def test_str_output_missing():
    result = TemplateCheckResult(missing=["SECRET_KEY"], extra=[])
    out = str(result)
    assert "Missing keys" in out
    assert "SECRET_KEY" in out


def test_str_output_ok():
    result = TemplateCheckResult()
    assert str(result) == "Profile satisfies template."

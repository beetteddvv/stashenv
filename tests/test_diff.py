import pytest
from stashenv.diff import diff_envs, format_diff, DiffEntry


OLD = {"FOO": "bar", "KEEP": "same", "GONE": "bye"}
NEW = {"FOO": "baz", "KEEP": "same", "ADDED": "hello"}


def test_detects_added():
    entries = diff_envs(OLD, NEW)
    added = [e for e in entries if e.status == "added"]
    assert len(added) == 1
    assert added[0].key == "ADDED"
    assert added[0].new_value == "hello"


def test_detects_removed():
    entries = diff_envs(OLD, NEW)
    removed = [e for e in entries if e.status == "removed"]
    assert len(removed) == 1
    assert removed[0].key == "GONE"
    assert removed[0].old_value == "bye"


def test_detects_changed():
    entries = diff_envs(OLD, NEW)
    changed = [e for e in entries if e.status == "changed"]
    assert len(changed) == 1
    assert changed[0].key == "FOO"
    assert changed[0].old_value == "bar"
    assert changed[0].new_value == "baz"


def test_unchanged_hidden_by_default():
    entries = diff_envs(OLD, NEW)
    unchanged = [e for e in entries if e.status == "unchanged"]
    assert unchanged == []


def test_show_unchanged():
    entries = diff_envs(OLD, NEW, show_unchanged=True)
    unchanged = [e for e in entries if e.status == "unchanged"]
    assert len(unchanged) == 1
    assert unchanged[0].key == "KEEP"


def test_identical_envs_returns_empty():
    entries = diff_envs(OLD, OLD)
    assert entries == []


def test_format_diff_no_diff():
    result = format_diff([])
    assert result == "(no differences)"


def test_format_diff_output():
    entries = diff_envs(OLD, NEW)
    output = format_diff(entries)
    assert "+ ADDED=hello" in output
    assert "- GONE=bye" in output
    assert "~ FOO" in output


def test_str_representations():
    assert str(DiffEntry("K", "added", new_value="v")) == "+ K=v"
    assert str(DiffEntry("K", "removed", old_value="v")) == "- K=v"
    assert str(DiffEntry("K", "changed", old_value="a", new_value="b")) == "~ K: 'a' -> 'b'"
    assert str(DiffEntry("K", "unchanged", new_value="v")) == "  K=v"

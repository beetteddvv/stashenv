import pytest
from stashenv.audit import record, read_log, clear_log, format_log


@pytest.fixture(autouse=True)
def clean_log(tmp_path, monkeypatch):
    monkeypatch.setenv("USER", "tester")
    # redirect stash dir to tmp
    import stashenv.audit as audit_mod
    monkeypatch.setattr(audit_mod, "_audit_path",
        lambda project: tmp_path / project / "audit.log")
    # ensure parent exists
    (tmp_path / "myproject").mkdir(parents=True, exist_ok=True)
    yield


PROJECT = "myproject"


def test_record_creates_entry():
    record(PROJECT, "save", "prod")
    entries = read_log(PROJECT)
    assert len(entries) == 1
    assert entries[0]["action"] == "save"
    assert entries[0]["profile"] == "prod"
    assert entries[0]["user"] == "tester"


def test_multiple_records_ordered():
    record(PROJECT, "save", "dev")
    record(PROJECT, "load", "dev")
    record(PROJECT, "delete", "dev")
    entries = read_log(PROJECT)
    assert [e["action"] for e in entries] == ["save", "load", "delete"]


def test_detail_field():
    record(PROJECT, "copy", "staging", detail="copied from prod")
    entries = read_log(PROJECT)
    assert entries[0]["detail"] == "copied from prod"


def test_clear_log():
    record(PROJECT, "save", "prod")
    clear_log(PROJECT)
    assert read_log(PROJECT) == []


def test_read_empty_project_returns_empty(tmp_path, monkeypatch):
    import stashenv.audit as audit_mod
    monkeypatch.setattr(audit_mod, "_audit_path",
        lambda project: tmp_path / project / "audit.log")
    assert read_log("nonexistent") == []


def test_format_log_no_entries():
    assert format_log([]) == "(no audit entries)"


def test_format_log_contains_action():
    record(PROJECT, "load", "prod")
    entries = read_log(PROJECT)
    output = format_log(entries)
    assert "load" in output
    assert "prod" in output

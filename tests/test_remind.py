"""Tests for stashenv.remind"""

import pytest
from stashenv.remind import (
    set_reminder,
    get_reminder,
    clear_reminder,
    list_reminders,
    _reminders_path,
)


PROJECT = "__test_remind_project__"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    p = _reminders_path(PROJECT)
    if p.exists():
        p.unlink()


def test_set_and_get_reminder():
    set_reminder(PROJECT, "dev", "Remember to rotate keys!")
    entry = get_reminder(PROJECT, "dev")
    assert entry is not None
    assert entry["message"] == "Remember to rotate keys!"
    assert "created_at" in entry


def test_get_missing_reminder_returns_none():
    result = get_reminder(PROJECT, "nonexistent")
    assert result is None


def test_set_overwrites_existing_reminder():
    set_reminder(PROJECT, "dev", "First note")
    set_reminder(PROJECT, "dev", "Updated note")
    entry = get_reminder(PROJECT, "dev")
    assert entry["message"] == "Updated note"


def test_clear_reminder_returns_true_when_existed():
    set_reminder(PROJECT, "staging", "Check DB creds")
    result = clear_reminder(PROJECT, "staging")
    assert result is True
    assert get_reminder(PROJECT, "staging") is None


def test_clear_reminder_returns_false_when_missing():
    result = clear_reminder(PROJECT, "ghost")
    assert result is False


def test_list_reminders_empty():
    assert list_reminders(PROJECT) == {}


def test_list_reminders_multiple():
    set_reminder(PROJECT, "dev", "Note A")
    set_reminder(PROJECT, "prod", "Note B")
    reminders = list_reminders(PROJECT)
    assert "dev" in reminders
    assert "prod" in reminders
    assert reminders["dev"]["message"] == "Note A"
    assert reminders["prod"]["message"] == "Note B"

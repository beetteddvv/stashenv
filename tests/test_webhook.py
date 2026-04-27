"""Tests for stashenv.webhook module."""

from __future__ import annotations

import json
from unittest.mock import patch, MagicMock
import pytest

from stashenv.webhook import (
    set_webhook,
    get_webhook,
    remove_webhook,
    list_webhooks,
    fire_webhook,
)


PROJECT = "test-webhook-project"


@pytest.fixture(autouse=True)
def cleanup(tmp_path, monkeypatch):
    from stashenv import store
    monkeypatch.setattr(store, "_stash_dir", lambda p: tmp_path / p)
    yield


def test_set_and_get_webhook():
    set_webhook(PROJECT, "profile.load", "https://example.com/hook")
    entry = get_webhook(PROJECT, "profile.load")
    assert entry is not None
    assert entry["url"] == "https://example.com/hook"
    assert "registered_at" in entry


def test_get_missing_webhook_returns_none():
    result = get_webhook(PROJECT, "nonexistent.event")
    assert result is None


def test_set_overwrites_existing():
    set_webhook(PROJECT, "profile.save", "https://old.example.com")
    set_webhook(PROJECT, "profile.save", "https://new.example.com")
    entry = get_webhook(PROJECT, "profile.save")
    assert entry["url"] == "https://new.example.com"


def test_remove_webhook_returns_true_when_existed():
    set_webhook(PROJECT, "profile.delete", "https://example.com/del")
    result = remove_webhook(PROJECT, "profile.delete")
    assert result is True
    assert get_webhook(PROJECT, "profile.delete") is None


def test_remove_webhook_returns_false_when_missing():
    result = remove_webhook(PROJECT, "ghost.event")
    assert result is False


def test_list_webhooks_returns_all():
    set_webhook(PROJECT, "event.a", "https://a.example.com")
    set_webhook(PROJECT, "event.b", "https://b.example.com")
    hooks = list_webhooks(PROJECT)
    assert "event.a" in hooks
    assert "event.b" in hooks


def test_list_webhooks_empty_project():
    hooks = list_webhooks("empty-project-xyz")
    assert hooks == {}


def test_fire_webhook_returns_false_when_not_set():
    result = fire_webhook(PROJECT, "no.such.event", {})
    assert result is False


def test_fire_webhook_calls_url():
    set_webhook(PROJECT, "profile.load", "https://example.com/hook")
    mock_response = MagicMock()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_response) as mock_open:
        result = fire_webhook(PROJECT, "profile.load", {"profile": "dev"})
    assert result is True
    mock_open.assert_called_once()


def test_fire_webhook_returns_false_on_error():
    set_webhook(PROJECT, "profile.load", "https://example.com/hook")
    with patch("urllib.request.urlopen", side_effect=OSError("connection refused")):
        result = fire_webhook(PROJECT, "profile.load", {})
    assert result is False

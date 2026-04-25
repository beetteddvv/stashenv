"""Tests for stashenv.env_status."""

import pytest
from pathlib import Path
from unittest.mock import patch

from stashenv.env_status import get_status, EnvStatus

PROJECT = "status-test-proj"


@pytest.fixture(autouse=True)
def _clean(tmp_path):
    """Patch stash dir and cwd for isolation."""
    with patch("stashenv.store._stash_dir", return_value=tmp_path / "stash"):
        with patch("stashenv.pin._pin_path", return_value=tmp_path / "pin.json"):
            with patch("stashenv.history._history_path", return_value=tmp_path / "history.json"):
                with patch("stashenv.lock._lock_path", return_value=tmp_path / "locks.json"):
                    with patch("stashenv.expire._expiry_path", return_value=tmp_path / "expiry.json"):
                        yield tmp_path


def test_status_no_profiles(_clean):
    s = get_status(PROJECT, cwd=_clean)
    assert s.total_profiles == 0
    assert s.pinned_profile is None
    assert s.last_loaded_profile is None
    assert s.dotenv_present is False


def test_status_dotenv_detected(_clean):
    dotenv = _clean / ".env"
    dotenv.write_text("KEY=val")
    s = get_status(PROJECT, cwd=_clean)
    assert s.dotenv_present is True


def test_status_str_contains_project(_clean):
    s = get_status(PROJECT, cwd=_clean)
    output = str(s)
    assert PROJECT in output
    assert "Profiles" in output
    assert "Pinned" in output


def test_status_locked_profiles_listed(_clean):
    from stashenv.store import save_profile
    from stashenv.lock import lock_profile

    save_profile(PROJECT, "dev", {"X": "1"}, "pw")
    lock_profile(PROJECT, "dev")
    s = get_status(PROJECT, cwd=_clean)
    assert "dev" in s.locked_profiles


def test_status_expired_profiles_listed(_clean):
    from stashenv.store import save_profile
    from stashenv.expire import set_expiry
    from datetime import timedelta

    save_profile(PROJECT, "old", {"Y": "2"}, "pw")
    set_expiry(PROJECT, "old", timedelta(seconds=-1))  # already expired
    s = get_status(PROJECT, cwd=_clean)
    assert "old" in s.expired_profiles


def test_status_pinned_shown(_clean):
    from stashenv.store import save_profile
    from stashenv.pin import pin_profile

    save_profile(PROJECT, "prod", {"Z": "3"}, "pw")
    pin_profile(PROJECT, "prod")
    s = get_status(PROJECT, cwd=_clean)
    assert s.pinned_profile == "prod"

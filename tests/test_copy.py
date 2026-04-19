import pytest
from stashenv.copy import copy_profile, rename_profile
from stashenv.store import list_profiles, load_profile, delete_profile


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path))
    return "myproject"


ENV = {"FOO": "bar", "BAZ": "qux"}
PASSWORD = "secret"


def _seed(project):
    from stashenv.store import save_profile
    save_profile(project, "dev", ENV, PASSWORD)


def test_copy_creates_dst(project):
    _seed(project)
    copy_profile(project, "dev", "staging", PASSWORD)
    assert "staging" in list_profiles(project)
    assert "dev" in list_profiles(project)


def test_copy_preserves_data(project):
    _seed(project)
    copy_profile(project, "dev", "staging", PASSWORD)
    loaded = load_profile(project, "staging", PASSWORD)
    assert loaded == ENV


def test_copy_missing_src_raises(project):
    with pytest.raises(KeyError, match="nope"):
        copy_profile(project, "nope", "dst", PASSWORD)


def test_copy_existing_dst_raises(project):
    _seed(project)
    from stashenv.store import save_profile
    save_profile(project, "staging", ENV, PASSWORD)
    with pytest.raises(ValueError, match="already exists"):
        copy_profile(project, "dev", "staging", PASSWORD)


def test_rename_removes_src(project):
    _seed(project)
    rename_profile(project, "dev", "production", PASSWORD)
    assert "dev" not in list_profiles(project)
    assert "production" in list_profiles(project)


def test_rename_preserves_data(project):
    _seed(project)
    rename_profile(project, "dev", "production", PASSWORD)
    loaded = load_profile(project, "production", PASSWORD)
    assert loaded == ENV

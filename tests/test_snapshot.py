import pytest
from stashenv.snapshot import create_snapshot, restore_snapshot, list_snapshots, delete_snapshot
from stashenv.store import save_profile, load_profile

PROJECT = "snap_test_project"
PASSWORD = "s3cr3t"


@pytest.fixture(autouse=True)
def cleanup(tmp_path, monkeypatch):
    import stashenv.store as st
    import stashenv.snapshot as sn
    monkeypatch.setattr(st, "_stash_dir", lambda p: tmp_path / p)
    monkeypatch.setattr(sn, "_stash_dir", lambda p: tmp_path / p)
    monkeypatch.setattr(sn, "save_profile", st.save_profile)
    monkeypatch.setattr(sn, "load_profile", st.load_profile)
    yield


def test_create_snapshot_returns_name(tmp_path, monkeypatch):
    import stashenv.store as st
    save_profile(PROJECT, "prod", "KEY=val", PASSWORD)
    name = create_snapshot(PROJECT, "prod", PASSWORD, label="backup1")
    assert name == "backup1"


def test_restore_snapshot(tmp_path, monkeypatch):
    import stashenv.store as st
    save_profile(PROJECT, "prod", "KEY=original", PASSWORD)
    create_snapshot(PROJECT, "prod", PASSWORD, label="snap1")
    save_profile(PROJECT, "prod", "KEY=changed", PASSWORD)
    restore_snapshot(PROJECT, "snap1", "prod", PASSWORD)
    restored = load_profile(PROJECT, "prod", PASSWORD)
    assert "KEY=original" in restored


def test_list_snapshots_includes_created(tmp_path, monkeypatch):
    import stashenv.store as st
    save_profile(PROJECT, "dev", "A=1", PASSWORD)
    create_snapshot(PROJECT, "dev", PASSWORD, label="mysnap")
    snaps = list_snapshots(PROJECT)
    names = [s["snap_name"] for s in snaps]
    assert "mysnap" in names


def test_delete_snapshot(tmp_path, monkeypatch):
    import stashenv.store as st
    save_profile(PROJECT, "dev", "A=1", PASSWORD)
    create_snapshot(PROJECT, "dev", PASSWORD, label="todel")
    delete_snapshot(PROJECT, "todel")
    snaps = list_snapshots(PROJECT)
    names = [s["snap_name"] for s in snaps]
    assert "todel" not in names


def test_delete_missing_snapshot_raises(tmp_path, monkeypatch):
    with pytest.raises(FileNotFoundError):
        delete_snapshot(PROJECT, "ghost")

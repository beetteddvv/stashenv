import pytest
from click.testing import CliRunner
from stashenv.cli_snapshot import snapshot
from stashenv.store import save_profile

PROJECT = "cli_snap_project"
PASSWORD = "testpass"


@pytest.fixture(autouse=True)
def patch_stash(tmp_path, monkeypatch):
    import stashenv.store as st
    import stashenv.snapshot as sn
    monkeypatch.setattr(st, "_stash_dir", lambda p: tmp_path / p)
    monkeypatch.setattr(sn, "_stash_dir", lambda p: tmp_path / p)
    monkeypatch.setattr(sn, "save_profile", st.save_profile)
    monkeypatch.setattr(sn, "load_profile", st.load_profile)
    yield


def test_create_and_list(tmp_path, monkeypatch):
    import stashenv.store as st
    save_profile(PROJECT, "dev", "X=1", PASSWORD)
    runner = CliRunner()
    result = runner.invoke(snapshot, ["create", PROJECT, "dev", "--label", "snap1"], input=f"{PASSWORD}\n{PASSWORD}\n")
    assert result.exit_code == 0
    assert "snap1" in result.output
    result2 = runner.invoke(snapshot, ["list", PROJECT])
    assert "snap1" in result2.output


def test_delete_cmd(tmp_path, monkeypatch):
    import stashenv.store as st
    save_profile(PROJECT, "dev", "X=1", PASSWORD)
    runner = CliRunner()
    runner.invoke(snapshot, ["create", PROJECT, "dev", "--label", "todel"], input=f"{PASSWORD}\n{PASSWORD}\n")
    result = runner.invoke(snapshot, ["delete", PROJECT, "todel"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_missing(tmp_path):
    runner = CliRunner()
    result = runner.invoke(snapshot, ["delete", PROJECT, "ghost"])
    assert result.exit_code == 1

import pytest
from stashenv.merge import merge_envs, MergeStrategy, MergeConflict


BASE = {"A": "1", "B": "2", "C": "3"}
INCOMING = {"B": "99", "C": "3", "D": "4"}


def test_adds_new_keys():
    merged, _ = merge_envs(BASE, INCOMING)
    assert merged["D"] == "4"


def test_no_conflict_on_equal_values():
    merged, conflicts = merge_envs(BASE, INCOMING)
    assert "C" not in conflicts
    assert merged["C"] == "3"


def test_theirs_wins_on_conflict():
    merged, conflicts = merge_envs(BASE, INCOMING, MergeStrategy.THEIRS)
    assert "B" in conflicts
    assert merged["B"] == "99"


def test_ours_wins_on_conflict():
    merged, conflicts = merge_envs(BASE, INCOMING, MergeStrategy.OURS)
    assert "B" in conflicts
    assert merged["B"] == "2"


def test_prompt_raises_on_conflict():
    with pytest.raises(MergeConflict) as exc_info:
        merge_envs(BASE, INCOMING, MergeStrategy.PROMPT)
    err = exc_info.value
    assert err.key == "B"
    assert err.base_val == "2"
    assert err.incoming_val == "99"


def test_no_conflicts_when_disjoint():
    _, conflicts = merge_envs({"X": "1"}, {"Y": "2"})
    assert conflicts == []


def test_base_unchanged_keys_preserved():
    merged, _ = merge_envs(BASE, INCOMING)
    assert merged["A"] == "1"


def test_empty_incoming():
    merged, conflicts = merge_envs(BASE, {})
    assert merged == BASE
    assert conflicts == []


def test_empty_base():
    merged, conflicts = merge_envs({}, INCOMING)
    assert merged == INCOMING
    assert conflicts == []

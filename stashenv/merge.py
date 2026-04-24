"""Merge two profiles together, with optional conflict resolution strategies."""

from enum import Enum
from typing import Dict, List, Tuple


class MergeStrategy(str, Enum):
    OURS = "ours"      # keep base value on conflict
    THEIRS = "theirs"  # use incoming value on conflict
    PROMPT = "prompt"  # not handled here, caller must resolve


class MergeConflict(Exception):
    """Raised when a conflict is found and strategy is PROMPT."""

    def __init__(self, key: str, base_val: str, incoming_val: str):
        self.key = key
        self.base_val = base_val
        self.incoming_val = incoming_val
        super().__init__(f"Conflict on key '{key}': '{base_val}' vs '{incoming_val}'")


def merge_envs(
    base: Dict[str, str],
    incoming: Dict[str, str],
    strategy: MergeStrategy = MergeStrategy.THEIRS,
) -> Tuple[Dict[str, str], List[str]]:
    """
    Merge incoming into base.

    Returns:
        (merged_dict, list_of_conflict_keys)
    """
    merged = dict(base)
    conflicts = []

    for key, value in incoming.items():
        if key not in merged:
            merged[key] = value
        elif merged[key] == value:
            pass  # no conflict
        else:
            conflicts.append(key)
            if strategy == MergeStrategy.THEIRS:
                merged[key] = value
            elif strategy == MergeStrategy.OURS:
                pass  # keep base
            elif strategy == MergeStrategy.PROMPT:
                raise MergeConflict(key, merged[key], value)

    return merged, conflicts


def diff_envs(
    base: Dict[str, str],
    incoming: Dict[str, str],
) -> Dict[str, Tuple[str | None, str | None]]:
    """
    Return a diff of two env dicts.

    Returns a dict mapping each changed key to a (base_value, incoming_value) tuple.
    A value of None means the key is absent in that side.
    """
    all_keys = set(base) | set(incoming)
    return {
        key: (base.get(key), incoming.get(key))
        for key in all_keys
        if base.get(key) != incoming.get(key)
    }

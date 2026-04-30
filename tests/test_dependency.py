"""Tests for stashenv.dependency."""

import pytest

from stashenv.dependency import (
    add_dependency,
    clear_dependencies,
    get_dependencies,
    get_dependents,
    remove_dependency,
    resolve_order,
)

PROJECT = "test_dep_project"


@pytest.fixture(autouse=True)
def cleanup():
    from stashenv.dependency import _deps_path

    yield
    p = _deps_path(PROJECT)
    if p.exists():
        p.unlink()


def test_add_and_get_dependency():
    add_dependency(PROJECT, "prod", "base")
    assert "base" in get_dependencies(PROJECT, "prod")


def test_add_is_idempotent():
    add_dependency(PROJECT, "prod", "base")
    add_dependency(PROJECT, "prod", "base")
    assert get_dependencies(PROJECT, "prod").count("base") == 1


def test_add_multiple_dependencies():
    add_dependency(PROJECT, "prod", "base")
    add_dependency(PROJECT, "prod", "secrets")
    deps = get_dependencies(PROJECT, "prod")
    assert "base" in deps
    assert "secrets" in deps


def test_self_dependency_raises():
    with pytest.raises(ValueError, match="cannot depend on itself"):
        add_dependency(PROJECT, "prod", "prod")


def test_remove_dependency_returns_true_when_existed():
    add_dependency(PROJECT, "prod", "base")
    assert remove_dependency(PROJECT, "prod", "base") is True
    assert "base" not in get_dependencies(PROJECT, "prod")


def test_remove_dependency_returns_false_when_missing():
    assert remove_dependency(PROJECT, "prod", "ghost") is False


def test_get_dependents():
    add_dependency(PROJECT, "prod", "base")
    add_dependency(PROJECT, "staging", "base")
    dependents = get_dependents(PROJECT, "base")
    assert "prod" in dependents
    assert "staging" in dependents


def test_clear_dependencies():
    add_dependency(PROJECT, "prod", "base")
    clear_dependencies(PROJECT, "prod")
    assert get_dependencies(PROJECT, "prod") == []


def test_resolve_order_simple():
    add_dependency(PROJECT, "prod", "base")
    order = resolve_order(PROJECT, "prod")
    assert order.index("base") < order.index("prod")


def test_resolve_order_chain():
    add_dependency(PROJECT, "c", "b")
    add_dependency(PROJECT, "b", "a")
    order = resolve_order(PROJECT, "c")
    assert order == ["a", "b", "c"]


def test_resolve_order_detects_cycle():
    add_dependency(PROJECT, "a", "b")
    add_dependency(PROJECT, "b", "a")
    with pytest.raises(ValueError, match="Circular dependency"):
        resolve_order(PROJECT, "a")

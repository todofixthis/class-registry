"""
Verifies registry behaviour when :py:func:`class_registry.ClassRegistry.gen_lookup_key`
is modified.
"""

import typing

import pytest

from class_registry import ClassRegistry
from test import Charmander, Pokemon, Squirtle


@pytest.fixture(name="customised_registry")
def fixture_customised_registry() -> ClassRegistry[Pokemon]:
    class CustomisedLookupRegistry(ClassRegistry[Pokemon]):
        @staticmethod
        def gen_lookup_key(key: typing.Hashable) -> typing.Hashable:
            """
            Simple override of `gen_lookup_key`, to ensure the registry
            behaves as expected when the lookup key is different.
            """
            if isinstance(key, str):
                return "".join(reversed(key))
            return key

    registry = CustomisedLookupRegistry()
    registry.register("fire")(Charmander)
    registry.register("water")(Squirtle)
    return registry


def test_contains(customised_registry: ClassRegistry[Pokemon]) -> None:
    assert "fire" in customised_registry
    assert "erif" not in customised_registry


def test_getitem(customised_registry: ClassRegistry[Pokemon]) -> None:
    assert isinstance(customised_registry["fire"], Charmander)


def test_iter(customised_registry: ClassRegistry[Pokemon]) -> None:
    generator = iter(customised_registry)

    assert next(generator) == "fire"
    assert next(generator) == "water"

    with pytest.raises(StopIteration):
        next(generator)


def test_len(customised_registry: ClassRegistry[Pokemon]) -> None:
    assert len(customised_registry) == 2


def test_get_class(customised_registry: ClassRegistry[Pokemon]) -> None:
    assert customised_registry.get_class("fire") is Charmander


def test_get(customised_registry: ClassRegistry[Pokemon]) -> None:
    assert isinstance(customised_registry.get("fire"), Charmander)


def test_unregister(customised_registry: ClassRegistry[Pokemon]) -> None:
    customised_registry.unregister("fire")

    assert "fire" not in customised_registry
    assert "erif" not in customised_registry


def test_use_case_aliases() -> None:
    """
    A common use case for overriding `gen_lookup_key` is to specify some
    aliases (e.g., for backwards-compatibility when refactoring an existing
    registry).
    """

    class TestRegistry(ClassRegistry[Pokemon]):
        @staticmethod
        def gen_lookup_key(key: typing.Hashable) -> typing.Hashable:
            """
            Simulate a scenario where we renamed the key for a class in the
            registry, but we want to preserve backwards-compatibility with
            existing code that hasn't been updated yet.
            """
            if key == "bird":
                return "flying"

            return key

    registry = TestRegistry()

    @registry.register("flying")
    class MissingNo(Pokemon):
        pass

    assert isinstance(registry["bird"], MissingNo)
    assert isinstance(registry["flying"], MissingNo)

    assert "bird" in registry
    assert "flying" in registry

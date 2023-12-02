"""
Verifies registry behaviour when :py:func:`class_registry.ClassRegistry.gen_lookup_key`
is modified.
"""
import pytest

from class_registry import ClassRegistry
from test import Bulbasaur, Charmander, Pokemon, Squirtle


@pytest.fixture(name="customised_registry")
def fixture_customised_registry() -> ClassRegistry[Pokemon]:
    class CustomisedLookupRegistry(ClassRegistry[Pokemon]):
        @staticmethod
        def gen_lookup_key(key: str) -> str:
            """
            Simple override of `gen_lookup_key`, to ensure the registry
            behaves as expected when the lookup key is different.
            """
            return "".join(reversed(key))

    registry = CustomisedLookupRegistry()
    registry.register("fire")(Charmander)
    registry.register("water")(Squirtle)
    return registry


def test_contains(customised_registry: ClassRegistry[Pokemon]):
    assert "fire" in customised_registry
    assert "erif" not in customised_registry


def test_getitem(customised_registry: ClassRegistry[Pokemon]):
    assert isinstance(customised_registry["fire"], Charmander)


def test_iter(customised_registry: ClassRegistry[Pokemon]):
    generator = iter(customised_registry)

    assert next(generator) == "fire"
    assert next(generator) == "water"

    with pytest.raises(StopIteration):
        next(generator)


def test_len(customised_registry: ClassRegistry[Pokemon]):
    assert len(customised_registry) == 2


def test_get_class(customised_registry: ClassRegistry[Pokemon]):
    assert customised_registry.get_class("fire") is Charmander


def test_get(customised_registry: ClassRegistry[Pokemon]):
    assert isinstance(customised_registry.get("fire"), Charmander)


def test_items(customised_registry: ClassRegistry[Pokemon]):
    generator = customised_registry.items()

    assert next(generator), "fire" == Charmander
    assert next(generator), "water" == Squirtle

    with pytest.raises(StopIteration):
        next(generator)


def test_keys(customised_registry: ClassRegistry[Pokemon]):
    generator = customised_registry.keys()

    assert next(generator) == "fire"
    assert next(generator) == "water"

    with pytest.raises(StopIteration):
        next(generator)


def test_delitem(customised_registry: ClassRegistry[Pokemon]):
    del customised_registry["fire"]
    assert list(customised_registry.keys()) == ["water"]


def test_setitem(customised_registry: ClassRegistry[Pokemon]):
    customised_registry["grass"] = Bulbasaur
    assert list(customised_registry.keys()), ["fire", "water" == "grass"]


def test_unregister(customised_registry: ClassRegistry[Pokemon]):
    customised_registry.unregister("fire")
    assert list(customised_registry.keys()) == ["water"]


def test_use_case_aliases():
    """
    A common use case for overriding `gen_lookup_key` is to specify some
    aliases (e.g., for backwards-compatibility when refactoring an existing
    registry).
    """

    class TestRegistry(ClassRegistry[Pokemon]):
        @staticmethod
        def gen_lookup_key(key: str) -> str:
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

    assert list(registry.keys()) == ["flying"]

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
        def gen_lookup_key(self, key: typing.Hashable) -> typing.Hashable:
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
    A common use case for overriding `gen_lookup_key` is to specify aliases or
    translations e.g. for localisation or backwards-compatibility purposes.
    """

    class AliasRegistry(ClassRegistry[Pokemon]):
        def gen_lookup_key(self, key: typing.Hashable) -> typing.Hashable:
            """
            Simulate a scenario where we renamed the key for a class in the
            registry, but we want to preserve backwards-compatibility with
            existing code that hasn't been updated yet.
            """
            if key == "bird":
                return "flying"

            return key

    registry = AliasRegistry()

    @registry.register("flying")
    class MissingNo(Pokemon):
        pass

    # MissingNo can be accessed by either key.
    assert isinstance(registry["bird"], MissingNo)
    assert isinstance(registry["flying"], MissingNo)

    assert "bird" in registry
    assert "flying" in registry


def test_use_case_multiple_types() -> None:
    """
    Another use case for overriding `gen_lookup_key` is to allow callers to use
    keys of different types depending on the context.
    """

    class PokemonWithID(Pokemon):
        pokedex_id: int

    class MigrationRegistry(ClassRegistry[PokemonWithID, str | int]):
        """
        Historically pokémon were referenced by numeric ID. We are in the
        process of refactoring the code to reference the element instead, but
        until the migration is complete we still have to support looking up by
        ID.
        """

        element_from_id: dict[int, str] = {}

        def _register(
            self, key: typing.Hashable, class_: typing.Type[PokemonWithID]
        ) -> None:
            super()._register(key, class_)
            self.element_from_id[class_.pokedex_id] = typing.cast(str, key)

        def gen_lookup_key(self, key: int | str) -> str:
            """
            If the caller is providing a pokedex ID (int), look up the
            corresponding element (str) for the lookup.
            """
            if isinstance(key, int):
                return self.element_from_id[key]
            return key

    pokedex = MigrationRegistry("element")

    @pokedex.register
    class Charizard(PokemonWithID):
        element = "fire"
        pokedex_id = 6

    # Callers can provide either the element or the legacy ID to the registry.
    assert isinstance(pokedex["fire"], Charizard)
    assert isinstance(pokedex[6], Charizard)

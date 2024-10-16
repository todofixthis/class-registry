import typing
from importlib.metadata import entry_points

import pytest

from class_registry import RegistryKeyError
from class_registry.entry_points import EntryPointClassRegistry
from test import Bulbasaur, Charmander, Mew, Pokemon, PokemonFactory, Squirtle
from test.helper import DummyDistributionFinder


@pytest.fixture(name="distro", autouse=True)
def fixture_distro() -> typing.Generator[None, None, None]:
    # Inject a distribution that defines some entry points.
    DummyDistributionFinder.install()
    yield
    DummyDistributionFinder.uninstall()


def test_happy_path() -> None:
    """
    Loading classes automatically via entry points.

    See ``dummy_package.egg-info/entry_points.txt`` for more info.
    """
    registry = EntryPointClassRegistry[Pokemon]("pokemon")

    fire = registry["fire"]
    assert isinstance(fire, Charmander)
    assert fire.name is None

    grass = registry.get("grass")
    assert isinstance(grass, Bulbasaur)
    assert grass.name is None

    water = registry.get("water", name="archibald")
    assert isinstance(water, Squirtle)
    assert water.name == "archibald"

    # The 'psychic' entry point actually references a function, but it
    # works exactly the same as a class.
    psychic = registry.get("psychic", "snuggles")
    assert isinstance(psychic, Mew)
    assert psychic.name == "snuggles"


def test_branding() -> None:
    """
    Configuring the registry to "brand" each class/instance with its
    corresponding key.
    """
    registry = EntryPointClassRegistry[Pokemon]("pokemon", attr_name="poke_type")
    try:
        # Branding is applied immediately to each registered class.
        assert getattr(Charmander, "poke_type") == "fire"
        assert getattr(Squirtle, "poke_type") == "water"

        # Instances, too!
        assert getattr(registry["fire"], "poke_type") == "fire"
        assert getattr(registry.get("water", "phil"), "poke_type") == "water"

        # Registered functions and methods can't be branded this way,
        # though...
        assert not hasattr(PokemonFactory.create_psychic_pokemon, "poke_type")

        # ... but we can brand the resulting instances.
        assert getattr(registry["psychic"], "poke_type") == "psychic"
        assert getattr(registry.get("psychic"), "poke_type") == "psychic"
    finally:
        # Clean up after ourselves.
        for cls in registry.classes():
            if isinstance(cls, type):
                try:
                    delattr(cls, "poke_type")
                except AttributeError:
                    pass


def test_len() -> None:
    """
    Getting the length of an entry point class registry.
    """
    # Just in case some other package defines pokémon entry
    # points (:
    expected = len(list(entry_points(group="pokemon")))

    # Quick sanity check, to make sure our test pokémon are
    # registered correctly.
    assert expected >= 4

    registry = EntryPointClassRegistry[Pokemon]("pokemon")
    assert len(registry) == expected


def test_error_wrong_group() -> None:
    """
    The registry can't find entry points associated with the wrong group.
    """
    registry = EntryPointClassRegistry[Pokemon]("fhqwhgads")

    with pytest.raises(RegistryKeyError):
        registry.get("fire")

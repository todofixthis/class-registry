import typing

import pytest

from class_registry import ClassRegistry
from class_registry.cache import ClassRegistryInstanceCache
from test import Bulbasaur, Charmander, Pokemon, Squirtle


@pytest.fixture(name="registry")
def fixture_registry() -> ClassRegistry[Pokemon]:
    registry = ClassRegistry[Pokemon](attr_name="element")
    registry.register(Bulbasaur)
    registry.register(Charmander)
    registry.register(Squirtle)
    return registry


@pytest.fixture(name="cache")
def fixture_cache(
    registry: ClassRegistry[Pokemon],
) -> ClassRegistryInstanceCache[Pokemon]:
    return ClassRegistryInstanceCache[Pokemon](registry)


def test_get(
    cache: ClassRegistryInstanceCache[Pokemon],
    registry: ClassRegistry[Pokemon],
) -> None:
    """
    When an instance is returned from
    :py:meth:`ClassRegistryInstanceCache.get`, future invocations return
    the same instance.
    """
    poke_1 = cache["grass"]
    assert isinstance(poke_1, Bulbasaur)

    # Same key = exact same instance.
    poke_2 = cache["grass"]
    assert poke_2 is poke_1

    poke_3 = cache["water"]
    assert isinstance(poke_3, Squirtle)

    # If we pull a class directly from the wrapped registry, we get
    # a new instance.
    poke_4 = registry["water"]
    assert isinstance(poke_4, Squirtle)
    assert poke_3 is not poke_4


def test_template_args(registry: ClassRegistry[Pokemon]) -> None:
    """
    Extra params passed to the cache constructor are passed to the template
    function when creating new instances.
    """
    # Add an extra init param to the cache.
    cache = ClassRegistryInstanceCache(registry, name="Bruce")

    # The cache parameters are automatically applied to the class'
    # initializer.
    poke_1 = cache["fire"]
    assert isinstance(poke_1, Charmander)
    assert poke_1.name == "Bruce"

    poke_2 = cache["water"]
    assert isinstance(poke_2, Squirtle)
    assert poke_2.name == "Bruce"


def test_len(
    cache: ClassRegistryInstanceCache[Pokemon],
    registry: ClassRegistry[Pokemon],
) -> None:
    """
    Checking the length of a cache.
    """
    # The length only reflects the number of cached instances.
    assert len(cache) == 0

    # Calling ``__getitem__`` directly to sneak past the linter (:
    cache.__getitem__("water")
    cache.__getitem__("grass")

    assert len(cache) == 2


def test_iter_with_customised_lookup_key() -> None:
    """
    Iterating over a cache still yields cached instances when the wrapped
    registry overrides ``gen_lookup_key`` with a non-identity function.
    """

    class FoldingRegistry(ClassRegistry[Pokemon]):
        def gen_lookup_key(self, key: typing.Hashable) -> typing.Hashable:
            return key.casefold() if isinstance(key, str) else key

    registry = FoldingRegistry()
    registry.register("Grass")(Bulbasaur)
    registry.register("Water")(Squirtle)

    cache = ClassRegistryInstanceCache[Pokemon](registry)
    cache.__getitem__("Grass")
    cache.__getitem__("Water")

    assert {type(instance) for instance in cache} == {Bulbasaur, Squirtle}

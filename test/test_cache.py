import pytest

from class_registry import ClassRegistry
from class_registry.cache import ClassRegistryInstanceCache
from test import Bulbasaur, Charmander, Charmeleon, Squirtle, Wartortle


@pytest.fixture(name="registry")
def fixture_registry() -> ClassRegistry:
    return ClassRegistry(attr_name="element")


@pytest.fixture(name="cache")
def fixture_cache(registry: ClassRegistry) -> ClassRegistryInstanceCache:
    return ClassRegistryInstanceCache(registry)


def test_get(cache: ClassRegistryInstanceCache, registry: ClassRegistry):
    """
    When an instance is returned from
    :py:meth:`ClassRegistryInstanceCache.get`, future invocations return
    the same instance.
    """
    # Register a few classes with the ClassRegistry.
    registry.register(Bulbasaur)
    registry.register(Charmander)
    registry.register(Squirtle)

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


def test_template_args(cache: ClassRegistryInstanceCache, registry: ClassRegistry):
    """
    Extra params passed to the cache constructor are passed to the template
    function when creating new instances.
    """
    registry.register(Charmeleon)
    registry.register(Wartortle)

    # Add an extra init param to the cache.
    cache = ClassRegistryInstanceCache(registry, name="Bruce")

    # The cache parameters are automatically applied to the class'
    # initializer.
    poke_1 = cache["fire"]
    assert isinstance(poke_1, Charmeleon)
    assert poke_1.name == "Bruce"

    poke_2 = cache["water"]
    assert isinstance(poke_2, Wartortle)
    assert poke_2.name == "Bruce"


def test_iterator(cache: ClassRegistryInstanceCache, registry: ClassRegistry):
    """
    Creating an iterator using :py:func:`iter`.
    """
    registry.register(Bulbasaur)
    registry.register(Charmander)
    registry.register(Squirtle)

    # The cache's iterator only operates over cached instances.
    assert list(iter(cache)) == []

    poke_1 = cache["water"]
    poke_2 = cache["grass"]
    poke_3 = cache["fire"]

    # The order that values are yielded depends on the ordering of
    # the wrapped registry.
    assert list(iter(cache)) == [poke_2, poke_3, poke_1]

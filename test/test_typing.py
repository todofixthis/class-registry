"""Type-level assertions for the optional generic key type (issue #100).

Validated by mypy (which runs over ``test``); ``typing.assert_type`` is a
runtime no-op, so each test also executes harmlessly under pytest. Every test
registers a concrete class so the lookups it asserts on succeed at runtime.
"""

import typing

from class_registry import ClassRegistry
from class_registry.base import BaseMutableRegistry
from class_registry.cache import ClassRegistryInstanceCache
from class_registry.entry_points import EntryPointClassRegistry
from class_registry.patcher import RegistryPatcher
from class_registry.registry import SortedClassRegistry


class Widget:
    pass


def test_class_registry_defaults_keys_to_str() -> None:
    registry: ClassRegistry[Widget] = ClassRegistry()

    @registry.register("custom")
    class Custom(Widget):
        pass

    typing.assert_type(registry["custom"], Widget)
    typing.assert_type(next(iter(registry.keys())), str)
    for key in registry:
        typing.assert_type(key, str)


def test_class_registry_accepts_explicit_key_type() -> None:
    registry: ClassRegistry[Widget, int] = ClassRegistry()

    @registry.register(42)
    class Custom(Widget):
        pass

    typing.assert_type(registry[42], Widget)
    typing.assert_type(next(iter(registry.keys())), int)


def test_sorted_class_registry_defaults_keys_to_str() -> None:
    registry: SortedClassRegistry[Widget] = SortedClassRegistry(sort_key="weight")

    @registry.register("a")
    class A(Widget):
        weight = 1

    typing.assert_type(next(iter(registry.keys())), str)


def test_entry_point_registry_keys_are_str() -> None:
    registry: EntryPointClassRegistry[Widget] = EntryPointClassRegistry("dummy.group")
    typing.assert_type(registry.keys(), typing.Iterable[str])


def test_instance_cache_infers_key_type_from_registry() -> None:
    registry: ClassRegistry[Widget, int] = ClassRegistry()

    @registry.register(7)
    class Seven(Widget):
        pass

    cache = ClassRegistryInstanceCache(registry)

    typing.assert_type(cache, ClassRegistryInstanceCache[Widget, int])
    typing.assert_type(cache.registry, ClassRegistry[Widget, int])
    typing.assert_type(cache[7], Widget)


def test_patcher_infers_key_type_from_registry() -> None:
    registry: ClassRegistry[Widget, int] = ClassRegistry(attr_name="key")

    patcher = RegistryPatcher(registry)

    typing.assert_type(patcher, RegistryPatcher[Widget, int])
    typing.assert_type(patcher.target, BaseMutableRegistry[Widget, int])

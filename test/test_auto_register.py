"""
Unit tests for :py:class:`class_registry.base.AutoRegister`, which replaces
:py:class:`class_registry.auto_register.AutoRegister` (the latter returns a metaclass,
whilst the former returns a base class).

:see: https://github.com/todofixthis/class-registry/issues/14
"""

from abc import ABC, abstractmethod as abstract_method

import pytest

from class_registry import ClassRegistry
from class_registry.base import AutoRegister
from test import Pokemon


def test_auto_register() -> None:
    """
    Using :py:func:`AutoRegister` to, well, auto-register classes.
    """
    registry = ClassRegistry["BasePokemon"](attr_name="element")

    # Note that we declare :py:func:`AutoRegister` as a base class.
    # Dynamic subclasses are not supported by mypy, so have to ignore type check here.
    # :see: https://github.com/python/mypy/wiki/Unsupported-Python-Features
    class BasePokemon(AutoRegister(registry), ABC):  # type: ignore
        """
        Abstract base class; will not get registered.
        """

        @abstract_method
        def get_abilities(self) -> list[str]:
            raise NotImplementedError()

    class Sandslash(BasePokemon):
        """
        Non-abstract subclass; will get registered automatically.
        """

        element = "ground"

        def get_abilities(self) -> list[str]:
            return ["sand veil"]

    class BaseEvolvingPokemon(BasePokemon, ABC):
        """
        Abstract subclass; will not get registered.
        """

        @abstract_method
        def evolve(self) -> str:
            raise NotImplementedError()

    class Ekans(BaseEvolvingPokemon):
        """
        Non-abstract subclass; will get registered automatically.
        """

        element = "poison"

        def get_abilities(self) -> list[str]:
            return ["intimidate", "shed skin"]

        def evolve(self) -> str:
            return "Congratulations! Your EKANS evolved into ARBOK!"

    # Note that only non-abstract classes got registered.
    assert list(registry.classes()) == [Sandslash, Ekans]


def test_abstract_strict_definition() -> None:
    """
    If a class has no unimplemented abstract methods, it gets registered.
    """
    registry = ClassRegistry["FightingPokemon"](attr_name="element")

    # Dynamic subclasses are not supported by mypy, so have to ignore type check here.
    # :see: https://github.com/python/mypy/wiki/Unsupported-Python-Features
    class FightingPokemon(AutoRegister(registry)):  # type: ignore
        element = "fighting"

    # :py:class:`FightingPokemon` does not define any abstract methods, so it is not
    # considered to be abstract :shrug:
    assert list(registry.classes()) == [FightingPokemon]


def test_error_attr_name_missing() -> None:
    """
    The registry doesn't have an ``attr_name``.
    """
    registry = ClassRegistry[Pokemon]()

    with pytest.raises(ValueError):
        AutoRegister(registry)

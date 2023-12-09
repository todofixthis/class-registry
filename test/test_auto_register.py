from abc import ABCMeta, abstractmethod as abstract_method

import pytest

from class_registry import ClassRegistry
from class_registry.auto_register import AutoRegister


def test_auto_register():
    """
    Using :py:func:`AutoRegister` to, well, auto-register classes.
    """
    registry = ClassRegistry["BasePokemon"](attr_name="element")

    # Note that we declare :py:func:`AutoRegister` as the metaclass
    # for our base class.
    class BasePokemon(metaclass=AutoRegister(registry)):
        """
        Abstract base class; will not get registered.
        """

        @abstract_method
        def get_abilities(self):
            raise NotImplementedError()

    class Sandslash(BasePokemon):
        """
        Non-abstract subclass; will get registered automatically.
        """

        element = "ground"

        def get_abilities(self):
            return ["sand veil"]

    class BaseEvolvingPokemon(BasePokemon, metaclass=ABCMeta):
        """
        Abstract subclass; will not get registered.
        """

        @abstract_method
        def evolve(self):
            raise NotImplementedError()

    class Ekans(BaseEvolvingPokemon):
        """
        Non-abstract subclass; will get registered automatically.
        """

        element = "poison"

        def get_abilities(self):
            return ["intimidate", "shed skin"]

        def evolve(self):
            return "Congratulations! Your EKANS evolved into ARBOK!"

    # Note that only non-abstract classes got registered.
    assert list(registry.classes()) == [Sandslash, Ekans]


def test_abstract_strict_definition():
    """
    If a class has no unimplemented abstract methods, it gets registered.
    """
    registry = ClassRegistry["FightingPokemon"](attr_name="element")

    class FightingPokemon(metaclass=AutoRegister(registry)):
        element = "fighting"

    # :py:class:`FightingPokemon` does not define any abstract methods, so it is not
    # considered to be abstract :shrug:
    assert list(registry.classes()) == [FightingPokemon]


def test_error_attr_name_missing():
    """
    The registry doesn't have an ``attr_name``.
    """
    registry = ClassRegistry()

    with pytest.raises(ValueError):
        AutoRegister(registry)

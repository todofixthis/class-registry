# This module is deprecated and will be removed in a future version of ClassRegistry, so
# not going to bother getting the type hints just right (aka it was too difficult for
# me to figure out, and so I looked for a justification for giving up XD).
# type: ignore
"""
Unit tests for the deprecated :py:class:`class_registry.auto_register.AutoRegister`
function.

This function is deprecated; use :py:class:`class_registry.base.AutoRegister` instead.
:see: https://github.com/todofixthis/class-registry/issues/14
"""

from abc import ABC, abstractmethod as abstract_method

import pytest

from class_registry import ClassRegistry

# noinspection PyDeprecation
from class_registry.auto_register import AutoRegister


def test_auto_register():
    """
    Using :py:func:`AutoRegister` to, well, auto-register classes.
    """
    registry = ClassRegistry(attr_name="element")

    # :py:func:`AutoRegister` is deprecated.
    # :see: https://github.com/todofixthis/class-registry/issues/14
    with pytest.deprecated_call():
        # Note that we declare :py:func:`AutoRegister` as the metaclass
        # for our base class.
        # noinspection PyDeprecation
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

    class BaseEvolvingPokemon(BasePokemon, ABC):
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
    registry = ClassRegistry(attr_name="element")

    # :py:func:`AutoRegister` is deprecated.
    # :see: https://github.com/todofixthis/class-registry/issues/14
    with pytest.deprecated_call():
        # noinspection PyDeprecation
        class FightingPokemon(metaclass=AutoRegister(registry)):
            element = "fighting"

    # :py:class:`FightingPokemon` does not define any abstract methods, so it is not
    # considered to be abstract!
    assert list(registry.classes()) == [FightingPokemon]


def test_error_attr_name_missing():
    """
    The registry doesn't have an ``attr_name``.
    """
    registry = ClassRegistry()

    with pytest.raises(ValueError):
        # :py:func:`AutoRegister` is deprecated.
        # :see: https://github.com/todofixthis/class-registry/issues/14
        with pytest.deprecated_call():
            # noinspection PyDeprecation
            AutoRegister(registry)

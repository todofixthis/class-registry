# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from abc import ABCMeta, abstractmethod as abstract_method
from unittest import TestCase

from six import with_metaclass

from class_registry import AutoRegister, ClassRegistry


class AutoRegisterTestCase(TestCase):
    def test_auto_register(self):
        """
        Using :py:func:`AutoRegister` to, well, auto-register classes.
        """
        registry = ClassRegistry(attr_name='element')

        # Note that we declare :py:func:`AutoRegister` as the metaclass
        # for our base class.
        class BasePokemon(with_metaclass(AutoRegister(registry))):
            """
            Abstract base class; will not get registered.
            """
            @abstract_method
            def get_abilities(self):
                raise NotImplementedError()

        # noinspection PyClassHasNoInit
        class Sandslash(BasePokemon):
            """
            Non-abstract subclass; will get registered automatically.
            """
            element = 'ground'

            def get_abilities(self):
                return ['sand veil']

        # noinspection PyClassHasNoInit
        class BaseEvolvingPokemon(with_metaclass(ABCMeta, BasePokemon)):
            """
            Abstract subclass; will not get registered.
            """
            @abstract_method
            def evolve(self):
                raise NotImplementedError()

        # noinspection PyClassHasNoInit
        class Ekans(BaseEvolvingPokemon):
            """
            Non-abstract subclass; will get registered automatically.
            """
            element = 'poison'

            def get_abilities(self):
                return ['intimidate', 'shed skin']

            def evolve(self):
                return 'Congratulations! Your EKANS evolved into ARBOK!'


        self.assertListEqual(
            list(registry.items()),

            [
                # Note that only non-abstract classes got registered.
                ('ground', Sandslash),
                ('poison', Ekans),
            ],
        )

    def test_abstract_strict_definition(self):
        """
        If a class has no unimplemented abstract methods, it gets
        registered.
        """
        registry = ClassRegistry(attr_name='element')

        class FightingPokemon(with_metaclass(AutoRegister(registry))):
            element = 'fighting'

        self.assertListEqual(
            list(registry.items()),

            [
                # :py:class:`FightingPokemon` does not define any
                # abstract methods, so it is not considered to be
                # abstract!
                ('fighting', FightingPokemon),
            ],
        )

    def test_error_attr_name_missing(self):
        """
        The registry doesn't have an ``attr_name``.
        """
        registry = ClassRegistry()

        with self.assertRaises(ValueError):
            AutoRegister(registry)

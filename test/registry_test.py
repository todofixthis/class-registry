# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from functools import cmp_to_key
from unittest import TestCase

from class_registry.registry import ClassRegistry, RegistryKeyError, \
    SortedClassRegistry
from test import Bulbasaur, Charmander, Charmeleon, Pokemon, \
    Squirtle, Wartortle


class ClassRegistryTestCase(TestCase):
    def test_register_manual_keys(self):
        """
        Registers a few classes with manually-assigned identifiers and
        verifies that the factory returns them correctly.
        """
        registry = ClassRegistry()

        @registry.register('fire')
        class Charizard(Pokemon):
            pass

        @registry.register('water')
        class Blastoise(Pokemon):
            pass

        # By default, you have to specify a registry key when
        # registering new classes.  We'll see how to assign
        # registry keys automatically in the next test.
        with self.assertRaises(ValueError):
            # noinspection PyUnusedLocal
            @registry.register
            class Venusaur(Pokemon):
                pass

        self.assertIsInstance(registry['fire'], Charizard)
        self.assertIsInstance(registry['water'], Blastoise)

    def test_register_detect_keys(self):
        """
        If an attribute name is passed to ClassRegistry's constructor,
        it will automatically check for this attribute when
        registering classes.
        """
        registry = ClassRegistry(attr_name='element')

        @registry.register
        class Charizard(Pokemon):
            element = 'fire'

        @registry.register
        class Blastoise(Pokemon):
            element = 'water'

        # You can still override the registry key if you want.
        @registry.register('poison')
        class Venusaur(Pokemon):
            element = 'grass'

        self.assertIsInstance(registry['fire'], Charizard)
        self.assertIsInstance(registry['water'], Blastoise)
        self.assertIsInstance(registry['poison'], Venusaur)

        # We overrode the registry key for this class.
        with self.assertRaises(RegistryKeyError):
            # noinspection PyStatementEffect
            registry['grass']

    def test_register_error_empty_key(self):
        """
        Attempting to register a class with an empty key.
        """
        registry = ClassRegistry('element')

        with self.assertRaises(ValueError):
            # noinspection PyUnusedLocal
            @registry.register(None)
            class Ponyta(Pokemon):
                element = 'fire'

        with self.assertRaises(ValueError):
            # noinspection PyUnusedLocal
            @registry.register('')
            class Rapidash(Pokemon):
                element = 'fire'

        with self.assertRaises(ValueError):
            # noinspection PyUnusedLocal
            @registry.register
            class Mew(Pokemon):
                element = None

        with self.assertRaises(ValueError):
            # noinspection PyUnusedLocal
            @registry.register
            class Mewtwo(Pokemon):
                element = ''

    def test_unique_keys(self):
        """
        Specifying ``unique=True`` when creating the registry requires
        all keys to be unique.
        """
        registry = ClassRegistry(attr_name='element', unique=True)

        # We can register any class like normal...
        # noinspection PyUnusedLocal
        registry.register(Charmander)

        # ... but if we try to register a second class with the same
        # key, we get an error.
        with self.assertRaises(RegistryKeyError):
            registry.register(Charmeleon)

    def test_unregister(self):
        """
        Removing a class from the registry.

        This is not used that often outside of unit tests (e.g., to
        remove artifacts when a test has to add a class to a global
        registry).
        """
        registry = ClassRegistry(attr_name='element')
        registry.register(Charmander)
        registry.register(Squirtle)

        # Don't feel bad Bulbasaur!  Actually, you're my favorite!

        self.assertIs(registry.unregister('fire'), Charmander)

        with self.assertRaises(RegistryKeyError):
            registry.get('fire')

        # Note that you must unregister the KEY, not the CLASS.
        with self.assertRaises(KeyError):
            # noinspection PyTypeChecker
            registry.unregister(Squirtle)

        # If you try to unregister a key that isn't registered, you'll
        # get an error.
        with self.assertRaises(KeyError):
            registry.unregister('fire')

    def test_constructor_params(self):
        """
        Params can be passed to the registered class' constructor.
        """
        registry = ClassRegistry(attr_name='element')
        registry.register(Bulbasaur)

        # Goofus uses positional arguments, which are magical and
        # make his code more difficult to read.
        goofus  = registry.get('grass', 'goofus')

        # Gallant uses keyword arguments, producing self-documenting
        # code and being courteous to his fellow developers.
        # He still names his pokémon after himself, though. Narcissist.
        gallant = registry.get('grass', name='gallant')

        self.assertIsInstance(goofus, Bulbasaur)
        self.assertEqual(goofus.name, 'goofus')

        self.assertIsInstance(gallant, Bulbasaur)
        self.assertEqual(gallant.name, 'gallant')

    def test_new_instance_every_time(self):
        """
        Every time a registered class is invoked, a new instance is
        returned.
        """
        registry = ClassRegistry(attr_name='element')
        registry.register(Wartortle)

        self.assertIsNot(registry['water'], registry['water'])

    def test_register_function(self):
        """
        Functions can be registered as well (so long as they walk, talk
        and quack like a class).
        """
        registry = ClassRegistry()

        @registry.register('fire')
        def pokemon_factory(name=None):
            return Charmeleon(name=name)

        poke = registry.get('fire', name='trogdor')

        self.assertIsInstance(poke, Charmeleon)
        self.assertEqual(poke.name, 'trogdor')


class SortedClassRegistryTestCase(TestCase):
    def test_sort_key(self):
        """
        When iterating over a SortedClassRegistry, classes are returned
        in sorted order rather than inclusion order.
        """
        registry =\
            SortedClassRegistry(
                attr_name   = 'element',
                sort_key    = 'weight',
            )

        @registry.register
        class Geodude(Pokemon):
            element = 'rock'
            weight  = 100

        @registry.register
        class Machop(Pokemon):
            element = 'fighting'
            weight = 75

        @registry.register
        class Bellsprout(Pokemon):
            element = 'grass'
            weight = 15

        # The registry iterates over registered classes in ascending
        # order by ``weight``.
        self.assertListEqual(
            list(registry.values()),
            [Bellsprout, Machop, Geodude],
        )

    def test_sort_key_reverse(self):
        """
        Reversing the order of a sort key.
        """
        registry =\
            SortedClassRegistry(
                attr_name   = 'element',
                sort_key    = 'weight',
                reverse     = True,
            )

        @registry.register
        class Geodude(Pokemon):
            element = 'rock'
            weight  = 100

        @registry.register
        class Machop(Pokemon):
            element = 'fighting'
            weight = 75

        @registry.register
        class Bellsprout(Pokemon):
            element = 'grass'
            weight = 15

        # The registry iterates over registered classes in descending
        # order by ``weight``.
        self.assertListEqual(
            list(registry.values()),
            [Geodude, Machop, Bellsprout],
        )

    def test_cmp_to_key(self):
        """
        If you want to use a ``cmp`` function to define the ordering,
        you must use the :py:func:`cmp_to_key` function.
        """
        def compare_pokemon(a, b):
            # ``a`` and ``b`` are tuples of ``(key, class)``.
            return (
                    (a[1].popularity < b[1].popularity)
                -   (a[1].popularity > b[1].popularity)
            )

        registry =\
            SortedClassRegistry(
                attr_name   = 'element',
                sort_key    = cmp_to_key(compare_pokemon),
            )

        @registry.register
        class Onix(Pokemon):
            element = 'rock'
            popularity = 50

        @registry.register
        class Cubone(Pokemon):
            element = 'water'
            popularity = 100

        @registry.register
        class Exeggcute(Pokemon):
            element = 'grass'
            popularity = 10

        # The registry iterates over registered classes in descending
        # order by ``popularity``.
        self.assertListEqual(
            list(registry.values()),
            [Cubone, Onix, Exeggcute],
        )

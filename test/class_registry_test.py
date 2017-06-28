# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from unittest import TestCase

from class_registry import ClassRegistry, ClassRegistryInstanceCache, \
    RegistryKeyError, RegistryPatcher, SortedClassRegistry


class Pokemon(object):
    element = None

    def __init__(self, name=None):
        super(Pokemon, self).__init__()

        self.name = name


# Define some classes that we can register.
class Charmander(Pokemon):   element = 'fire'
class Charmeleon(Pokemon):   element = 'fire'
class Squirtle(Pokemon):     element = 'water'
class Wartortle(Pokemon):    element = 'water'
class Bulbasaur(Pokemon):    element = 'grass'
class Ivysaur(Pokemon):      element = 'grass'


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


class RegistryPatcherTestCase(TestCase):
    def setUp(self):
        super(RegistryPatcherTestCase, self).setUp()

        self.registry = ClassRegistry(attr_name='element')

    def test_patch_detect_keys(self):
        """
        Patching a registry in a context, with registry keys detected
        automatically.
        """
        self.registry.register(Charmander)
        self.registry.register(Squirtle)

        with RegistryPatcher(self.registry, Charmeleon, Bulbasaur):
            self.assertIsInstance(self.registry['fire'], Charmeleon)
            self.assertIsInstance(self.registry['water'], Squirtle)

            # Nesting contexts?  You betcha!
            with RegistryPatcher(self.registry, Ivysaur):
                self.assertIsInstance(self.registry['grass'], Ivysaur)

            self.assertIsInstance(self.registry['grass'], Bulbasaur)

        # Save file corrupted.  Restoring previous save...
        self.assertIsInstance(self.registry['fire'], Charmander)
        self.assertIsInstance(self.registry['water'], Squirtle)

        with self.assertRaises(RegistryKeyError):
            self.registry.get('grass')

    def test_patch_manual_keys(self):
        """
        Patching a registry in a context, specifying registry keys
        manually.
        """
        self.registry.register('sparky')(Charmander)
        self.registry.register('chad')(Squirtle)

        with RegistryPatcher(self.registry, sparky=Charmeleon, rex=Bulbasaur):
            self.assertIsInstance(self.registry['sparky'], Charmeleon)
            self.assertIsInstance(self.registry['chad'], Squirtle)

            # Don't worry Chad; your day will come!
            with RegistryPatcher(self.registry, rex=Ivysaur):
                self.assertIsInstance(self.registry['rex'], Ivysaur)

            self.assertIsInstance(self.registry['rex'], Bulbasaur)

        # Save file corrupted.  Restoring previous save...
        self.assertIsInstance(self.registry['sparky'], Charmander)
        self.assertIsInstance(self.registry['chad'], Squirtle)

        with self.assertRaises(RegistryKeyError):
            self.registry.get('jodie')


class SortedClassRegistryTestCase(TestCase):
    def test_sorted_classes(self):
        """
        When iterating over a SortedClassRegistry, classes are returned
        in sorted order rather than inclusion order.
        """
        registry = SortedClassRegistry(
            # Use the ``widget_type`` attribute to identify each class.
            attr_name = 'widget_type',

            # Compare the ``weight`` attribute to determine the sort
            # order.
            sort_key = lambda t: t[1].weight,
        )

        @registry.register
        class AlphaWidget(object):
            widget_type = 'alpha'
            weight      = 30

        @registry.register
        class BravoWidget(object):
            widget_type = 'bravo'
            weight      = -20

        @registry.register
        class CharlieWidget(object):
            widget_type = 'charlie'
            weight      = 0

        # When calling one of the iterator functions, the result is
        # ordered by weight because of the ``cmp_func`` we specified
        # when creating the SortedClassRegistry.
        self.assertListEqual(
            list(registry.values()),
            [BravoWidget, CharlieWidget, AlphaWidget],
        )


class ClassRegistryInstanceCacheTestCase(TestCase):
    def setUp(self):
        super(ClassRegistryInstanceCacheTestCase, self).setUp()

        self.registry = ClassRegistry(attr_name='element')
        self.cache = ClassRegistryInstanceCache(self.registry)

    def test_get(self):
        """
        When an instance is returned from
        :py:meth:`ClassRegistryInstanceCache.get`, future invocations
        return the same instance.
        """
        # Register a few classes with the ClassRegistry.
        self.registry.register(Bulbasaur)
        self.registry.register(Charmander)
        self.registry.register(Squirtle)

        poke_1 = self.cache['grass']
        self.assertIsInstance(poke_1, Bulbasaur)

        # Same key = exact same instance.
        poke_2 = self.cache['grass']
        self.assertIs(poke_2, poke_1)

        poke_3 = self.cache['water']
        self.assertIsInstance(poke_3, Squirtle)

        # If we pull a class directly from the wrapped registry, we get
        # a new instance.
        poke_4 = self.registry['water']
        self.assertIsInstance(poke_4, Squirtle)
        self.assertIsNot(poke_3, poke_4)

    def test_template_args(self):
        """
        Extra params passed to the cache constructor are passed to the
        template function when creating new instances.
        """
        self.registry.register(Charmeleon)
        self.registry.register(Wartortle)

        # Add an extra init param to the cache.
        cache = ClassRegistryInstanceCache(self.registry, name='Bruce')

        # The cache parameters are automatically applied to the class'
        # initializer.
        poke_1 = cache['fire']
        self.assertIsInstance(poke_1, Charmeleon)
        self.assertEqual(poke_1.name, 'Bruce')

        poke_2 = cache['water']
        self.assertIsInstance(poke_2, Wartortle)
        self.assertEqual(poke_2.name, 'Bruce')

    def test_iterator(self):
        """
        Creating an iterator using :py:func:`iter`.
        """
        self.registry.register(Bulbasaur)
        self.registry.register(Charmander)
        self.registry.register(Squirtle)

        # The cache's iterator only operates over cached instances.
        self.assertListEqual(list(iter(self.cache)), [])

        poke_1 = self.cache['water']
        poke_2 = self.cache['grass']
        poke_3 = self.cache['fire']

        # The order that values are yielded depends on the ordering of
        # the wrapped registry.
        self.assertListEqual(
            list(iter(self.cache)),
            [poke_2, poke_3, poke_1],
        )

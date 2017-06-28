# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from unittest import TestCase

from class_registry.registry import ClassRegistry
from class_registry.cache import ClassRegistryInstanceCache
from test import Bulbasaur, Charmander, Charmeleon, Squirtle, Wartortle


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

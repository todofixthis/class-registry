# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from os.path import dirname
from unittest import TestCase

from pkg_resources import working_set, iter_entry_points

from class_registry import EntryPointClassRegistry, RegistryKeyError
from test import Bulbasaur, Charmander, Squirtle


def setUpModule():
    #
    # Install a fake distribution that we can use to inject entry
    # points at runtime.
    #
    # The side effects from this are pretty severe, but they only
    # impact this test, and they are undone as soon as the process
    # terminates.
    #
    working_set.add_entry(dirname(__file__))


class EntryPointClassRegistryTestCase(TestCase):
    def test_happy_path(self):
        """
        Loading classes automatically via entry points.
        """
        registry = EntryPointClassRegistry('pokemon')

        fire = registry['fire']
        self.assertIsInstance(fire, Charmander)
        self.assertIsNone(fire.name)

        grass = registry.get('grass')
        self.assertIsInstance(grass, Bulbasaur)
        self.assertIsNone(grass.name)

        water = registry.get('water', name='archibald')
        self.assertIsInstance(water, Squirtle)
        self.assertEqual(water.name, 'archibald')

    def test_len(self):
        """
        Getting the length of an entry point class registry.
        """
        # Just in case some other package defines pokémon entry
        # points (:
        expected = len(list(iter_entry_points('pokemon')))

        # Quick sanity check, to make sure our test pokémon are
        # registered correctly.
        self.assertGreaterEqual(expected, 3)

        registry = EntryPointClassRegistry('pokemon')
        self.assertEqual(len(registry), expected)

    def test_error_wrong_group(self):
        """
        The registry can't find entry points associated with the wrong
        """
        registry = EntryPointClassRegistry('random')

        with self.assertRaises(RegistryKeyError):
            # The dummy project registers
            registry.get('fire')

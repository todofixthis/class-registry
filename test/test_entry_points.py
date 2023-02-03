from os.path import dirname
from unittest import TestCase

from pkg_resources import iter_entry_points, working_set

from class_registry import EntryPointClassRegistry, RegistryKeyError
from test import Bulbasaur, Charmander, Mew, PokemonFactory, Squirtle


def setUpModule():
    #
    # Install a fake distribution that we can use to inject entry points at
    # runtime.
    #
    # The side effects from this are pretty severe, but they (very probably)
    # only impact this test, and they are undone as soon as the process
    # terminates.
    #
    working_set.add_entry(dirname(__file__))


class EntryPointClassRegistryTestCase(TestCase):
    def test_happy_path(self):
        """
        Loading classes automatically via entry points.

        See ``dummy_package.egg-info/entry_points.txt`` for more info.
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

        # The 'psychic' entry point actually references a function, but it
        # works exactly the same as a class.
        psychic = registry.get('psychic', 'snuggles')
        self.assertIsInstance(psychic, Mew)
        self.assertEqual(psychic.name, 'snuggles')

    def test_branding(self):
        """
        Configuring the registry to "brand" each class/instance with its
        corresponding key.
        """
        registry = EntryPointClassRegistry('pokemon', attr_name='poke_type')
        try:
            # Branding is applied immediately to each registered class.
            self.assertEqual(getattr(Charmander, 'poke_type'), 'fire')
            self.assertEqual(getattr(Squirtle, 'poke_type'), 'water')

            # Instances, too!
            self.assertEqual(registry['fire'].poke_type, 'fire')
            self.assertEqual(registry.get('water', 'phil').poke_type, 'water')

            # Registered functions and methods can't be branded this way,
            # though...
            self.assertFalse(
                hasattr(PokemonFactory.create_psychic_pokemon, 'poke_type'),
            )

            # ... but we can brand the resulting instances.
            self.assertEqual(registry['psychic'].poke_type, 'psychic')
            self.assertEqual(registry.get('psychic').poke_type, 'psychic')
        finally:
            # Clean up after ourselves.
            for cls in registry.values():
                if isinstance(cls, type):
                    try:
                        delattr(cls, 'poke_type')
                    except AttributeError:
                        pass

    def test_len(self):
        """
        Getting the length of an entry point class registry.
        """
        # Just in case some other package defines pokémon entry
        # points (:
        expected = len(list(iter_entry_points('pokemon')))

        # Quick sanity check, to make sure our test pokémon are
        # registered correctly.
        self.assertGreaterEqual(expected, 4)

        registry = EntryPointClassRegistry('pokemon')
        self.assertEqual(len(registry), expected)

    def test_error_wrong_group(self):
        """
        The registry can't find entry points associated with the wrong group.
        """
        # Pokémon get registered (unsurprisingly) under the ``pokemon`` group,
        # not ``random``.
        registry = EntryPointClassRegistry('random')

        with self.assertRaises(RegistryKeyError):
            registry.get('fire')

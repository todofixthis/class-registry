# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from unittest import TestCase

from class_registry.patcher import RegistryPatcher
from class_registry.registry import ClassRegistry, RegistryKeyError
from test import Bulbasaur, Charmander, Charmeleon, Ivysaur, Squirtle


class RegistryPatcherTestCase(TestCase):
    def setUp(self):
        super(RegistryPatcherTestCase, self).setUp()

        self.registry = ClassRegistry(attr_name='element', unique=True)

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

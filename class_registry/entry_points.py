# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from typing import Text

from pkg_resources import EntryPoint, iter_entry_points

from class_registry import BaseRegistry

__all__ = [
    'EntryPointClassRegistry',
]


class EntryPointClassRegistry(BaseRegistry):
    """
    A class registry that loads classes using setuptools entry points.
    """
    def __init__(self, group):
        # type: (Text) -> None
        """
        :param group:
            The name of the entry point group that will be used to load
            new classes.
        """
        super(EntryPointClassRegistry, self).__init__()

        self.group = group

    def __len__(self):
        return sum(1 for _ in self.keys())

    def get_class(self, key):
        for e in iter_entry_points(self.group): # type: EntryPoint
            if e.name == key:
                return e.load()

        return self.__missing__(key)

    def _items(self):
        for e in iter_entry_points(self.group): # type: EntryPoint
            yield e.name, e.load()

    def keys(self):
        for e in iter_entry_points(self.group): # type: EntryPoint
            yield e.name

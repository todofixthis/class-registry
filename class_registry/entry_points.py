# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from typing import Text, Generator

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
        for e in self._iter_entry_points():
            if e.name == key:
                return e.load()

        return self.__missing__(key)

    def _items(self):
        for e in self._iter_entry_points():
            yield e.name, e.load()

    def keys(self):
        for e in self._iter_entry_points():
            yield e.name

    def _iter_entry_points(self):
        # type: () -> Generator[EntryPoint]
        """
        Iterates over all entry points assigned to the registry's group
        name.
        """
        return iter_entry_points(self.group)

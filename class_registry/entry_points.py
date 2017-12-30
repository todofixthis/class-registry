# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from typing import Dict, Optional, Text

from pkg_resources import iter_entry_points
from six import iteritems

from class_registry import BaseRegistry

__all__ = [
    'EntryPointClassRegistry',
]


class EntryPointClassRegistry(BaseRegistry):
    """
    A class registry that loads classes using setuptools entry points.
    """
    def __init__(self, group, attr_name=None):
        # type: (Text, Optional[Text]) -> None
        """
        :param group:
            The name of the entry point group that will be used to load
            new classes.

        :param attr_name:
            If set, the registry will "brand" each class with its
            corresponding registry key.  This makes it easier to
            perform reverse lookups later.

            Note: if a class already defines this attribute, the
            registry will overwrite it!
        """
        super(EntryPointClassRegistry, self).__init__()

        self.attr_name  = attr_name
        self.group      = group

        self._cache = None # type: Optional[Dict[Text, type]]
        """
        Caches registered classes locally, so that we don't have to
        keep iterating over entry points.
        """

        # If :py:attr:`attr_name` is set, warm the cache immediately to
        # apply branding.
        if self.attr_name:
            self._get_cache()

    def __len__(self):
        return len(self._get_cache())

    def __repr__(self):
        return '{type}(group={group!r})'.format(
            group   = self.group,
            type    = type(self).__name__,
        )

    def get(self, key, *args, **kwargs):
        instance =\
            super(EntryPointClassRegistry, self).get(key, *args, **kwargs)

        if self.attr_name:
            # Apply branding to the instance explicitly.
            # This is particularly important if the corresponding entry
            # point references a function or method.
            setattr(instance, self.attr_name, key)

        return instance

    def get_class(self, key):
        try:
            cls = self._get_cache()[key]
        except KeyError:
            cls = self.__missing__(key)

        return cls

    def items(self):
        return iteritems(self._get_cache())

    def refresh(self):
        """
        Purges the local cache.
        The next access attempt will reload all entry points.

        This is useful if you load a distribution at runtime.
        Otherwise, it probably serves no useful purpose.
        """
        self._cache = None

    def _get_cache(self):
        # type: () -> Dict[Text, type]
        """
        Populates the cache (if necessary) and returns it.
        """
        if self._cache is None:
            self._cache = {}
            for e in iter_entry_points(self.group):
                cls = e.load()

                # Try to apply branding, but only for compatible types
                # (i.e., functions and methods can't be branded this
                # way).
                if self.attr_name and isinstance(cls, type):
                    setattr(cls, self.attr_name, e.name)

                self._cache[e.name] = cls

        # noinspection PyTypeChecker
        return self._cache

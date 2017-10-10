# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from collections import defaultdict
from typing import Any, Dict, Generator, Hashable

from six import iterkeys

from class_registry import ClassRegistry

__all__ = [
    'ClassRegistryInstanceCache',
]


class ClassRegistryInstanceCache(object):
    """
    Wraps a ClassRegistry instance, caching instances as they are
    created.

    This allows you to create [multiple] registries that cache
    INSTANCES locally (so that they can be scoped and garbage-
    collected), while keeping the CLASS registry separate.

    Note that the internal class registry is copied by reference, so
    any classes that are registered afterward are accessible to
    both the ClassRegistry and the ClassRegistryInstanceCache.
    """
    def __init__(self, class_registry, *args, **kwargs):
        # type: (ClassRegistry, *Any, **Any) -> None
        """
        :param class_registry:
            The wrapped ClassRegistry.

        :param args:
            Positional arguments passed to the class registry's
            template when creating new instances.

        :param kwargs:
            Keyword arguments passed to the class registry's template
            function when creating new instances.
        """
        super(ClassRegistryInstanceCache, self).__init__()

        self._registry  = class_registry
        self._cache     = {}

        self._key_map = defaultdict(list) # type: Dict[Hashable, list]

        self._template_args     = args
        self._template_kwargs   = kwargs

    def __getitem__(self, key):
        """
        Returns the cached instance associated with the specified key.
        """
        instance_key = self.get_instance_key(key)

        if instance_key not in self._cache:
            class_key = self.get_class_key(key)

            # Map lookup keys to cache keys so that we can iterate over
            # them in the correct order.
            # :py:meth:`__iter__`
            self._key_map[class_key].append(instance_key)

            self._cache[instance_key] =\
                self._registry.get(
                    class_key,
                    *self._template_args,
                    **self._template_kwargs
                )

        return self._cache[instance_key]

    def __iter__(self):
        # type: () -> Generator[Any]
        """
        Returns a generator for iterating over cached instances, using
        the wrapped registry to determine sort order.

        If a key has not been accessed yet, it will not be included.
        """
        for lookup_key in iterkeys(self._registry):
            for cache_key in self._key_map[lookup_key]:
                yield self._cache[cache_key]

    def warm_cache(self):
        """
        Warms up the cache, ensuring that an instance is created for
        every key in the registry.

        Note that this method does not account for any classes that may
        be added to the wrapped ClassRegistry in the future.
        """
        for key in iterkeys(self._registry):
            self.__getitem__(key)

    def get_instance_key(self, key):
        # type: (Any) -> Hashable
        """
        Generates a key that can be used to store/lookup values in the
        instance cache.

        :param key:
            Value provided to :py:meth:`__getitem__`.
        """
        return self.get_class_key(key)

    def get_class_key(self, key):
        # type: (Any) -> Hashable
        """
        Generates a key that can be used to store/lookup values in the
        wrapped :py:class:`ClassRegistry` instance.

        This method is only invoked in the event of a cache miss.

        :param key:
            Value provided to :py:meth:`__getitem__`.
        """
        return self._registry.gen_lookup_key(key)

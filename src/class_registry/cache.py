__all__ = ["ClassRegistryInstanceCache"]

import typing
from collections import defaultdict

from . import ClassRegistry

T = typing.TypeVar("T")


class ClassRegistryInstanceCache(typing.Mapping[typing.Hashable, T]):
    """
    Wraps a ClassRegistry instance, caching instances as they are created.

    This allows you to create [multiple] registries that cache instances locally (so
    that they can be scoped and garbage-collected), whilst keeping the class registry
    separate.

    Note that the internal class registry is copied by reference, so any classes that
    are registered afterward are accessible to both the ``ClassRegistry`` and the
    ``ClassRegistryInstanceCache``.
    """

    def __init__(
        self,
        class_registry: ClassRegistry[T],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """
        Args:
            class_registry:
                The wrapped ClassRegistry.
            args:
                Positional arguments passed to the class registry's template when
                creating new instances.
            kwargs:
                Keyword arguments passed to the class registry's template function when
                creating new instances.
        """
        super().__init__()

        self._registry: ClassRegistry[T] = class_registry
        self._cache: dict[typing.Hashable, T] = {}

        self._key_map: dict[typing.Hashable, list[typing.Hashable]] = defaultdict(list)

        self._template_args = args
        self._template_kwargs = kwargs

    def __getitem__(self, key: typing.Hashable) -> T:
        """
        Returns the cached instance associated with the specified key.
        """
        instance_key = self.get_instance_key(key)

        if instance_key not in self._cache:
            class_key = self.get_class_key(key)

            # Map lookup keys to cache keys so that we can iterate over them in the
            # correct order.
            self._key_map[class_key].append(instance_key)

            self._cache[instance_key] = self._registry.get(
                class_key, *self._template_args, **self._template_kwargs
            )

        return self._cache[instance_key]

    def __iter__(self) -> typing.Generator[T, None, None]:
        """
        Returns a generator for iterating over cached instances, using the wrapped
        registry to determine sort order.

        If a key has not been accessed yet, it will not be included.
        """
        for lookup_key in self._registry.keys():
            for cache_key in self._key_map[lookup_key]:
                yield self._cache[cache_key]

    def __len__(self) -> int:
        """
        Returns the number of cached instances.

        Does not reflect any registered classes that haven't been accessed yet.
        """
        return len(self._cache)

    def warm_cache(self) -> None:
        """
        Warms up the cache, ensuring that an instance is created for every key currently
        in the registry.

        .. note::

           This method has no effect for any classes added to the wrapped
           :py:class:`ClassRegistry` after calling ``warm_cache``.
        """
        for key in self._registry.keys():
            self.__getitem__(key)

    def get_instance_key(self, key: typing.Hashable) -> typing.Hashable:
        """
        Generates a key that can be used to store/lookup values in the instance cache.

        Args:
            key:
                Value provided to :py:meth:`__getitem__`.
        """
        return self.get_class_key(key)

    def get_class_key(self, key: typing.Hashable) -> typing.Hashable:
        """
        Generates a key that can be used to store/lookup values in the wrapped
        :py:class:`ClassRegistry` instance.

        This method is only invoked in the event of a cache miss.

        Args:
            key:
                Value provided to :py:meth:`__getitem__`.
        """
        return self._registry.gen_lookup_key(key)

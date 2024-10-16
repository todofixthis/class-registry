__all__ = ["EntryPointClassRegistry"]

import typing
from importlib.metadata import entry_points

from .base import BaseRegistry

T = typing.TypeVar("T")


class EntryPointClassRegistry(BaseRegistry[T]):
    """
    A class registry that loads classes using setuptools entry points.
    """

    def __init__(
        self,
        group: str,
        attr_name: typing.Optional[str] = None,
    ) -> None:
        """
        Args:
            group:
                The name of the entry point group that will be used to load new classes.

            attr_name:
                If set, the registry will "brand" each class with its corresponding
                registry key.  This makes it easier to perform reverse lookups later.

                Note: if a class already defines this attribute, the registry will
                overwrite it!
        """
        super().__init__()

        self.attr_name = attr_name
        self.group = group

        self._cache: typing.Optional[dict[typing.Hashable, typing.Type[T]]] = None
        """
        Caches registered classes locally, so that we don't have to keep iterating over
        entry points.
        """

        # If :py:attr:`attr_name` is set, warm the cache immediately, to apply branding.
        if self.attr_name:
            self._get_cache()

    def __len__(self) -> int:
        return len(self._get_cache())

    def __repr__(self) -> str:
        return f"{type(self).__name__}(group={self.group!r})"

    def get(self, key: typing.Hashable, *args: typing.Any, **kwargs: typing.Any) -> T:
        instance = super().get(key, *args, **kwargs)

        if self.attr_name:
            # Apply branding to the instance explicitly.
            # This is particularly important if the corresponding entry point references
            # a function or method.
            setattr(instance, self.attr_name, key)

        return instance

    def get_class(self, key: typing.Hashable) -> typing.Type[T]:
        try:
            return self._get_cache()[key]
        except KeyError:
            return self.__missing__(key)

    def keys(self) -> typing.Iterable[typing.Hashable]:
        return iter(self._get_cache().keys())

    def refresh(self) -> None:
        """
        Purges the local cache.  The next access attempt will reload all entry points.

        This is useful if you load a distribution at runtime...such as during unit tests
        for ``phx-class-registry``.  Otherwise, it probably serves no useful purpose (:
        """
        self._cache = None

    def _get_cache(self) -> dict[typing.Hashable, typing.Type[T]]:
        """
        Populates the cache (if necessary) and returns it.
        """
        if self._cache is None:
            self._cache = {}
            for e in entry_points(group=self.group):
                cls = e.load()

                # Try to apply branding, but only for compatible types (i.e., functions
                # and methods can't be branded this way).
                if self.attr_name and isinstance(cls, type):
                    setattr(cls, self.attr_name, e.name)

                self._cache[e.name] = cls

        return self._cache

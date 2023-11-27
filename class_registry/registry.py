__all__ = ["ClassRegistry", "SortedClassRegistry"]

import typing
from collections import OrderedDict
from functools import cmp_to_key

from .base import BaseMutableRegistry, RegistryKeyError


class ClassRegistry(BaseMutableRegistry):
    """
    Maintains a registry of classes and provides a generic factory for instantiating
    them.
    """

    def __init__(
        self,
        attr_name: typing.Optional[str] = None,
        unique: bool = False,
    ) -> None:
        """
        :param attr_name:
            If provided, :py:meth:`register` will automatically detect the key to use
            when registering new classes.

        :param unique:
            Determines what happens when two classes are registered with the same key:

            - ``True``: A :py:class:`KeyError` will be raised.
            - ``False``: The second class will replace the first one.
        """
        super(ClassRegistry, self).__init__(attr_name)

        self.unique = unique

        self._registry: typing.OrderedDict[typing.Hashable, type] = OrderedDict()

    def __len__(self) -> int:
        """
        Returns the number of registered classes.
        """
        return len(self._registry)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(attr_name={self.attr_name!r}, unique={self.unique!r})"

    def get_class(self, key: typing.Hashable) -> typing.Optional[type]:
        """
        Returns the class associated with the specified key.
        """
        lookup_key = self.gen_lookup_key(key)

        try:
            return self._registry[lookup_key]
        except KeyError:
            return self.__missing__(lookup_key)

    def items(
        self,
    ) -> typing.Generator[typing.Tuple[typing.Hashable, type], None, None]:
        """
        Iterates over all registered classes, in the order they were added.
        """
        for key, lookup_key in self._lookup_keys.items():
            yield key, self._registry[lookup_key]

    def _register(self, key: typing.Hashable, class_: type) -> None:
        """
        Registers a class with the registry.

        :param key: Has already been processed by :py:meth:`gen_lookup_key`.
        """
        if key in ["", None]:
            raise ValueError(
                f"Attempting to register class {class_.__name__} "
                "with empty registry key {key!r}."
            )

        if self.unique and (key in self._registry):
            raise RegistryKeyError(
                f"{class_.__name__} with key {key!r} is already registered.",
            )

        self._registry[key] = class_

    def _unregister(self, key: typing.Hashable) -> type:
        """
        Unregisters the class at the specified key.

        :param key: Has already been processed by :py:meth:`gen_lookup_key`.
        """
        return (
            self._registry.pop(key) if key in self._registry else self.__missing__(key)
        )


class SortedClassRegistry(ClassRegistry):
    """
    A ClassRegistry that uses a function to determine sort order when iterating.
    """

    def __init__(
        self,
        sort_key: typing.Any,
        attr_name: typing.Optional[str] = None,
        unique: bool = False,
        reverse: bool = False,
    ) -> None:
        """
        :param sort_key:
            Attribute name or callable, used to determine the sort value.

            If callable, must accept two tuples of (key, class, lookup_key).

            You can also use :py:func:`functools.cmp_to_key`.

        :param attr_name:
            If provided, :py:meth:`register` will automatically detect the key to use
            when registering new classes.

        :param unique:
            Determines what happens when two classes are registered with the same key:

            - ``True``: The second class will replace the first one.
            - ``False``: A ``ValueError`` will be raised.

        :param reverse:
            Whether to reverse the sort ordering.
        """
        super(SortedClassRegistry, self).__init__(attr_name, unique)

        self._sort_key = (
            sort_key if callable(sort_key) else self.create_sorter(sort_key)
        )

        self.reverse = reverse

    def items(
        self,
    ) -> typing.Generator[typing.Tuple[typing.Hashable, type], None, None]:
        for key, class_, _ in sorted(
            # Provide both the human-readable key and actual lookup key to the sorter...
            (
                (key, class_, self.gen_lookup_key(key))
                for (key, class_) in super().items()
            ),
            key=self._sort_key,
            reverse=self.reverse,
        ):
            # ...but for parity with other ClassRegistry types, only include the
            # human-readable key in the result.
            yield key, class_

    @staticmethod
    def create_sorter(sort_key: str) -> typing.Any:
        """
        Given a sort key, creates a function that can be used to sort items when
        iterating over the registry.
        """

        def sorter(a, b):
            a_attr = getattr(a[1], sort_key)
            b_attr = getattr(b[1], sort_key)

            return (a_attr > b_attr) - (a_attr < b_attr)

        return cmp_to_key(sorter)

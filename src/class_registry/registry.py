__all__ = ["ClassRegistry", "SortedClassRegistry"]

import typing
from functools import cmp_to_key

from .base import BaseMutableRegistry, RegistryKeyError

# :see: https://github.com/python/typeshed/blob/main/stdlib/_typeshed/README.md
if typing.TYPE_CHECKING:
    from _typeshed import SupportsAllComparisons

T = typing.TypeVar("T")


class ClassRegistry(BaseMutableRegistry[T]):
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
        Args:
            attr_name:
                If provided, :py:meth:`register` will automatically detect the key to
                use when registering new classes.

            unique:
                Determines what happens when two classes are registered with the same
                key:

                - ``True``: A :py:class:`KeyError` will be raised.
                - ``False``: The second class will replace the first one.
        """
        super().__init__(attr_name)

        self.unique = unique

        self._registry: dict[typing.Hashable, typing.Type[T]] = {}

    def __len__(self) -> int:
        return len(self._registry)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(attr_name={self.attr_name!r}, unique={self.unique!r})"

    def get_class(self, key: typing.Hashable) -> typing.Type[T]:
        """
        Returns the class associated with the specified key.
        """
        lookup_key = self.gen_lookup_key(key)

        try:
            return self._registry[lookup_key]
        except KeyError:
            return self.__missing__(lookup_key)

    def _register(self, key: typing.Hashable, class_: typing.Type[T]) -> None:
        """
        Registers a class with the registry.

        Args:
            key:
                Has already been processed by :py:meth:`gen_lookup_key`.
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

    def _unregister(self, key: typing.Hashable) -> typing.Type[T]:
        """
        Unregisters the class at the specified key.

        Args:
            key:
                Has already been processed by :py:meth:`gen_lookup_key`.
        """
        return (
            self._registry.pop(key) if key in self._registry else self.__missing__(key)
        )


class SortedClassRegistry(ClassRegistry[T]):
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
        Args:
            sort_key:
                Attribute name or callable, used to determine the sort value.

                If callable, must accept two tuples of (key, class, lookup_key).

                You can also use :py:func:`functools.cmp_to_key`.
            attr_name:
                If provided, :py:meth:`register` will automatically detect the key to
                use when registering new classes.
            unique:
                Determines what happens when two classes are registered with the same
                key:

                - ``True``: The second class will replace the first one.
                - ``False``: A ``ValueError`` will be raised.
            reverse:
                Whether to reverse the sort ordering.
        """
        super().__init__(attr_name, unique)

        self._sort_key = (
            sort_key if callable(sort_key) else self.create_sorter(sort_key)
        )

        self.reverse = reverse

    def keys(self) -> typing.Iterable[typing.Hashable]:
        """
        Returns the collection of registry keys, in the order that they were registered.
        """
        return iter(
            key
            for key, _, _ in sorted(
                (
                    # Provide both human-readable and lookup keys to the sorter.
                    (key, self.get_class(key), self.gen_lookup_key(key))
                    for key in super().keys()
                ),
                key=self._sort_key,
                reverse=self.reverse,
            )
        )

    @staticmethod
    def create_sorter(sort_key: str) -> typing.Callable[..., "SupportsAllComparisons"]:
        """
        Given a sort key, creates a function that can be used to sort items when
        iterating over the registry.
        """

        def sorter(
            a: typing.Tuple[typing.Hashable, typing.Type[T], typing.Hashable],
            b: typing.Tuple[typing.Hashable, typing.Type[T], typing.Hashable],
        ) -> int:
            a_attr = getattr(a[1], sort_key)
            b_attr = getattr(b[1], sort_key)

            # Technically ``typing.Hashable`` objects don't have to implement comparison
            # support, so this is slightly unsafe. But, in the vast majority of cases we
            # expect keys to be str values, so this should be fine (:O
            #
            # Incidentally, that's why we need a seemingly-unnecessary ``cast`` here.
            return typing.cast(int, (a_attr > b_attr) - (a_attr < b_attr))

        return cmp_to_key(sorter)

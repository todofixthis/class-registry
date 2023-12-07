import typing

__all__ = [
    "ClassRegistry",
]

from .base import BaseMutableRegistry, RegistryKeyError

T = typing.TypeVar("T")


class ClassRegistry(BaseMutableRegistry[T]):
    """
    Maintains a registry of classes and provides a generic factory for
    instantiating them.
    """

    def __init__(
        self,
        attr_name: typing.Optional[str] = None,
        unique: bool = False,
    ) -> None:
        """
        :param attr_name:
            If provided, :py:meth:`register` will automatically detect the key
            to use when registering new classes.

        :param unique:
            Determines what happens when two classes are registered with the
            same key:

            - ``True``: A :py:class:`KeyError` will be raised.
            - ``False``: The second class will replace the first one.
        """
        super().__init__(attr_name)

        self.unique = unique

        self._registry: dict[typing.Hashable, typing.Type[T]] = {}

    def __repr__(self) -> str:
        return "{type}(attr_name={attr_name!r}, unique={unique!r})".format(
            attr_name=self.attr_name,
            type=type(self).__name__,
            unique=self.unique,
        )

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

        :param key: Has already been processed by :py:meth:`gen_lookup_key`.
        """
        if key in ["", None]:
            raise ValueError(
                "Attempting to register class {cls} "
                "with empty registry key {key!r}.".format(
                    cls=class_.__name__,
                    key=key,
                ),
            )

        if self.unique and (key in self._registry):
            raise RegistryKeyError(
                "{cls} with key {key!r} is already registered.".format(
                    cls=class_.__name__,
                    key=key,
                ),
            )

        self._registry[key] = class_

    def _unregister(self, key: typing.Hashable) -> typing.Type[T]:
        """
        Unregisters the class at the specified key.

        :param key: Has already been processed by :py:meth:`gen_lookup_key`.
        """
        return (
            self._registry.pop(key) if key in self._registry else self.__missing__(key)
        )

__all__ = ["RegistryPatcher"]

import typing

from . import RegistryKeyError
from .base import BaseMutableRegistry


T = typing.TypeVar("T")


class RegistryPatcher(object):
    """
    Creates a context in which classes are temporarily registered with a class registry,
    then removed when the context exits.

    .. note::

       Only mutable registries can be patched.
    """

    class DoesNotExist(object):
        """
        Used to identify a value that did not exist before we started.
        """

        pass

    def __init__(
        self,
        registry: BaseMutableRegistry[T],
        *args: typing.Type[T],
        **kwargs: typing.Type[T]
    ) -> None:
        """
        :param registry:
            A :py:class:`MutableRegistry` instance to patch.

        :param args:
            Classes to add to the registry.

            This behaves the same as decorating each class with ``@registry.register``.

            .. note::

               ``registry.attr_name`` must be set.

        :param kwargs:
            Same as ``args``, except you explicitly specify the registry keys.

            In the event of a conflict, values in ``args`` override values in
            ``kwargs``.
        """
        super().__init__()

        assert registry.attr_name is not None
        for class_ in args:
            kwargs[getattr(class_, registry.attr_name)] = class_

        self.target: BaseMutableRegistry[T] = registry

        self._new_values: dict[str, typing.Type[T]] = kwargs
        self._prev_values: dict[
            typing.Hashable,
            typing.Union[typing.Type[T], typing.Type[RegistryPatcher.DoesNotExist]],
        ] = {}

    def __enter__(self) -> None:
        self.apply()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.restore()

    def apply(self) -> None:
        """
        Applies the new values.
        """
        # Back up previous values.
        self._prev_values = {
            key: self._get_value(key, self.DoesNotExist) for key in self._new_values
        }

        # Patch values.
        for key, value in self._new_values.items():
            # Remove the existing value first (prevents issues if the registry has
            # ``unique=True``).
            self._del_value(key)

            if value is not self.DoesNotExist:
                self._set_value(key, value)

    def restore(self) -> None:
        """
        Restores previous settings.
        """
        for key, value in self._prev_values.items():
            # Remove the existing value first (prevents issues if the registry has
            # ``unique=True``).
            self._del_value(key)

            if value is not self.DoesNotExist:
                self._set_value(key, value)

    def _get_value(self, key: typing.Hashable, default=None) -> typing.Any:
        try:
            return self.target.get_class(key)
        except RegistryKeyError:
            return default

    def _set_value(self, key: typing.Hashable, value: typing.Type[T]) -> None:
        self.target.register(key)(value)

    def _del_value(self, key: typing.Hashable) -> None:
        try:
            self.target.unregister(key)
        except RegistryKeyError:
            pass

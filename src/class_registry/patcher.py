__all__ = ["RegistryPatcher"]

import typing
from types import TracebackType

from . import RegistryKeyError
from .base import BaseMutableRegistry, KeyType, ValueType


class RegistryPatcher(typing.Generic[ValueType, KeyType]):
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
        registry: BaseMutableRegistry[ValueType, KeyType],
        *args: typing.Type[ValueType],
        **kwargs: typing.Type[ValueType],
    ) -> None:
        """
        Args:
            registry:
                A :py:class:`MutableRegistry` instance to patch.

            args:
                Classes to add to the registry.

                This behaves the same as decorating each class with
                ``@registry.register``.

                .. note::

                   ``registry.attr_name`` must be set.

            kwargs:
                Same as ``args``, except you explicitly specify the registry keys.

                In the event of a conflict, values in ``args`` override values in
                ``kwargs``.
        """
        super().__init__()

        assert registry.attr_name is not None
        for class_ in args:
            kwargs[getattr(class_, registry.attr_name)] = class_

        self.target: BaseMutableRegistry[ValueType, KeyType] = registry

        self._new_values: dict[str, typing.Type[ValueType]] = kwargs
        self._prev_values: dict[
            typing.Hashable,
            typing.Union[
                typing.Type[ValueType], typing.Type[RegistryPatcher.DoesNotExist]
            ],
        ] = {}

    def __enter__(self) -> None:
        self.apply()

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[TracebackType],
    ) -> None:
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
                if typing.TYPE_CHECKING:
                    # Convince mypy that ``value`` cannot be ``self.DoesNotExist``.
                    value = typing.cast(typing.Type[ValueType], value)

                self._set_value(key, value)

    def _get_value(
        self,
        key: typing.Hashable,
        default: typing.Any = None,
    ) -> typing.Any:
        try:
            # ``key`` is a registry key drawn from ``_new_values`` — a kwarg
            # name, or an ``attr_name`` value off a class passed positionally;
            # the target's ``get_class`` is typed against the public
            # ``KeyType``. The cast is runtime-erased — see docs/adr/002.
            return self.target.get_class(typing.cast(KeyType, key))
        except RegistryKeyError:
            return default

    def _set_value(self, key: typing.Hashable, value: typing.Type[ValueType]) -> None:
        # ``key`` comes from ``_new_values`` when patching, or from the
        # ``_prev_values`` backup when restoring; the target's ``register`` is
        # typed against the public ``KeyType``. The cast is runtime-erased —
        # see docs/adr/002.
        self.target.register(typing.cast(KeyType, key))(value)

    def _del_value(self, key: typing.Hashable) -> None:
        try:
            # Same key provenance as ``_set_value``; the target's
            # ``unregister`` is typed against the public ``KeyType``. The cast
            # is runtime-erased — see docs/adr/002.
            self.target.unregister(typing.cast(KeyType, key))
        except RegistryKeyError:
            pass

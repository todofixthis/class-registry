__all__ = [
    "AutoRegister",
    "BaseMutableRegistry",
    "BaseRegistry",
    "KeyType",
    "RegistryKeyError",
    "ValueType",
]

import sys
import typing
from abc import ABC, abstractmethod as abstract_method
from inspect import isabstract as is_abstract, isclass as is_class
from warnings import warn

# PEP 696 ``TypeVar`` defaults are native to ``typing`` in 3.13+; on 3.12 they
# come from ``typing_extensions`` (see docs/adr/001).
if sys.version_info >= (3, 13):
    from typing import TypeVar
else:
    from typing_extensions import TypeVar


class RegistryKeyError(KeyError):
    """
    Used to differentiate a registry lookup from a standard KeyError.

    This is especially useful when a registry class expects to extract values from dicts
    to generate keys.
    """

    pass


ValueType = TypeVar("ValueType")

# ``KeyType`` parametrises the public/human-readable key. Lookup keys (produced
# by ``gen_lookup_key``) stay ``Hashable`` — see docs/adr/002.
KeyType = TypeVar("KeyType", bound=typing.Hashable, default=str)

# [#53] Fix incorrect return type from ``register``
D = TypeVar("D", bound=typing.Callable[..., typing.Any])


class BaseRegistry(typing.Generic[ValueType, KeyType], ABC):
    """
    Base functionality for registries.

    The two type parameters are:

    - ``ValueType`` — the registered class, and the instance that
      :py:meth:`get` returns.
    - ``KeyType`` — the public key used to look a class up (passed to
      :py:meth:`get`/:py:meth:`register` and returned by :py:meth:`keys`).
      Defaults to :py:class:`str`.  The *internal* lookup key produced by
      :py:meth:`gen_lookup_key` is always
      :py:class:`~collections.abc.Hashable` and is deliberately not
      parametrised (see docs/adr/002).
    """

    def __contains__(self, key: KeyType) -> bool:
        """
        Returns whether the specified key is registered.
        """
        try:
            # Use :py:meth:`get_class` instead of :py:meth:`__getitem__`, to avoid
            # creating a new instance unnecessarily (i.e., prevent errors if the
            # corresponding class' constructor requires arguments).
            self.get_class(key)
        except RegistryKeyError:
            return False
        else:
            return True

    def __dir__(self) -> typing.Iterable[str]:
        """
        Attempts to return the list of registered keys.

        Raises:
            TypeError: if a key cannot be cast as a string.
        """
        return list(map(str, self.keys()))

    def __getitem__(self, key: KeyType) -> ValueType:
        """
        Shortcut for calling :py:meth:`get` with empty args/kwargs.
        """
        return self.get(key)

    def __iter__(self) -> typing.Iterator[KeyType]:
        """
        Iterates over registry keys.
        """
        return iter(self.keys())

    def __len__(self) -> int:
        """
        Returns the number of registered classes.
        """
        return sum(1 for _ in self.keys())

    def __missing__(self, key: typing.Hashable) -> typing.Type[ValueType]:
        """
        Defines what to do when trying to access an unregistered key.

        Default behaviour is to throw a typed exception, but you could override this in
        a subclass, e.g., to return a default value.

        .. note::

           This method must return a class, not an instance.
        """
        raise RegistryKeyError(key)

    @abstract_method
    def get_class(self, key: KeyType) -> typing.Type[ValueType]:
        """
        Returns the class associated with the specified key.
        """
        raise NotImplementedError()

    def get(self, key: KeyType, *args: typing.Any, **kwargs: typing.Any) -> ValueType:
        """
        Creates a new instance of the class matching the specified key.

        Args:
            key:
                The corresponding load key.
            args:
                Positional arguments passed to class initializer.
                Ignored if the class registry was initialized with a null template
                function.
            kwargs:
                Keyword arguments passed to class initializer.
                Ignored if the class registry was initialized with a null template
                function.

        References:
          - :py:meth:`__init__`
        """
        return self.create_instance(self.get_class(key), *args, **kwargs)

    @abstract_method
    def keys(self) -> typing.Iterable[KeyType]:
        """
        Returns the collection of registered keys.
        """
        raise NotImplementedError()

    def classes(self) -> typing.Iterable[typing.Type[ValueType]]:
        """
        Returns the collection of registered classes.
        """
        return iter(self.get_class(key) for key in self.keys())

    def gen_lookup_key(self, key: KeyType) -> typing.Hashable:
        """
        Used by :py:meth:`get` to generate a lookup key.

        You may override this method in a subclass, for example if you need to support
        legacy aliases, etc.

        Args:
            key:
                The key value provided to e.g., :py:meth:`__getitem__`

        Returns:
            The registry key, used to look up the corresponding class.

        Note:
            The return type is :py:class:`~collections.abc.Hashable` rather
            than ``KeyType``.  This hook may change the key's type — e.g.
            case-folding, or wrapping the key in a tuple — so the lookup key
            it produces can differ from the public key.  See docs/adr/002.
        """
        return key

    @staticmethod
    def create_instance(
        class_: typing.Type[ValueType], *args: typing.Any, **kwargs: typing.Any
    ) -> ValueType:
        """
        Prepares the return value for :py:meth:`get`.

        You may override this method in a subclass, if you want to customize the way new
        instances are created.

        Args:
            class_:
                The requested class.
            args:
                Positional keywords passed to :py:meth:`get`.
            kwargs:
                Keyword arguments passed to :py:meth:`get`.
        """
        return class_(*args, **kwargs)


class BaseMutableRegistry(BaseRegistry[ValueType, KeyType], ABC):
    """
    Extends :py:class:`BaseRegistry` with methods that can be used to modify the
    registered classes.
    """

    def __init__(self, attr_name: typing.Optional[str] = None) -> None:
        """
        Args:
            attr_name:
                If provided, :py:meth:`register` will automatically detect the key to
                use when registering new classes.
        """
        super().__init__()

        self.attr_name = attr_name

        # Map lookup keys to readable keys.
        # Only needed when :py:meth:`gen_lookup_key` is overridden, but I'm not good
        # enough at reflection black magic to figure out how to do that (:
        self._lookup_keys: dict[KeyType, typing.Hashable] = {}

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.attr_name!r})"

    def keys(self) -> typing.Iterable[KeyType]:
        """
        Returns the collection of registry keys, in the order that they were registered.
        """
        return iter(self._lookup_keys.keys())

    def items(self) -> typing.Iterable[tuple[KeyType, typing.Type[ValueType]]]:
        """
        .. warning::

           DEPRECATED: use :py:meth:`keys` or :py:meth:`classes` instead.

        Returns the collection of registered key-class pairs, in the order that they
        were registered.
        """
        warn(
            f"{type(self).__name__}.items() is deprecated and will be removed in a "
            f"future version of ClassRegistry.  Use `zip({type(self).__name__}.keys(), "
            f"{type(self).__name__}.classes())` instead.",
            DeprecationWarning,
        )
        return iter(zip(self.keys(), self.classes()))

    def values(self) -> typing.Iterable[typing.Type[ValueType]]:
        """
        .. warning::

           DEPRECATED: use :py:meth:`classes` instead.

        Returns the collection of registered classes, in the order that they were
        registered.
        """
        warn(
            f"{type(self).__name__}.values() is deprecated and will be removed in a "
            f"future version of ClassRegistry.  Use {type(self).__name__}.classes()"
            f"instead.",
            DeprecationWarning,
        )
        return self.classes()

    # [#53] Using ``D`` instead of ``ValueType`` to prevent scrubbing type info when
    # decorating a class.
    # :see: https://mypy.readthedocs.io/en/stable/generics.html#decorator-factories
    # :see: https://docs.python.org/3/library/typing.html#typing.overload
    @typing.overload
    def register(self, key: D, /) -> D:
        """Bare decorator variant"""
        ...

    @typing.overload
    def register(self, key: KeyType) -> typing.Callable[[D], D]:
        """Decorator factory variant"""
        ...

    def register(self, key: typing.Union[D, KeyType]) -> typing.Union[
        D,
        typing.Callable[[D], D],
    ]:
        """
        Decorator that registers a class with the registry.

        Example::

           registry = ClassRegistry(attr_name='widget_type')

           @registry.register
           class CustomWidget(BaseWidget):
             widget_type = 'custom'
             ...

           # Override the registry key:
           @registry.register('premium')
           class AdvancedWidget(BaseWidget):
             ...

        Args:
            key:
                The registry key to use for the registered class.
                Optional if the registry's :py:attr:`attr_name` is set.
        """
        # ``@register`` usage:
        if is_class(key):
            if typing.TYPE_CHECKING:
                key = typing.cast(D, key)

            if self.attr_name:
                attr_key = getattr(key, self.attr_name)
                lookup_key = self.gen_lookup_key(attr_key)

                self._register(lookup_key, typing.cast(typing.Type[ValueType], key))
                self._lookup_keys[attr_key] = lookup_key

                return key
            else:
                raise ValueError(
                    f"Attempting to register {key.__name__} to {type(self).__name__}"
                    f"via decorator, but `{type(self).__name__}.attr_key` is not set."
                )
        else:
            # ``@register('some_attr')`` usage:
            def _decorator(cls: D) -> D:
                key_ = typing.cast(KeyType, key)
                lookup_key_ = self.gen_lookup_key(key_)

                self._register(lookup_key_, typing.cast(typing.Type[ValueType], cls))
                self._lookup_keys[key_] = lookup_key_

                return cls

            return _decorator

    def unregister(self, key: KeyType) -> typing.Type[ValueType]:
        """
        Unregisters the class with the specified key.

        Args:
            key:
                The registry key to remove (not the registered class!).

        Returns:
            The class that was unregistered.

        Raises:
            KeyError: if the key is not registered.
        """
        result = self._unregister(self.gen_lookup_key(key))
        del self._lookup_keys[key]

        return result

    @abstract_method
    def _register(self, key: typing.Hashable, class_: typing.Type[ValueType]) -> None:
        """
        Registers a class with the registry.

        Args:
            key:
                Return value from :py:meth:`gen_lookup_key`.
        """
        raise NotImplementedError()

    @abstract_method
    def _unregister(self, key: typing.Hashable) -> typing.Type[ValueType]:
        """
        Unregisters the class at the specified key.

        Args:
            key:
                Return value from :py:meth:`gen_lookup_key`.
        """
        raise NotImplementedError()


def AutoRegister(registry: BaseMutableRegistry[ValueType, typing.Any]) -> type:
    """
    Creates a base class that automatically registers all non-abstract subclasses in the
    specified registry.

    Example::

       commands = ClassRegistry(attr_name='command_name')

       class BaseCommand(AutoRegister(commands), ABC):
         @abstractmethod
         def exec(self):
           raise NotImplementedError()

       class PrintCommand(BaseCommand):
         command_name = 'print'

         def exec(self):
           ...

       print(list(commands.items())) # [('print', PrintCommand)]

    .. important::

       Python defines abstract as "having at least one unimplemented abstract method";
       adding :py:class:`abc.ABC` as a base class is not enough.

    Args:
        registry:
            The registry that new classes will be added to.

            .. note::

               The registry's ``attr_name`` attribute must be set.


    """
    if not registry.attr_name:
        raise ValueError(f"Missing `attr_name` in {registry}.")

    class _Base:
        def __init_subclass__(cls, **kwargs: typing.Any) -> None:
            super().__init_subclass__(**kwargs)

            if not is_abstract(cls):
                registry.register(cls)

    return _Base

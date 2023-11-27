__all__ = ["AutoRegister", "BaseMutableRegistry", "BaseRegistry", "RegistryKeyError"]

import typing
from abc import ABC, abstractmethod as abstract_method
from inspect import isabstract, isclass as is_class


class RegistryKeyError(KeyError):
    """
    Used to differentiate a registry lookup from a standard KeyError.

    This is especially useful when a registry class expects to extract values from dicts
    to generate keys.
    """

    pass


class BaseRegistry(typing.Mapping, ABC):
    """
    Base functionality for registries.
    """

    def __contains__(self, key: typing.Hashable) -> bool:
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

    def __dir__(self) -> typing.List[typing.Hashable]:
        return list(self.keys())

    def __getitem__(self, key: typing.Hashable) -> typing.Any:
        """
        Shortcut for calling :py:meth:`get` with empty args/kwargs.
        """
        return self.get(key)

    def __iter__(self) -> typing.Generator[typing.Hashable, None, None]:
        """
        Returns a generator for iterating over registry keys, in the order that they
        were registered.
        """
        return self.keys()

    @abstract_method
    def __len__(self) -> int:
        """
        Returns the number of registered classes.
        """
        raise NotImplementedError(
            "Not implemented in {cls}.".format(cls=type(self).__name__),
        )

    def __missing__(self, key) -> typing.Optional[typing.Any]:
        """
        Defines what to do when trying to access an unregistered key.

        Default behaviour is to throw a typed exception, but you could override this in
        a subclass, e.g., to return a default value.
        """
        raise RegistryKeyError(key)

    @abstract_method
    def get_class(self, key: typing.Hashable) -> type:
        """
        Returns the class associated with the specified key.
        """
        raise NotImplementedError(
            "Not implemented in {cls}.".format(cls=type(self).__name__),
        )

    def get(self, key: typing.Hashable, *args, **kwargs) -> typing.Any:
        """
        Creates a new instance of the class matching the specified key.

        :param key:
            The corresponding load key.

        :param args:
            Positional arguments passed to class initializer.
            Ignored if the class registry was initialized with a null template function.

        :param kwargs:
            Keyword arguments passed to class initializer.
            Ignored if the class registry was initialized with a null template function.

        References:
          - :py:meth:`__init__`
        """
        return self.create_instance(self.get_class(key), *args, **kwargs)

    @staticmethod
    def gen_lookup_key(key: typing.Hashable) -> typing.Hashable:
        """
        Used by :py:meth:`get` to generate a lookup key.

        You may override this method in a subclass, for example if you need to support
        legacy aliases, etc.
        """
        return key

    @staticmethod
    def create_instance(class_: type, *args, **kwargs) -> typing.Any:
        """
        Prepares the return value for :py:meth:`get`.

        You may override this method in a subclass, if you want to customize the way new
        instances are created.

        :param class_:
            The requested class.

        :param args:
            Positional keywords passed to :py:meth:`get`.

        :param kwargs:
            Keyword arguments passed to :py:meth:`get`.
        """
        return class_(*args, **kwargs)

    @abstract_method
    def items(
        self,
    ) -> typing.Generator[typing.Tuple[typing.Hashable, type], None, None]:
        """
        Iterates over registered classes and their corresponding keys, in the order that
        they were registered.
        """
        raise NotImplementedError(
            "Not implemented in {cls}.".format(cls=type(self).__name__),
        )

    def keys(self) -> typing.Generator[typing.Hashable, None, None]:
        """
        Returns a generator for iterating over registry keys, in the order that they
        were registered.
        """
        for item in self.items():
            yield item[0]

    def values(self) -> typing.Generator[type, None, None]:
        """
        Returns a generator for iterating over registered classes, in the order that
        they were registered.
        """
        for item in self.items():
            yield item[1]


class BaseMutableRegistry(BaseRegistry, typing.MutableMapping, ABC):
    """
    Extends :py:class:`BaseRegistry` with methods that can be used to modify the
    registered classes.
    """

    def __init__(self, attr_name: typing.Optional[str] = None) -> None:
        """
        :param attr_name:
            If provided, :py:meth:`register` will automatically detect the key to use
            when registering new classes.
        """
        super(BaseMutableRegistry, self).__init__()

        self.attr_name = attr_name

        # Map lookup keys to readable keys.
        # Only needed when :py:meth:`gen_lookup_key` is overridden, but I'm not good
        # enough at reflection black magic to figure out how to do that (:
        self._lookup_keys: typing.Dict[typing.Hashable, typing.Hashable] = {}

    def __delitem__(self, key: typing.Hashable) -> None:
        """
        Provides alternate syntax for un-registering a class.
        """
        self._unregister(self.gen_lookup_key(key))
        del self._lookup_keys[key]

    def __repr__(self) -> str:
        return "{type}({attr_name!r})".format(
            attr_name=self.attr_name,
            type=type(self).__name__,
        )

    def __setitem__(self, key: typing.Hashable, class_: type) -> None:
        """
        Provides alternate syntax for registering a class.
        """
        lookup_key = self.gen_lookup_key(key)

        self._register(lookup_key, class_)
        self._lookup_keys[key] = lookup_key

    def register(
        self,
        key: typing.Union[typing.Hashable, type],
    ) -> typing.Callable[[type], type]:
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

        :param key:
            The registry key to use for the registered class.
            Optional if the registry's :py:attr:`attr_name` is set.
        """
        # ``@register`` usage:
        if is_class(key):
            if self.attr_name:
                attr_key = getattr(key, self.attr_name)
                lookup_key = self.gen_lookup_key(attr_key)

                self._register(lookup_key, key)
                self._lookup_keys[attr_key] = lookup_key

                return key
            else:
                raise ValueError(
                    f"Attempting to register {key.__name__} to {type(self).__name__}"
                    f"via decorator, but `{type(self).__name__}.attr_key` is not set."
                )

        # ``@register('some_attr')`` usage:
        def _decorator(cls: type) -> type:
            _lookup_key = self.gen_lookup_key(key)

            self._register(_lookup_key, cls)
            self._lookup_keys[key] = _lookup_key

            return cls

        return _decorator

    def unregister(self, key: typing.Hashable) -> type:
        """
        Unregisters the class with the specified key.

        :param key:
            The registry key to remove (not the registered class!).

        :return:
            The class that was unregistered.

        :raise:
            - :py:class:`KeyError` if the key is not registered.
        """
        result = self._unregister(self.gen_lookup_key(key))
        del self._lookup_keys[key]

        return result

    @abstract_method
    def _register(self, key: typing.Hashable, class_: type) -> None:
        """
        Registers a class with the registry.

        :param key: Has already been processed by :py:meth:`gen_lookup_key`.
        """
        raise NotImplementedError(
            "Not implemented in {cls}.".format(cls=type(self).__name__),
        )

    @abstract_method
    def _unregister(self, key: typing.Hashable) -> type:
        """
        Unregisters the class at the specified key.

        :param key: Has already been processed by :py:meth:`gen_lookup_key`.
        """
        raise NotImplementedError(
            "Not implemented in {cls}.".format(cls=type(self).__name__),
        )


def AutoRegister(registry: BaseMutableRegistry) -> type:
    """
    Creates a base class that automatically registers all non-abstract subclasses in the
    specified registry.

    IMPORTANT:  Python defines abstract as "having at least one unimplemented abstract
    method"; adding :py:class:`ABC` as a base class is not enough!

    Example::

       commands = ClassRegistry(attr_name='command_name')

       class BaseCommand(AutoRegister(commands), ABC):
         @abstractmethod
         def print(self):
           raise NotImplementedError()

       class PrintCommand(BaseCommand):
         command_name = 'print'

         def print(self):
           ...

       print(list(commands.items())) # [('print', PrintCommand)]

    :param registry:
        The registry that new classes will be added to.

        Note: the registry's ``attr_name`` attribute must be set!
    """
    if not registry.attr_name:
        raise ValueError(
            "Missing `attr_name` in {registry}.".format(registry=registry),
        )

    class _Base:
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)

            if not isabstract(cls):
                registry.register(cls)

    return _Base

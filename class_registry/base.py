import typing
from abc import ABCMeta, abstractmethod as abstract_method
from inspect import isclass as is_class


class RegistryKeyError(KeyError):
    """
    Used to differentiate a registry lookup from a standard KeyError.

    This is especially useful when a registry class expects to extract values
    from dicts to generate keys.
    """

    pass


T = typing.TypeVar("T")


class BaseRegistry(typing.Mapping[typing.Hashable, T], metaclass=ABCMeta):
    """
    Base functionality for registries.
    """

    def __contains__(self, key: typing.Hashable) -> bool:
        """
        Returns whether the specified key is registered.
        """
        try:
            # Use :py:meth:`get_class` instead of :py:meth:`__getitem__`, to
            # avoid creating a new instance unnecessarily (i.e., prevent
            # errors if the corresponding class' constructor requires
            # arguments).
            self.get_class(key)
        except RegistryKeyError:
            return False
        else:
            return True

    def __dir__(self) -> typing.List[typing.Hashable]:
        return list(self.keys())

    def __getitem__(self, key: typing.Hashable) -> T:
        """
        Shortcut for calling :py:meth:`get` with empty args/kwargs.
        """
        return self.get(key)

    def __iter__(self) -> typing.Generator[typing.Hashable, None, None]:
        """
        Returns a generator for iterating over registry keys, in the
        order that they were registered.
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

        Default behaviour is to throw a typed exception, but you could override
        this in a subclass, e.g., to return a default value.
        """
        raise RegistryKeyError(key)

    @abstract_method
    def get_class(self, key: typing.Hashable) -> typing.Type[T]:
        """
        Returns the class associated with the specified key.
        """
        raise NotImplementedError(
            "Not implemented in {cls}.".format(cls=type(self).__name__),
        )

    def get(self, key: typing.Hashable, *args, **kwargs) -> T:
        """
        Creates a new instance of the class matching the specified key.

        :param key:
            The corresponding load key.

        :param args:
            Positional arguments passed to class initializer.
            Ignored if the class registry was initialized with a null template
            function.

        :param kwargs:
            Keyword arguments passed to class initializer.
            Ignored if the class registry was initialized with a null template
            function.

        References:
          - :py:meth:`__init__`
        """
        return self.create_instance(self.get_class(key), *args, **kwargs)

    @staticmethod
    def gen_lookup_key(key: typing.Hashable) -> typing.Hashable:
        """
        Used by :py:meth:`get` to generate a lookup key.

        You may override this method in a subclass, for example if you need to
        support legacy aliases, etc.
        """
        return key

    @staticmethod
    def create_instance(class_: type, *args, **kwargs) -> T:
        """
        Prepares the return value for :py:meth:`get`.

        You may override this method in a subclass, if you want to customize
        the way new instances are created.

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
    ) -> typing.Generator[typing.Tuple[typing.Hashable, typing.Type[T]], None, None]:
        """
        Iterates over registered classes and their corresponding keys, in the
        order that they were registered.
        """
        raise NotImplementedError(
            "Not implemented in {cls}.".format(cls=type(self).__name__),
        )

    def keys(self) -> typing.Generator[typing.Hashable, None, None]:
        """
        Returns a generator for iterating over registry keys, in the order that
        they were registered.
        """
        for item in self.items():
            yield item[0]

    def values(self) -> typing.Generator[typing.Type[T], None, None]:
        """
        Returns a generator for iterating over registered classes, in the order
        that they were registered.
        """
        for item in self.items():
            yield item[1]


class BaseMutableRegistry(
    BaseRegistry[T], typing.MutableMapping[typing.Hashable, T], metaclass=ABCMeta
):
    """
    Extends :py:class:`BaseRegistry` with methods that can be used to modify
    the registered classes.
    """

    def __init__(self, attr_name: typing.Optional[str] = None) -> None:
        """
        :param attr_name:
            If provided, :py:meth:`register` will automatically detect the key
            to use when registering new classes.
        """
        super().__init__()

        self.attr_name = attr_name

        # Map lookup keys to readable keys.
        # Only needed when :py:meth:`gen_lookup_key` is overridden, but I'm not
        # good enough at reflection black magic to figure out how to do that (:
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

    def __setitem__(self, key: typing.Hashable, class_: typing.Type[T]) -> None:
        """
        Provides alternate syntax for registering a class.
        """
        lookup_key = self.gen_lookup_key(key)

        self._register(lookup_key, class_)
        self._lookup_keys[key] = lookup_key

    def register(
        self,
        key: typing.Union[typing.Hashable, typing.Type[T]],
    ) -> typing.Union[
        typing.Type[T],
        typing.Callable[[typing.Type[T]], typing.Type[T]],
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

        :param key:
            The registry key to use for the registered class.
            Optional if the registry's :py:attr:`attr_name` is set.
        """
        # ``@register`` usage:
        if is_class(key):
            if self.attr_name:
                attr_key = getattr(key, self.attr_name)
                lookup_key = self.gen_lookup_key(attr_key)

                # Note that ``getattr`` will raise an AttributeError if the
                # class doesn't have the required attribute.
                self._register(lookup_key, key)
                self._lookup_keys[attr_key] = lookup_key

                return key
            else:
                raise ValueError(
                    "Attempting to register {cls} to {registry} via decorator,"
                    " but `{registry}.attr_key` is not set.".format(
                        cls=key.__name__,
                        registry=type(self).__name__,
                    )
                )

        # ``@register('some_attr')`` usage:
        def _decorator(cls: typing.Type[T]) -> typing.Type[T]:
            lookup_key_ = self.gen_lookup_key(key)

            self._register(lookup_key_, cls)
            self._lookup_keys[key] = lookup_key_

            return cls

        return _decorator

    def unregister(self, key: typing.Hashable) -> typing.Type[T]:
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
    def _register(self, key: typing.Hashable, class_: typing.Type[T]) -> None:
        """
        Registers a class with the registry.

        :param key: Has already been processed by :py:meth:`gen_lookup_key`.
        """
        raise NotImplementedError(
            "Not implemented in {cls}.".format(cls=type(self).__name__),
        )

    @abstract_method
    def _unregister(self, key: typing.Hashable) -> typing.Type[T]:
        """
        Unregisters the class at the specified key.

        :param key: Has already been processed by :py:meth:`gen_lookup_key`.
        """
        raise NotImplementedError(
            "Not implemented in {cls}.".format(cls=type(self).__name__),
        )

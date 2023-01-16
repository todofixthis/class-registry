import typing
from abc import ABCMeta, abstractmethod as abstract_method
from collections import OrderedDict
from functools import cmp_to_key
from inspect import isclass as is_class

__all__ = [
    'BaseRegistry',
    'ClassRegistry',
    'BaseMutableRegistry',
    'RegistryKeyError',
    'SortedClassRegistry',
]


class RegistryKeyError(KeyError):
    """
    Used to differentiate a registry lookup from a standard KeyError.

    This is especially useful when a registry class expects to extract values
    from dicts to generate keys.
    """
    pass


class BaseRegistry(typing.Mapping, metaclass=ABCMeta):
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

    def __getitem__(self, key: typing.Hashable) -> object:
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
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )

    def __missing__(self, key) -> typing.Optional[object]:
        """
        Defines what to do when trying to access an unregistered key.

        Default behaviour is to throw a typed exception, but you could override
        this in a subclass, e.g., to return a default value.
        """
        raise RegistryKeyError(key)

    @abstract_method
    def get_class(self, key: typing.Hashable) -> type:
        """
        Returns the class associated with the specified key.
        """
        raise NotImplementedError(
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )

    def get(self, key: typing.Hashable, *args, **kwargs) -> object:
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
    def create_instance(class_: type, *args, **kwargs) -> object:
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
    def items(self) -> typing.Generator[
        typing.Tuple[typing.Hashable, type], None, None]:
        """
        Iterates over registered classes and their corresponding keys, in the
        order that they were registered.
        """
        raise NotImplementedError(
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )

    def keys(self) -> typing.Generator[typing.Hashable, None, None]:
        """
        Returns a generator for iterating over registry keys, in the order that
        they were registered.
        """
        for item in self.items():
            yield item[0]

    def values(self) -> typing.Generator[type, None, None]:
        """
        Returns a generator for iterating over registered classes, in the order
        that they were registered.
        """
        for item in self.items():
            yield item[1]


class BaseMutableRegistry(BaseRegistry, typing.MutableMapping,
    metaclass=ABCMeta):
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
        super(BaseMutableRegistry, self).__init__()

        self.attr_name = attr_name

        # Map lookup keys to readable keys.
        # Only needed when :py:meth:`gen_lookup_key` is overridden, but I'm not
        # good enough at reflection black magic to figure out how to do that (:
        self._lookup_keys: typing.Dict[typing.Hashable, typing.Hashable] = {}

    def __delitem__(self, key: typing.Hashable) -> None:
        """
        Provides alternate syntax for un-registering a class.
        """
        self._unregister(type(self).gen_lookup_key(key))
        del self._lookup_keys[key]

    def __repr__(self) -> str:
        return '{type}({attr_name!r})'.format(
            attr_name=self.attr_name,
            type=type(self).__name__,
        )

    def __setitem__(self, key: typing.Hashable,
            class_: type) -> None:
        """
        Provides alternate syntax for registering a class.
        """
        lookup_key = type(self).gen_lookup_key(key)

        self._register(lookup_key, class_)
        self._lookup_keys[key] = lookup_key

    def register(self,
            key: typing.Union[typing.Hashable, type]) -> \
            typing.Callable[[type], type]:
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
                lookup_key = type(self).gen_lookup_key(attr_key)

                # Note that ``getattr`` will raise an AttributeError if the
                # class doesn't have the required attribute.
                self._register(lookup_key, key)
                self._lookup_keys[attr_key] = lookup_key

                return key
            else:
                raise ValueError(
                    'Attempting to register {cls} to {registry} via decorator,'
                    ' but `{registry}.attr_key` is not set.'.format(
                        cls=key.__name__,
                        registry=type(self).__name__,
                    )
                )

        # ``@register('some_attr')`` usage:
        def _decorator(cls: type) -> type:
            lookup_key = type(self).gen_lookup_key(key)

            self._register(lookup_key, cls)
            self._lookup_keys[key] = lookup_key

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
        result = self._unregister(type(self).gen_lookup_key(key))
        del self._lookup_keys[key]

        return result

    @abstract_method
    def _register(self, key: typing.Hashable,
            class_: type) -> None:
        """
        Registers a class with the registry.

        :param key: Has already been processed by :py:meth:`gen_lookup_key`.
        """
        raise NotImplementedError(
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )

    @abstract_method
    def _unregister(self, key: typing.Hashable) -> type:
        """
        Unregisters the class at the specified key.

        :param key: Has already been processed by :py:meth:`gen_lookup_key`.
        """
        raise NotImplementedError(
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )


class ClassRegistry(BaseMutableRegistry):
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
        super(ClassRegistry, self).__init__(attr_name)

        self.unique = unique

        self._registry: typing.OrderedDict[
            typing.Hashable, type] = OrderedDict()

    def __len__(self) -> int:
        """
        Returns the number of registered classes.
        """
        return len(self._registry)

    def __repr__(self) -> str:
        return '{type}(attr_name={attr_name!r}, unique={unique!r})'.format(
            attr_name=self.attr_name,
            type=type(self).__name__,
            unique=self.unique,
        )

    def get_class(self, key: typing.Hashable) -> typing.Optional[type]:
        """
        Returns the class associated with the specified key.
        """
        lookup_key = type(self).gen_lookup_key(key)

        try:
            return self._registry[lookup_key]
        except KeyError:
            return self.__missing__(lookup_key)

    def items(self) -> typing.Generator[
        typing.Tuple[typing.Hashable, type], None, None]:
        """
        Iterates over all registered classes, in the order they were added.
        """
        for key, lookup_key in self._lookup_keys.items():
            yield key, self._registry[lookup_key]

    def _register(self, key: typing.Hashable,
            class_: type) -> None:
        """
        Registers a class with the registry.

        :param key: Has already been processed by :py:meth:`gen_lookup_key`.
        """
        if key in ['', None]:
            raise ValueError(
                'Attempting to register class {cls} '
                'with empty registry key {key!r}.'.format(
                    cls=class_.__name__,
                    key=key,
                ),
            )

        if self.unique and (key in self._registry):
            raise RegistryKeyError(
                '{cls} with key {key!r} is already registered.'.format(
                    cls=class_.__name__,
                    key=key,
                ),
            )

        self._registry[key] = class_

    def _unregister(self, key: typing.Hashable) -> type:
        """
        Unregisters the class at the specified key.

        :param key: Has already been processed by :py:meth:`gen_lookup_key`.
        """
        return (
            self._registry.pop(key)
            if key in self._registry
            else self.__missing__(key)
        )


class SortedClassRegistry(ClassRegistry):
    """
    A ClassRegistry that uses a function to determine sort order when
    iterating.
    """

    def __init__(
            self,
            sort_key: typing.Union[
                str,
                typing.Callable[
                    [
                        typing.Tuple[typing.Hashable, type, typing.Hashable],
                        typing.Tuple[typing.Hashable, type, typing.Hashable]
                    ],
                    int,
                ],
            ],
            attr_name: typing.Optional[str] = None,
            unique: bool = False,
            reverse: bool = False,
    ) -> None:
        """
        :param sort_key:
            Attribute name or callable, used to determine the sort value.

            If callable, must accept two tuples of (key, class, lookup_key).

        :param attr_name:
            If provided, :py:meth:`register` will automatically detect the key
            to use when registering new classes.

        :param unique:
            Determines what happens when two classes are registered with the
            same key:

            - ``True``: The second class will replace the first one.
            - ``False``: A ``ValueError`` will be raised.

        :param reverse:
            Whether to reverse the sort ordering.
        """
        super(SortedClassRegistry, self).__init__(attr_name, unique)

        self._sort_key = (
            sort_key
            if callable(sort_key)
            else self.create_sorter(sort_key)
        )

        self.reverse = reverse

    def items(self) -> typing.Generator[
        typing.Tuple[typing.Hashable, type], None, None]:
        for (key, class_, _) in sorted(
                # Provide human-readable key and lookup key to the sorter...
                ((key, class_, type(self).gen_lookup_key(key)) for
                        (key, class_) in super().items()),
                key=self._sort_key,
                reverse=self.reverse,
        ):
            # ... but for parity with other ClassRegistry types, only include
            # the human-readable key in the result.
            yield key, class_

    @staticmethod
    def create_sorter(sort_key: str) -> typing.Callable[
        [
            typing.Tuple[typing.Hashable, type],
            typing.Tuple[typing.Hashable, type]
        ],
        int,
    ]:
        """
        Given a sort key, creates a function that can be used to sort items
        when iterating over the registry.
        """

        def sorter(a, b):
            a_attr = getattr(a[1], sort_key)
            b_attr = getattr(b[1], sort_key)

            return (a_attr > b_attr) - (a_attr < b_attr)

        return cmp_to_key(sorter)

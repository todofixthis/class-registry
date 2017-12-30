# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from abc import ABCMeta, abstractmethod as abstract_method
from collections import OrderedDict
from functools import cmp_to_key
from inspect import isclass as is_class
from typing import Any, Callable, Generator, Hashable, Iterator, \
    Mapping, MutableMapping, Optional, Text, Tuple, Union

from six import PY2, iteritems, with_metaclass

__all__ = [
    'BaseRegistry',
    'ClassRegistry',
    'MutableRegistry',
    'RegistryKeyError',
    'SortedClassRegistry',
]


class RegistryKeyError(KeyError):
    """
    Used to differentiate a registry lookup from a standard KeyError.

    This is especially useful when a registry class expects to extract
    values from dicts to generate keys.
    """
    pass


class BaseRegistry(with_metaclass(ABCMeta, Mapping)):
    """
    Base functionality for registries.
    """
    def __contains__(self, key):
        """
        Returns whether the specified key is registered.
        """
        try:
            # Use :py:meth:`get_class` instead of :py:meth:`__getitem__`
            # in case the registered class' initializer requires
            # arguments.
            self.get_class(key)
        except RegistryKeyError:
            return False
        else:
            return True

    def __dir__(self):
        return list(self.keys())

    def __getitem__(self, key):
        """
        Shortcut for calling :py:meth:`get` with empty args/kwargs.
        """
        return self.get(key)

    def __iter__(self):
        # type: () -> Generator[Hashable]
        """
        Returns a generator for iterating over registry keys, in the
        order that they were registered.
        """
        return self.keys()

    @abstract_method
    def __len__(self):
        # type: () -> int
        """
        Returns the number of registered classes.
        """
        raise NotImplementedError(
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )

    def __missing__(self, key):
        """
        Returns the result (or raises an exception) when the requested
        key can't be found in the registry.
        """
        raise RegistryKeyError(key)

    @abstract_method
    def get_class(self, key):
        """
        Returns the class associated with the specified key.
        """
        raise NotImplementedError(
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )

    def get(self, key, *args, **kwargs):
        """
        Creates a new instance of the class matching the specified key.

        :param key:
            The corresponding load key.

        :param args:
            Positional arguments passed to class initializer.
            Ignored if the class registry was initialized with a null
            template function.

        :param kwargs:
            Keyword arguments passed to class initializer.
            Ignored if the class registry was initialized with a null
            template function.

        References:
          - :py:meth:`__init__`
        """
        return self.create_instance(self.get_class(key), *args, **kwargs)

    @staticmethod
    def gen_lookup_key(key):
        # type: (Any) -> Hashable
        """
        Used by :py:meth:`get` to generate a lookup key.

        You may override this method in a subclass, for example if you
        need to support legacy aliases, etc.
        """
        return key

    @staticmethod
    def create_instance(class_, *args, **kwargs):
        # type: (type, *Any, **Any) -> Any
        """
        Prepares the return value for :py:meth:`get`.

        You may override this method in a subclass, if you want to
        customize the way new instances are created.

        :param class_:
            The requested class.

        :param args:
            Positional keywords passed to :py:meth:`get`.

        :param kwargs:
            Keyword arguments passed to :py:meth:`get`.
        """
        return class_(*args, **kwargs)

    @abstract_method
    def items(self):
        # type: () -> Generator[Tuple[Hashable, type]]
        """
        Iterates over registered classes and their corresponding keys,
        in the order that they were registered.

        Note: For compatibility with Python 3, this method should
        return a generator.
        """
        raise NotImplementedError(
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )

    def keys(self):
        # type: () -> Generator[Hashable]
        """
        Returns a generator for iterating over registry keys, in the
        order that they were registered.

        Note: For compatibility with Python 3, this method should
        return a generator.
        """
        for item in self.items():
            yield item[0]

    def values(self):
        # type: () -> Generator[type]
        """
        Returns a generator for iterating over registered classes, in
        the order that they were registered.

        Note: For compatibility with Python 3, this method should
        return a generator.
        """
        for item in self.items():
            yield item[1]

    # Add some compatibility aliases to make class registries behave
    # more like dicts in Python 2.
    if PY2:
        def iteritems(self):
            """
            Included for compatibility with :py:data:`six.iteritems`.
            Do not invoke directly!
            """
            return self.items()

        def iterkeys(self):
            """
            Included for compatibility with :py:data:`six.iterkeys`.
            Do not invoke directly!
            """
            return self.keys()

        def itervalues(self):
            """
            Included for compatibility with :py:data:`six.itervalues`.
            Do not invoke directly!
            """
            return self.values()


class MutableRegistry(with_metaclass(ABCMeta, BaseRegistry, MutableMapping)):
    """
    Extends :py:class:`BaseRegistry` with methods that can be used to
    modify the registered classes.
    """
    def __init__(self, attr_name=None):
        # type: (Optional[Text]) -> None
        """
        :param attr_name:
            If provided, :py:meth:`register` will automatically detect
            the key to use when registering new classes.
        """
        super(MutableRegistry, self).__init__()

        self.attr_name = attr_name

    def __delitem__(self, key):
        # type: (Hashable) -> None
        """
        Provides alternate syntax for un-registering a class.
        """
        self._unregister(key)

    def __repr__(self):
        return '{type}({attr_name!r})'.format(
            attr_name   = self.attr_name,
            type        = type(self).__name__,
        )

    def __setitem__(self, key, class_):
        # type: (Text, type) -> None
        """
        Provides alternate syntax for registering a class.
        """
        self._register(key, class_)

    def register(self, key):
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
        if is_class(key):
            if self.attr_name:
                # Note that ``getattr`` will raise an AttributeError if
                # the class doesn't have the required attribute.
                self._register(getattr(key, self.attr_name), key)
                return key
            else:
                raise ValueError('Registry key is required.')

        def _decorator(cls):
            self._register(key, cls)
            return cls
        return _decorator

    def unregister(self, key):
        # type: (Any) -> type
        """
        Unregisters the class with the specified key.

        :param key:
            The registry key to remove (not the registered class!).

        :return:
            The class that was unregistered.

        :raise:
            - :py:class:`KeyError` if the key is not registered.
        """
        return self._unregister(self.gen_lookup_key(key))

    @abstract_method
    def _register(self, key, class_):
        # type: (Hashable, type) -> None
        """
        Registers a class with the registry.
        """
        raise NotImplementedError(
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )

    @abstract_method
    def _unregister(self, key):
        # type: (Hashable) -> type
        """
        Unregisters the class at the specified key.
        """
        raise NotImplementedError(
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )



class ClassRegistry(MutableRegistry):
    """
    Maintains a registry of classes and provides a generic factory for
    instantiating them.
    """
    def __init__(self, attr_name=None, unique=False):
        # type: (Optional[Text], bool) -> None
        """
        :param attr_name:
            If provided, :py:meth:`register` will automatically detect
            the key to use when registering new classes.

        :param unique:
            Determines what happens when two classes are registered with
            the same key:

            - ``True``: The second class will replace the first one.
            - ``False``: A ``ValueError`` will be raised.
        """
        super(ClassRegistry, self).__init__(attr_name)

        self.unique = unique

        self._registry = OrderedDict()

    def __len__(self):
        # type: () -> int
        """
        Returns the number of registered classes.
        """
        return len(self._registry)

    def __repr__(self):
        return '{type}(attr_name={attr_name!r}, unique={unique!r})'.format(
            attr_name   = self.attr_name,
            type        = type(self).__name__,
            unique      = self.unique,
        )

    def get_class(self, key):
        """
        Returns the class associated with the specified key.
        """
        lookup_key = self.gen_lookup_key(key)

        try:
            return self._registry[lookup_key]
        except KeyError:
            return self.__missing__(lookup_key)

    def items(self):
        # type: () -> Iterator[Tuple[Hashable, type]]
        """
        Iterates over all registered classes, in the order they were
        added.
        """
        return iteritems(self._registry)

    def _register(self, key, class_):
        # type: (Hashable, type) -> None
        """
        Registers a class with the registry.
        """
        if key in ['', None]:
            raise ValueError(
                'Attempting to register class {cls} '
                'with empty registry key {key!r}.'.format(
                    cls = class_.__name__,
                    key = key,
                ),
            )

        if self.unique and (key in self._registry):
            raise RegistryKeyError(
                '{cls} with key {key!r} is already registered.'.format(
                    cls = class_.__name__,
                    key = key,
                ),
            )

        self._registry[key] = class_

    def _unregister(self, key):
        # type: (Hashable) -> type
        """
        Unregisters the class at the specified key.
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
            sort_key,                   # type: Union[Text, Callable[[Tuple[Hashable, type], Tuple[Hashable, type]], int]]
            attr_name       = None,     # type: Optional[Text]
            unique          = False,    # type: bool
            reverse         = False,    # type: bool
    ):
        """
        :param sort_key:
            Attribute name or callable, used to determine the sort value.

            If callable, must accept two tuples of (key, class).

        :param attr_name:
            If provided, :py:meth:`register` will automatically detect
            the key to use when registering new classes.

        :param unique:
            Determines what happens when two classes are registered with
            the same key:

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

    def items(self):
        # type: () -> Iterator[Tuple[Hashable, type]]
        return sorted(
            iteritems(self._registry),
                key     = self._sort_key,
                reverse = self.reverse,
        )

    @staticmethod
    def create_sorter(sort_key):
        """
        Given a sort key, creates a function that can be used to sort
        items when iterating over the registry.
        """
        def sorter(a, b):
            # type: (Tuple[Hashable, type], Tuple[Hashable, type]) -> int
            a_attr = getattr(a[1], sort_key)
            b_attr = getattr(b[1], sort_key)

            return (a_attr > b_attr) - (a_attr < b_attr)

        return cmp_to_key(sorter)

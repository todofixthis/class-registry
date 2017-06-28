# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from collections import OrderedDict
from importlib import import_module
from inspect import isclass as is_class
from typing import Any, Callable, Generator, Hashable, Iterable, Iterator, \
    Mapping, Optional, Set, Text, Tuple, Union

from six import PY2, iteritems, text_type

__all__ = [
    'ClassRegistry',
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


class ClassRegistry(Mapping):
    """
    Maintains a registry of classes and provides a generic factory for
    instantiating them.
    """
    def __init__(self, attr_name=None, unique=False, preload_modules=None):
        # type: (Optional[Text], bool, Iterable[Text]) -> None
        """
        :param attr_name:
            If provided, :py:meth:`register` will automatically detect
            the key to use when registering new classes.

        :param unique:
            Determines what happens when two classes are registered with
            the same key:

            - ``True``: The second class will replace the first one.
            - ``False``: A ``ValueError`` will be raised.

        :param preload_modules:
            Dotted paths of modules to load before retrieving values
            from the registry.

            This is useful if you have lots of classes across multiple
            modules that need to be registered.
        """
        super(ClassRegistry, self).__init__()

        self._registry = OrderedDict()

        self.attr_name  = attr_name
        self.unique     = unique

        # Ensure the value is coerced to a set so that it's easy for
        # code to append values to it at any time.
        self.preload_modules = set(preload_modules or ()) # type: Set[Text]

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

    def __len__(self):
        # type: () -> int
        """
        Returns the number of registered classes.
        """
        return len(self._registry)

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
        return self._registry.pop(self.gen_lookup_key(key))

    def get(self, key, *args, **kwargs):
        """
        Creates a new instance of the class matching the specified key.

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
        if self.preload_modules:
            for module_path in self.preload_modules:
                import_module(module_path)

            self.preload_modules = set()

        return self.create_instance(self.get_class(key), *args, **kwargs)

    def get_class(self, key):
        """
        Returns the class associated with the specified key.
        """
        lookup_key = self.gen_lookup_key(key)

        try:
            return self._registry[lookup_key]
        except KeyError as e:
            raise RegistryKeyError(text_type(e))

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
        # type: (type, ...) -> Any
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

    def items(self):
        # type: () -> Generator[Tuple[Hashable, type]]
        """
        Iterates over registered classes and their corresponding keys,
        in the order that they were registered.

        Note: For compatibility with Python 3, this method returns a
        generator.
        """
        for item in self._items():
            yield item

    if PY2:
        iteritems = items
        """
        Included for compatibility with :py:data:`six.iteritems`.
        Do not invoke directly!
        """

    def keys(self):
        # type: () -> Generator[Hashable]
        """
        Returns a generator for iterating over registry keys, in the
        order that they were registered.

        Note: For compatibility with Python 3, this method returns a
        generator.
        """
        for item in self._items():
            yield item[0]

    if PY2:
        iterkeys = keys
        """
        Included for compatibility with :py:data:`six.iterkeys`.
        Do not invoke directly!
        """

    def values(self):
        # type: () -> Generator[type]
        """
        Returns a generator for iterating over registered classes, in
        the order that they were registered.

        Note: For compatibility with Python 3, this method returns a
        generator.
        """
        for item in self._items():
            yield item[1]

    if PY2:
        itervalues = values
        """
        Included for compatibility with :py:data:`six.itervalues`.
        Do not invoke directly!
        """

    def _items(self):
        # type: () -> Iterator[Tuple[Hashable, type]]
        """
        Iterates over all registered classes, in the order they were
        added.
        """
        return iteritems(self._registry)

    def _register(self, key, cls):
        # type: (Hashable, type) -> None
        """
        Registers a class with the registry.
        """
        if key in ['', None]:
            raise ValueError(
                'Attempting to register class {cls} '
                'with empty registry key {key!r}.'.format(
                    cls = cls.__name__,
                    key = key,
                ),
            )

        if self.unique and (key in self._registry):
            raise RegistryKeyError(
                '{cls} with key {key!r} is already registered.'.format(
                    cls = cls.__name__,
                    key = key,
                ),
            )

        self._registry[key] = cls


class SortedClassRegistry(ClassRegistry):
    """
    A ClassRegistry that uses a function to determine sort order when
    iterating.
    """
    def __init__(
            self,
            sort_key,                   # type: Union[Text, Callable[[Tuple[Hashable, type]], int]]
            attr_name       = None,     # type: Optional[Text]
            unique          = False,    # type: bool
            preload_modules = None,     # type: Optional[Iterable[Text]]
    ):
        """
        :param sort_key:
            Attribute name or callable, used to determine the sort value.

            If callable, must accept a tuple of (key, class).

        :param attr_name:
            If provided, :py:meth:`register` will automatically detect
            the key to use when registering new classes.

        :param unique:
            Determines what happens when two classes are registered with
            the same key:

            - ``True``: The second class will replace the first one.
            - ``False``: A ``ValueError`` will be raised.

        :param preload_modules:
            Dotted paths of modules to load before retrieving values
            from the registry.

            This is useful if you have lots of classes across multiple
            modules that need to be registered.
        """
        super(SortedClassRegistry, self)\
            .__init__(attr_name, unique, preload_modules)

        self._sort_key = sort_key

    def _items(self):
        # type: () -> Iterator[Tuple[Hashable, type]]
        return sorted(iteritems(self._registry), key=self._sort_key)

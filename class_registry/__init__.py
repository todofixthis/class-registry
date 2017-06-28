# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from inspect import isclass as is_class
from typing import Any, Callable, Dict, Generator, Hashable, Iterable, \
    Iterator, Mapping, Optional, Set, Text, Tuple, Union

from collections import OrderedDict, defaultdict
from importlib import import_module
from six import PY2, iteritems, iterkeys, text_type


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


class RegistryPatcher(object):
    """
    Creates a context in which classes are temporarily registered with
    a class registry, then removed when the context exits.
    """
    class DoesNotExist(object):
        """
        Used to identify a value that did not exist before we started.
        """
        pass

    def __init__(self, registry, *args, **kwargs):
        """
        :param registry:
            The :py:class:`ClassRegistry` instance to patch.

        :param args:
            Classes to add to the registry.

            This behaves the same as decorating each class with
            ``@registry.register``.

            Note: ``registry.attr_name`` must be set!

        :param kwargs:
            Same as ``args``, except you explicitly specify the
            registry keys.

            In the event of a conflict, values in ``args`` override
            values in ``kwargs``.
        """
        super(RegistryPatcher, self).__init__()

        for class_ in args:
            kwargs[getattr(class_, registry.attr_name)] = class_

        self.target = registry

        self._new_values  = kwargs
        self._prev_values = {}

    def __enter__(self):
        self.apply()

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.restore()

    def apply(self):
        """
        Applies the new values.
        """
        # Back up previous values.
        self._prev_values = {
            key: self._get_value(key, self.DoesNotExist)
                for key in self._new_values
        }

        # Patch values.
        for key, value in iteritems(self._new_values):
            if value is self.DoesNotExist:
                self._del_value(key)
            else:
                self._set_value(key, value)

    def restore(self):
        """
        Restores previous settings.
        """
        # Restore previous settings.
        for key, value in iteritems(self._prev_values):
            if value is self.DoesNotExist:
                self._del_value(key)
            else:
                self._set_value(key, value)

    def _get_value(self, key, default=None):
        try:
            return self.target.get_class(key)
        except RegistryKeyError:
            return default

    def _set_value(self, key, value):
        self.target.register(key)(value)

    def _del_value(self, key):
        self.target.unregister(key)


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


class ClassRegistryInstanceCache(object):
    """
    Wraps a ClassRegistry instance, caching instances as they are
    created.

    This allows you to create [multiple] registries that cache
    INSTANCES locally (so that they can be scoped and garbage-
    collected), while keeping the CLASS registry separate.

    Note that the internal class registry is copied by reference, so
    any classes that are registered afterward are accessible to
    both the ClassRegistry and the ClassRegistryInstanceCache.
    """
    def __init__(self, class_registry, *args, **kwargs):
        # type: (ClassRegistry, ...) -> None
        """
        :param class_registry:
            The wrapped ClassRegistry.

        :param args:
            Positional arguments passed to the class registry's
            template when creating new instances.

        :param kwargs:
            Keyword arguments passed to the class registry's template
            function when creating new instances.
        """
        super(ClassRegistryInstanceCache, self).__init__()

        self._registry  = class_registry
        self._cache     = {}

        self._key_map = defaultdict(list) # type: Dict[Hashable, list]

        self._template_args     = args
        self._template_kwargs   = kwargs

    def __getitem__(self, key):
        """
        Returns the cached instance associated with the specified key.
        """
        cache_key = self.gen_cache_key(key)

        if cache_key not in self._cache:
            lookup_key = self.gen_lookup_key(key)

            # Map lookup keys to cache keys so that we can iterate over
            # them in the correct order.
            # :py:meth:`__iter__`
            self._key_map[lookup_key].append(cache_key)

            self._cache[cache_key] =\
                self._registry.get(
                    lookup_key,
                    *self._template_args,
                    **self._template_kwargs
                )

        return self._cache[cache_key]

    def __iter__(self):
        # type: () -> Generator[Hashable]
        """
        Returns a generator for iterating over cached instances, using
        the wrapped registry to determine sort order.

        If a key has not been accessed yet, it will not be included.
        """
        for lookup_key in iterkeys(self._registry):
            for cache_key in self._key_map[lookup_key]:
                yield self._cache[cache_key]

    def warm_cache(self):
        """
        Warms up the cache, ensuring that an instance is created for
        every key in the registry.

        Note that this method does not account for any classes that may
        be added to the wrapped ClassRegistry in the future.
        """
        for key in iterkeys(self._registry):
            self.__getitem__(key)

    def gen_cache_key(self, key):
        # type: (Any) -> Hashable
        """
        Generates a key that can be used to store/lookup values in the
        instance cache.

        :param key:
            Value provided to :py:meth:`__getitem__`.
        """
        return self.gen_lookup_key(key)

    def gen_lookup_key(self, key):
        # type: (Any) -> Hashable
        """
        Generates a key that can be used to store/lookup values in the
        wrapped :py:class:`ClassRegistry` instance.

        This method is only invoked in the event of a cache miss.

        :param key:
            Value provided to :py:meth:`__getitem__`.
        """
        return self._registry.gen_lookup_key(key)

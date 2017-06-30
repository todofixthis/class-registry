# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from abc import ABCMeta
from inspect import isabstract as is_abstract

from class_registry.registry import MutableRegistry

__all__ = [
    'AutoRegister',
]


def AutoRegister(registry, base_type=ABCMeta):
    # type: (MutableRegistry, type) -> type
    """
    Creates a metaclass that automatically registers all non-abstract
    subclasses in the specified registry.

    IMPORTANT:  Python defines abstract as "having at least one
    unimplemented abstract method"; specifying :py:class:`ABCMeta` as
    the metaclass is not enough!

    Example::

       commands = ClassRegistry(attr_name='command_name')

       # Specify ``AutoRegister`` as the metaclass:
       class BaseCommand(with_metaclass(AutoRegister(commands))):
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

    :param base_type:
        The base type of the metaclass returned by this function.

        99.99% of the time, this should be :py:class:`ABCMeta`.
    """
    if not registry.attr_name:
        raise ValueError(
            'Missing `attr_name` in {registry}.'.format(registry=registry),
        )

    class _metaclass(base_type):
        def __init__(self, what, bases=None, attrs=None):
            super(_metaclass, self).__init__(what, bases, attrs)

            if not is_abstract(self):
                registry.register(self)

    return _metaclass

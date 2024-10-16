# This module is deprecated and will be removed in a future version of ClassRegistry, so
# not going to bother getting the type hints just right (aka it was too difficult for
# me to figure out, and so I looked for a justification for giving up XD).
# type: ignore
__all__ = ["AutoRegister"]

from abc import ABCMeta
from inspect import isabstract as is_abstract
from warnings import warn

from .base import BaseMutableRegistry


def AutoRegister(registry: BaseMutableRegistry, base_type: type = ABCMeta) -> type:
    """
    DEPRECATED: Use ``class_registry.base.AutoRegister`` instead (returns a base class
    instead of a metaclass).

    Creates a metaclass that automatically registers all non-abstract subclasses in the
    specified registry.

    Example::

       commands = ClassRegistry(attr_name='command_name')

       # Specify ``AutoRegister`` as the metaclass:
       class BaseCommand(metaclass=AutoRegister(commands)):
         @abstractmethod
         def print(self):
           raise NotImplementedError()

       class PrintCommand(BaseCommand):
         command_name = 'print'

         def print(self):
           ...

       print(list(commands.items())) # [('print', PrintCommand)]

    .. important::

       Python defines abstract as "having at least one unimplemented abstract method";
       adding :py:class:`abc.ABC` as a base class is not enough.

    :param registry:
        The registry that new classes will be added to.

        .. note::

           The registry's ``attr_name`` attribute must be set.

    :param base_type:
        The base type of the metaclass returned by this function.

        99.99% of the time, this should be :py:class:`abc.ABCMeta`.
    """
    warn(
        "class_registry.auto_register.AutoRegister is deprecated and will be removed in"
        "a future version of ClassRegistry.  Use class_registry.base.AutoRegister"
        "instead (returns a base class instead of a metaclass).  See"
        "https://github.com/todofixthis/class-registry/issues/14 for more information.",
        DeprecationWarning,
    )

    if not registry.attr_name:
        raise ValueError(f"Missing `attr_name` in {registry}.")

    class _metaclass(base_type):
        def __init__(self, what, bases=None, attrs=None):
            super().__init__(what, bases, attrs)

            if not is_abstract(self):
                registry.register(self)

    return _metaclass

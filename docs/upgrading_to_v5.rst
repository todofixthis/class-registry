Upgrading to ClassRegistry v5
=============================
`ClassRegistry v5 <https://github.com/todofixthis/class-registry/releases/tag/5.0.0>`_
introduces some changes that can break code that was previously using ClassRegistry v4.
If you are upgrading from ClassRegistry v4 to ClassRegistry v5, you'll need to make the
following changes:

Type Parameters
---------------
I thought I'd start this off with some good news 😺

If a :py:class:`ClassRegistry` always returns objects derived from a particular
base class, you can now provide a
`type parameter <https://typing.readthedocs.io/en/latest/source/generics.html#generics>`_
to help with type checking, autocomplete, etc.:

.. code-block:: python

   # Add type parameter ``[Pokemon]``:
   pokedex = ClassRegistry[Pokemon]()

   # Your IDE will automatically infer that ``fighter1`` is a ``Pokemon``.
   fighter1 = pokedex['fire']

:py:class:`ClassRegistryInstanceCache` now inherits the
`type parameter <https://typing.readthedocs.io/en/latest/source/generics.html#generics>`_
from the :py:class:`ClassRegistry` that it wraps in order to help with type checking,
autocompletion, etc.:

.. code-block:: python

   # Add type parameter ``[Pokemon]``:
   registry = ClassRegistry[Pokemon]()

   # The ``ClassRegistryInstanceCache`` inherits the type parameters from the
   # ``ClassRegistry`` that it wraps.
   pokedex = ClassRegistryInstanceCache(registry)

   # Your IDE will automatically infer that ``fire_fighter`` is a ``Pokemon``.
   fire_fighter = pokedex['fire']

Alternatively, you can apply the type parameter to the
:py:class:`ClassRegistryInstanceCache` directly:

.. code-block:: python

   pokedex = ClassRegistryInstanceCache[Pokemon](registry)

Imports
-------
In ClassRegistry v5 many symbols were removed from the top-level ``class_registry``
namespace.  The table below shows how to import each symbol in ClassRegistry v5 in your
code:

.. table

======================================  ===================================================================
Symbol                                  How to Import in ClassRegistry v5
======================================  ===================================================================
:py:func:`AutoRegister`                 ``from class_registry.base import AutoRegister``
:py:class:`ClassRegistry`               ``from class_registry import Classregistry`` (unchanged)
:py:class:`ClassRegistryInstanceCache`  ``from class_registry.cache import ClassRegistryInstanceCache``
:py:class:`EntryPointClassRegistry`     ``from class_registry.entry_points import EntryPointClassRegistry``
:py:class:`RegistryKeyError`            ``from class_registry import RegistryKeyError`` (unchanged)
:py:class:`RegistryPatcher`             ``from class_registry.patcher import RegistryPatcher``
:py:class:`SortedClassRegistry`         ``from class_registry.registry import SortedClassRegistry``
======================================  ===================================================================

AutoRegister
------------
In ClassRegistry v5, :py:func:`AutoRegister` now returns a base class instead of a
metaclass.  The example below shows how to update classes that use
:py:func:`AutoRegister`:

ClassRegistry v4:

.. code-block:: py

   from class_registry import AutoRegister

      class MyBaseClass(metaclass=AutoRegister(my_registry)):
          ...

ClassRegistry v5:

.. code-block:: py

   from abc import ABC
   from class_registry.base import AutoRegister

   class MyBaseClass(AutoRegister(my_registry), ABC):
       ...

.. note::

   If this is a non-trivial change for your code, you can continue to use the
   (deprecated) metaclass version of :py:func:`AutoRegister` which is located at
   ``class_registry.auto_register.AutoRegister``.

   The metaclass version of :py:func:`AutoRegister` will be removed in a future version
   of ClassRegistry, so it's recommended that you update your code.  If you need help,
   `post in the ClassRegistry issue tracker <https://github.com/todofixthis/class-registry/issues>`_,
   and I'll have a look 🙂

Removed/Renamed Methods
-----------------------
The following methods have been removed or renamed:

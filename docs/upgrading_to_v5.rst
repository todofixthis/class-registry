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
Now for the tricky parts.

In ClassRegistry v5 many symbols were removed from the top-level ``class_registry``
namespace.  The table below shows how to import each symbol in ClassRegistry v5 in your
code:

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

.. code-block:: python

   from class_registry import AutoRegister

   class MyBaseClass(metaclass=AutoRegister(my_registry)):
       ...

ClassRegistry v5:

.. code-block:: python

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

Other Changes
-------------

BaseRegistry
^^^^^^^^^^^^

.. important::
   :py:class:`BaseRegistry` no longer implements :py:class:`typing.Mapping` due to
   violations of the Liskov Substitutability Principle:

   .. code-block:: python

      >>> isinstance(ClassRegistry(), typing.Mapping)
      False

   If your code relies on the previous behaviour,
   `post in the ClassRegistry issue tracker <https://github.com/todofixthis/class-registry/issues>`_,
   so that we can find an alternative solution.

Additionally, the following methods have been deprecated and will be removed in a future
version:

- :py:meth:`BaseRegistry.items` is deprecated. If you still need this functionality, use
  the following workaround:

  ClassRegistry v4:

  .. code-block:: python

     registry.items()

  ClassRegistry v5:

  .. code-block:: python

     zip(registry.keys(), registry.classes())

- :py:meth:`BaseRegistry.values` is now renamed to :py:meth:`BaseRegistry.classes`:

  ClassRegistry v4:

  .. code-block:: python

     registry.values()

  ClassRegistry v5:

  .. code-block:: python

     registry.classes()

BaseMutableRegistry
^^^^^^^^^^^^^^^^^^^

.. important::
   :py:class:`BaseMutableRegistry` no longer implements
   :py:class:`typing.MutableMapping` due to violations of the Liskov Substitutability
   Principle:

   .. code-block:: python

      >>> isinstance(ClassRegistry(), typing.MutableMapping)
      False

   If your code relies on the previous behaviour,
   `post in the ClassRegistry issue tracker <https://github.com/todofixthis/class-registry/issues>`_,
   so that we can find an alternative solution.

- ``BaseMutableRegistry.__delitem__()`` method has been removed. Use the
  ``unregister()`` method instead:

  ClassRegistry v4:

  .. code-block:: python

     del registry["fire"]

  ClassRegistry v5:

  .. code-block:: python

     registry.unregister("fire")

- ``BaseMutableRegistry.__setitem__()`` method has been removed. Use the ``register()``
  method instead:

  ClassRegistry v4:

  .. code-block:: python

     registry["fire"] = Charizard

  ClassRegistry v5:

  .. code-block:: python

     registry.register("fire")(Charizard)

  .. note::

     If you initialised the :py:class:`ClassRegistry` with ``unique=True``, you will
     need to ``unregister()`` the key first:

     .. code-block:: python

        >>> registry = ClassRegistry(unique=True)
        >>> registry.register(Charmander)

        # Attempting to register over an existing class will fail.
        >>> registry.register("fire")(Charizard)
        RegistryKeyError: <class Charmander>

        # Instead, unregister the current class and then register the new one.
        >>> registry.unregister("fire")
        >>> registry.register("fire")(Charizard)

New Methods
-----------
The following methods have been added:

- :py:meth:`BaseRegistry.__dir__` method returns the list of registered keys as strings.
- :py:meth:`BaseRegistry.__len__` method returns the number of registered symbols.

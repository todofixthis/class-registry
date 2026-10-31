Upgrading to ClassRegistry v6
==============================

`ClassRegistry v6 <https://github.com/todofixthis/class-registry/releases/tag/6.0.0>`_
changes the default registry key type. That affects only type checking, but mypy
doesn't always report it (see the warning under `Registry keys now default to str`_).
It also makes two small changes that can fail at runtime:

- :py:meth:`~class_registry.base.BaseRegistry.gen_lookup_key` is now an instance
  method (see `gen_lookup_key is now an instance method`_).
- The ``T`` type variables are gone (see `The T type variables are gone`_).

One runtime change is a fix rather than a break: iterating over a
``ClassRegistryInstanceCache`` whose registry overrides ``gen_lookup_key`` now
yields every instance, where v5 silently skipped those whose lookup key differed
from their key.

Registry keys now default to :py:class:`str`
----------------------------------------------
Previously, a bare ``ClassRegistry[Foo]`` resolved its key type to
:py:class:`~typing.Hashable`. In ClassRegistry v6, it resolves to
:py:class:`str` instead.

.. note::

   See :doc:`iterating_over_registries` for the full picture of how key types work.

If your code uses non-:py:class:`str` keys under a bare ``ClassRegistry[Foo]``,
or an unannotated ``ClassRegistry(...)`` (which mypy resolves to
``ClassRegistry[Any, str]``), every call that takes a key fails type checking.
mypy reports one of::

   error: Invalid index type "int" for "ClassRegistry[Pokemon, str]"; expected type "str"  [index]
   error: Argument 1 to "get" of "BaseRegistry" has incompatible type "int"; expected "str"  [arg-type]
   error: Argument 1 to "get_class" of "ClassRegistry" has incompatible type "int"; expected "str"  [arg-type]
   error: Argument 1 to "unregister" of "BaseMutableRegistry" has incompatible type "int"; expected "str"  [arg-type]
   error: Unsupported operand types for in ("int" and "ClassRegistry[Pokemon, str]")  [operator]
   error: No overload variant of "register" of "BaseMutableRegistry" matches argument type "int"  [call-overload]

The names in quotes come from your code.

.. warning::

   mypy can't see keys that come from an ``attr_name`` attribute, so a registry
   that only registers that way and only iterates over its keys reports nothing
   after upgrading — yet every key is now typed :py:class:`str`. Your code still
   runs, but mypy now gets it wrong in two ways. With
   ``ClassRegistry[Handler]('code')`` and a handler whose ``code = 404``:

   - mypy now accepts ``[k.upper() for k in handlers]``, which v5 rejected, and
     which fails at runtime as it always did::

        AttributeError: 'int' object has no attribute 'upper'

   - an existing ``if isinstance(k, int):`` branch becomes unreachable, so mypy
     silently skips checking it. Only ``--warn-unreachable`` (which ``--strict``
     doesn't enable) reports it::

        error: Subclass of "str" and "int" cannot exist: have distinct disjoint bases  [unreachable]
        error: Statement is unreachable  [unreachable]

   Declare the key type of every registry whose keys aren't :py:class:`str`,
   whether or not mypy complains.

If you pass the registry to a ``ClassRegistryInstanceCache`` or ``RegistryPatcher``
annotated with only a value type, mypy reports one of::

   error: Argument 1 to "ClassRegistryInstanceCache" has incompatible type "ClassRegistry[Pokemon, int]"; expected "ClassRegistry[Pokemon, str]"  [arg-type]
   error: Argument 1 to "RegistryPatcher" has incompatible type "ClassRegistry[Pokemon, int]"; expected "BaseMutableRegistry[Pokemon, str]"  [arg-type]

Both now take the key type as a second argument too, defaulting to :py:class:`str`;
see `The T type variables are gone`_.

For example:

.. code-block:: python

   # ClassRegistry v5:  ``pokedex`` is a ``ClassRegistry[Pokemon, typing.Hashable]``
   # ClassRegistry v6+: ``pokedex`` is a ``ClassRegistry[Pokemon, str]``
   pokedex: ClassRegistry[Pokemon] = ClassRegistry('pokedex_id')

   @pokedex.register
   class Geodude(Pokemon):
       pokedex_id = 74

   # The following code will **run** correctly, but mypy reports error:
   # error: Invalid index type "int" for "ClassRegistry[Pokemon, str]"; expected type "str"
   fighter1 = pokedex[74]

**Runtime behaviour is unchanged.** Your code still works; only the type checker
objects. To fix it, declare the key type explicitly:

.. code-block:: python

   # Pass a second type argument to specify the key type (``int`` in this case).
   pokedex: ClassRegistry[Pokemon, int] = ClassRegistry('pokedex_id')

Restoring pre-v6 behaviour
~~~~~~~~~~~~~~~~~~~~~~~~~~
If your keys vary in type, or you'd rather not name a specific key type, declare
:py:class:`~typing.Hashable` to restore the original permissive behaviour:

.. code-block:: python

   from collections.abc import Hashable

   pokedex: ClassRegistry[Pokemon, Hashable] = ClassRegistry('pokedex_id')

Public keys vs. internal lookup keys
------------------------------------
.. note::

   This section only applies if you have written a derived class that overrides
   :py:meth:`~class_registry.base.BaseRegistry.gen_lookup_key`. See
   :ref:`overriding-lookup-keys` for more information.

The key type you declare (``str``, ``int``, ``Hashable``, or otherwise) is the
**public** key: what you pass to ``get``/``register`` and get back from ``keys()``.

The **lookup** key — what
:py:meth:`~class_registry.base.BaseRegistry.gen_lookup_key` *returns* — is a separate
type, chosen independently of the public key. The base class types it
:py:class:`~typing.Hashable` rather than your key type on purpose: the hook is
free to reshape the key — narrowing it, wrapping it in a tuple, etc. — so its return
value may be a completely different type.

The public key is usually the *wider* of the two. Consider a ``Pokedex`` migrating from
lookup by pokédex ID to lookup by name. While the migration is under way, callers pass
either an ``int`` ID or a ``str`` name, so the public key is widened to
``int | str`` — yet every pokémon is still identified internally by exactly one
``int``:

.. code-block:: python

   from class_registry import ClassRegistry


   # ClassRegistry v6+: default key type is ``str``, so we declare the public key
   # type explicitly.
   class Pokedex(ClassRegistry[Pokemon, int | str]):
       def gen_lookup_key(self, key: int | str) -> int:
           # A name (``str``) is translated to its pokédex ID; an ID is already a
           # lookup key, so it passes straight through.
           if isinstance(key, str):
               return pokedex_id_from_name(key)

           return key


   # Callers don't need to care how the key is translated internally.
   red_pokedex = Pokedex('pokedex_id')
   charmander = red_pokedex['charmander']
   squirtle = red_pokedex[7]

Declare the narrowest public key type your callers need.
:py:class:`~typing.Hashable` also works, but then mypy can't tell that a
non-``str`` key is an ``int``, so returning it from a hook annotated ``-> int``
fails::

   error: Incompatible return value type (got "Hashable", expected "int")  [return-value]

``gen_lookup_key`` is now an instance method
--------------------------------------------
:py:meth:`~class_registry.base.BaseRegistry.gen_lookup_key` used to be a
``@staticmethod``. In ClassRegistry v6 it is an instance method, so that its
argument takes the registry's key type.

Calling it on a registry instance works as before. Calling it on a registry
*class* fails at runtime, unless that class (or one of its parents) overrides
``gen_lookup_key`` with a ``@staticmethod``::

   TypeError: BaseRegistry.gen_lookup_key() missing 1 required positional argument: 'key'

If your class overrides ``gen_lookup_key`` with an instance method, the message
names your class instead of ``BaseRegistry``. mypy flags the same call before it
runs, with a pair of errors::

   error: Missing positional argument "key" in call to "gen_lookup_key" of "BaseRegistry"  [call-arg]
   error: Argument 1 to "gen_lookup_key" of "BaseRegistry" has incompatible type "str"; expected "BaseRegistry[Never, str]"  [arg-type]

Again, the names in quotes come from your code.

To fix it, call the method on a registry instance:

.. code-block:: python

   pokedex = ClassRegistry('element')

   # ClassRegistry v5 only:
   lookup_key = ClassRegistry.gen_lookup_key('fire')

   # ClassRegistry v6+:
   lookup_key = pokedex.gen_lookup_key('fire')

A ``@staticmethod`` override of ``gen_lookup_key`` still works, even called on
your class — unless it delegates to the base implementation, which a
``@staticmethod`` can only reach through the class:

.. code-block:: python

   from collections.abc import Hashable


   class FoldingRegistry(ClassRegistry[Pokemon]):
       @staticmethod
       def gen_lookup_key(key: str) -> Hashable:
           # Fails in v6 with the TypeError above.
           return ClassRegistry.gen_lookup_key(key.casefold())

Convert an override like that to an instance method, and call
``super().gen_lookup_key()`` instead:

.. code-block:: python

   class FoldingRegistry(ClassRegistry[Pokemon]):
       def gen_lookup_key(self, key: str) -> Hashable:
           return super().gen_lookup_key(key.casefold())

Annotate ``key`` with your registry's key type: ``str`` here, since
``ClassRegistry[Pokemon]`` defaults to it. A narrower annotation, such as ``str`` on
a ``ClassRegistry[Pokemon, Hashable]``, fails::

   error: Argument 1 of "gen_lookup_key" is incompatible with supertype "class_registry.base.BaseRegistry"; supertype defines the argument type as "Hashable"  [override]

Once converted, calling it on the class itself —
``FoldingRegistry.gen_lookup_key('Fire')`` — breaks as described above, so move
those calls onto an instance first.

The ``T`` type variables are gone
---------------------------------
Each of ``class_registry.base``, ``.cache``, ``.entry_points``, ``.patcher`` and
``.registry`` defined a private ``T`` type variable. ClassRegistry v6 replaces them with
two type variables shared across the package, both exported from
``class_registry.base``:

- ``ValueType``: the registered class.
- ``KeyType``: the public key type, which defaults to :py:class:`str`.

Importing ``T`` now fails at runtime::

   ImportError: cannot import name 'T' from 'class_registry.base'

The module in the message may be any of the five above. mypy reports::

   error: Module "class_registry.base" has no attribute "T"  [attr-defined]

To fix it, import ``ValueType`` instead. If your class wraps a registry, a
``ClassRegistryInstanceCache`` or a ``RegistryPatcher``, add ``KeyType`` too: all
three take it as a second type argument, which silently defaults to
:py:class:`str`, so passing in a registry with other keys fails as in
`Registry keys now default to str`_. Your own class then behaves the same way:
annotate code that uses it with both type arguments
(``RegistryWrapper[Pokemon, int]``).

.. code-block:: python

   from typing import Generic

   from class_registry import ClassRegistry
   from class_registry.base import KeyType, ValueType


   class RegistryWrapper(Generic[ValueType, KeyType]):
       def __init__(self, registry: ClassRegistry[ValueType, KeyType]) -> None:
           self.registry = registry

       def first_key(self) -> KeyType:
           return next(iter(self.registry.keys()))

List ``KeyType`` after ``ValueType``, and after any of your own type variables.
A type variable with a default can't precede one without, so
``Generic[KeyType, ValueType]`` fails as soon as the class is defined::

   TypeError: Type parameter ~ValueType without a default follows type parameter with a default

mypy reports::

   error: "ValueType" cannot appear after "KeyType" in type parameter list because it has no default type  [misc]

Subclasses that override methods or attributes
----------------------------------------------
Methods and attributes that return or store keys now use the key type. If your
subclass, or your own :py:class:`~class_registry.base.BaseRegistry`
implementation, annotates one of them with :py:class:`~typing.Hashable` keys, mypy
rejects the override:

- ``keys()`` returns ``Iterable[KeyType]``, and ``__iter__()`` returns
  ``Iterator[KeyType]``.
- ``EntryPointClassRegistry._get_cache()`` returns ``dict[str, type[ValueType]]``,
  and ``EntryPointClassRegistry._cache`` is ``dict[str, type[ValueType]] | None``.
- ``BaseMutableRegistry._lookup_keys`` is ``dict[KeyType, Hashable]``.

For example::

   error: Return type "Iterable[Hashable]" of "keys" incompatible with return type "Iterable[str]" in supertype "class_registry.base.BaseRegistry"  [override]
   error: Return type "Iterator[Hashable]" of "__iter__" incompatible with return type "Iterator[str]" in supertype "class_registry.base.BaseRegistry"  [override]
   error: Return type "dict[Hashable, type[Base]]" of "_get_cache" incompatible with return type "dict[str, type[Base]]" in supertype "class_registry.entry_points.EntryPointClassRegistry"  [override]

To fix it, declare the registry's key type (as in
`Registry keys now default to str`_) and match your override's annotation to it.
Runtime behaviour is unchanged.

``EntryPointClassRegistry`` takes only a value type: entry point names are always
:py:class:`str`, so its key type is fixed. Pass it ``str`` keys.

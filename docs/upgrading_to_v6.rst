Upgrading to ClassRegistry v6
==============================

`ClassRegistry v6 <https://github.com/todofixthis/class-registry/releases/tag/6.0.0>`_
changes the default registry key type. This is a **type-checker-visible only** change:
runtime behaviour is unchanged. If your type checker flags an error after upgrading,
read on.

Registry keys now default to :py:class:`str`
----------------------------------------------
Previously, a bare ``ClassRegistry[Foo]`` resolved its key type to
:py:class:`~typing.Hashable`. In ClassRegistry v6, it resolves to
:py:class:`str` instead.

.. note::

   See :doc:`iterating_over_registries` for the full picture of how key types work.

If your code registers non-:py:class:`str` keys under a bare ``ClassRegistry[Foo]``,
your type checker will report an error such as::

   error: Invalid index type ... for "ClassRegistry[..., str]"; expected type "str"

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

   from typing import Hashable

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
:py:class:`~typing.Hashable` — yet every pokémon is still identified internally by
exactly one ``int``:

.. code-block:: python

   from typing import Hashable

   from class_registry import ClassRegistry

   # ClassRegistry v6+: default key type is ``str`` so we have to explicitly declare
   # the public key type as ``Hashable`` here.
   class Pokedex(ClassRegistry[Pokemon, Hashable]):
       @staticmethod
       def gen_lookup_key(key: Hashable) -> int:
           # A name (``str``) is translated to its pokédex ID; an ID is already a
           # lookup key, so it passes straight through.
           if isinstance(key, str):
               return pokedex_id_from_name(key)

           return key

   # ``Pokedex`` public key type is ``typing.Hashable`` — callers don't need to
   # care how the key is translated internally.
   red_pokedex = Pokedex('element')
   charmander = red_pokedex['fire']
   squirtle = red_pokedex[7]

.. tip::

   :py:class:`~typing.Hashable` may actually be too wide for your use case. Take the
   opportunity to see if you can use a more specific key type.

   For example:

   .. code-block:: python

      # Callers can use ``int`` or ``str`` keys to look up pokemon, not any arbitrary
      # hashable value.
      class Pokedex(ClassRegistry[Pokemon, int | str]):
          # ...

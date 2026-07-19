Upgrading to ClassRegistry v6
==============================

`ClassRegistry v6 <https://github.com/todofixthis/class-registry/releases/tag/6.0.0>`_
changes the default registry key type.  This is a **type-checker-visible only** change:
runtime behaviour is unchanged.  If your type checker flags an error after upgrading,
read on.

Registry keys now default to :py:class:`str`
----------------------------------------------
Previously, a bare ``ClassRegistry[Foo]`` resolved its key type to
:py:class:`~collections.abc.Hashable`.  In ClassRegistry v6, it resolves to
:py:class:`str` instead.

.. note::

   See :doc:`iterating_over_registries` for the full picture of how key types work.

If your code registers non-:py:class:`str` keys under a bare ``ClassRegistry[Foo]``,
your type checker will report an error such as::

   error: Argument 1 to "get_class" of "ClassRegistry" has incompatible type "int"; expected "str"  [arg-type]

For example:

.. code-block:: python

   # ClassRegistry v5:  ``pokedex`` is a ``ClassRegistry[Pokemon, typing.Hashable]``
   # ClassRegistry v6+: ``pokedex`` is a ``ClassRegistry[Pokemon, str]``
   pokedex: ClassRegistry[Pokemon] = ClassRegistry('pokedex_id')

   @pokedex.register
   class Geodude(Pokemon):
       pokedex_id = 74

   pokedex.get_class(74)  # error: incompatible type "int"; expected "str"

**Runtime behaviour is unchanged.** Your code still works; only the type checker
objects. To fix it, declare the key type explicitly:

.. code-block:: python

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
The key type you declare (``str``, ``int``, ``Hashable``, or otherwise) is the
**public** key: what you pass to ``get``/``register`` and get back from ``keys()``.

The **lookup** key — what
:py:meth:`~class_registry.base.BaseRegistry.gen_lookup_key` *returns* — is typed
:py:class:`~typing.Hashable`, *not* your registry's key type.  The base class declares
it that way deliberately: the hook is free to reshape the key (for example, wrapping it
in a tuple), so its result is not guaranteed to be a key type at all.  Don't assume
``gen_lookup_key`` hands you back a value of your registry's key type.

Its ``key`` *parameter*, by contrast, is typed as your registry's key type.  If you
override the hook to support aliases or case-folding, you may keep that signature
or widen it — see :doc:`advanced_topics` for an example.

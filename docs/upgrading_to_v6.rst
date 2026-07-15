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
:py:class:`str` instead — see :doc:`iterating_over_registries` for the full
picture of how key types work.

If your code registers non-:py:class:`str` keys under a bare ``ClassRegistry[Foo]``,
your type checker will report an error such as:

.. code-block:: text

   error: Argument 1 to "get_class" of "ClassRegistry" has incompatible type "int"; expected "str"  [arg-type]

For example:

.. code-block:: python

   pokedex: ClassRegistry[Pokemon] = ClassRegistry('pokedex_id')

   @pokedex.register
   class Geodude(Pokemon):
       pokedex_id = 74

   pokedex.get_class(74)  # error: incompatible type "int"; expected "str"

**Runtime behaviour is unchanged.**  Your code still works; only the type checker
objects.  To fix it, declare the key type explicitly:

.. code-block:: python

   pokedex: ClassRegistry[Pokemon, int] = ClassRegistry('pokedex_id')

The ``Hashable`` escape hatch
-----------------------------
If your keys vary in type, or you'd rather not name a specific key type, declare
:py:class:`~collections.abc.Hashable` to restore the original permissive behaviour:

.. code-block:: python

   from collections.abc import Hashable

   pokedex: ClassRegistry[Pokemon, Hashable] = ClassRegistry('pokedex_id')

A trap to avoid: ``KeyType`` is invariant
-----------------------------------------
Having switched to ``Hashable``, you might write a helper that accepts it:

.. code-block:: python

   def takes_permissive(registry: ClassRegistry[Pokemon, Hashable]) -> None:
       ...

   pokedex: ClassRegistry[Pokemon] = ClassRegistry('element')
   takes_permissive(pokedex)

This fails to type-check:

.. code-block:: text

   error: Argument 1 to "takes_permissive" has incompatible type "ClassRegistry[Pokemon, str]"; expected "ClassRegistry[Pokemon, Hashable]"  [arg-type]

Notice that mypy renders the bare ``ClassRegistry[Pokemon]`` as
``ClassRegistry[Pokemon, str]`` — the default from a moment ago, already applied.
A registry's key type is invariant: it appears both where you pass keys in
(``get``, ``register``) and where they come out (``keys()``), so a
``ClassRegistry[Pokemon, str]`` is not interchangeable with a
``ClassRegistry[Pokemon, Hashable]``, even though ``str`` is a ``Hashable``.

Pick one key type for a given registry and use it consistently, in the registry's
declaration and in any helper that accepts that registry.

Public keys vs. the internal lookup key
------------------------------------------
The key type you declare (``str``, ``int``, ``Hashable``, or otherwise) is the
**public** key: what you pass to ``get``/``register`` and get back from ``keys()``.

The **lookup** key — what
:py:meth:`~class_registry.base.BaseRegistry.gen_lookup_key` *returns* — is typed
:py:class:`~collections.abc.Hashable`, not your registry's key type.  The base
class declares it that way deliberately: the hook is free to reshape the key (for
example, wrapping it in a tuple), so its result is not guaranteed to be a key type
at all.  Don't assume ``gen_lookup_key`` hands you back a value of your registry's
key type.

Its ``key`` *parameter*, by contrast, is typed as your registry's key type.  If you
override the hook to support aliases or case-folding, you may keep that signature
or widen it — see :doc:`advanced_topics` for an example.

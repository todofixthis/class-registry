ClassRegistry
=============
.. toctree::
   :maxdepth: 1
   :caption: Contents:

   getting_started
   service_registries
   iterating_over_registries
   entry_points
   advanced_topics
   upgrading_to_v5
   upgrading_to_v6
   api


ClassRegistry
=============
At the intersection of the Registry and Factory patterns lies the ``ClassRegistry``:

- Define global factories that generate new class instances based on configurable keys.
- Seamlessly create powerful service registries.
- Integrate with setuptools's ``entry_points`` system to make your registries infinitely
  extensible by 3rd-party libraries!
- And more!

Upgrading from an Earlier Version
----------------------------------
.. warning::

   Major releases of ClassRegistry introduce breaking changes. If you are upgrading to a
   new major version of ClassRegistry, please consult the migration docs.

   If you are upgrading through more than one major version (e.g. v4 -> v6), it's
   usually easier to upgrade through each major release incrementally (e.g. v4 -> v5 ->
   v6) rather than make all the changes for each major release all at once.

   - v5 -> v6: :doc:`upgrading_to_v6`
   - v4 -> v5: :doc:`upgrading_to_v5`

Getting Started
---------------
Create a registry using the ``class_registry.ClassRegistry`` class, then decorate any
classes that you wish to register with its ``register`` method:

.. code-block:: python

   from class_registry import ClassRegistry

   pokedex = ClassRegistry()

   @pokedex.register('fire')
   class Charizard(Pokemon):
       ...

   @pokedex.register('grass')
   class Bulbasaur(Pokemon):
       ...

   @pokedex.register('water')
   class Squirtle(Pokemon):
       ...

To create a class instance from a registry, use the subscript operator:

.. code-block:: python

   # Charizard, I choose you!
   fighter1 = pokedex['fire']

   # CHARIZARD fainted!
   # How come my rival always picks the type that my pokémon is weak against??
   fighter2 = pokedex['water']

.. tip::

   If a :py:class:`ClassRegistry` always returns objects derived from a
   particular base class, you can provide a
   `type parameter <https://typing.readthedocs.io/en/latest/source/generics.html#generics>`_
   to help with type checking, autocomplete, etc.:

   .. code-block:: python

      # Add type parameter ``[Pokemon]``:
      pokedex = ClassRegistry[Pokemon]()

      # Your IDE will automatically infer that ``fighter1`` is a ``Pokemon``.
      fighter1 = pokedex['fire']

   Registry keys are typed as :py:class:`str` by default; see "Specifying
   the Key Type" in :doc:`iterating_over_registries` to use a different key
   type.

Advanced Usage
--------------
There's a whole lot more you can do with ClassRegistry, including:

- Provide args and kwargs to new class instances.
- Automatically register non-abstract classes.
- Integrate with setuptools's ``entry_points`` system so that 3rd-party libraries can
  add their own classes to your registries.
- Wrap your registry in an instance cache to create a service registry.
- And more!

To learn more about what you can do with ClassRegistry,
:doc:`keep reading! </getting_started>`

Requirements
------------
ClassRegistry is known to be compatible with the following Python versions:

- 3.14
- 3.13
- 3.12

.. note::

   I'm only one person, so to keep from getting overwhelmed, I'm only committing to
   supporting the 3 most recent versions of Python.  ClassRegistry's code is pretty
   simple, so it's likely to be compatible with versions not listed here; there just
   won't be any test coverage to prove it 😇

Installation
------------
Install the latest stable version via pip::

   pip install phx-class-registry

.. important::

   Make sure to install `phx-class-registry`, **not** `class-registry`.  I created the
   latter at a previous job years ago, and after I left they never touched that project
   again and stopped responding to my emails — so in the end I had to fork it 🤷

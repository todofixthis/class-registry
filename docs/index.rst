ClassRegistry
=============
.. toctree::
   :maxdepth: 1
   :caption: Contents:

   getting_started
   factories_vs_registries
   iterating_over_registries
   entry_points
   advanced_topics


ClassRegistry
=============
At the intersection of the Registry and Factory patterns lies the
``ClassRegistry``:

- Define global factories that generate new class instances based on
  configurable keys.
- Seamlessly create powerful service registries.
- Integrate with setuptools's ``entry_points`` system to make your registries
  infinitely extensible by 3rd-party libraries!
- And more!

Getting Started
---------------
Create a registry using the ``class_registry.ClassRegistry`` class, then
decorate any classes that you wish to register with its ``register`` method:

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
   fighter2 = pokedex['grass']

Advanced Usage
--------------
There's a whole lot more you can do with ClassRegistry, including:

- Provide args and kwargs to new class instances.
- Automatically register non-abstract classes.
- Integrate with setuptools's ``entry_points`` system so that 3rd-party
  libraries can add their own classes to your registries.
- Wrap your registry in an instance cache to create a service registry.
- And more!

To learn more about what you can do with ClassRegistry,
:doc:`keep reading! </getting_started>`

Requirements
------------
ClassRegistry is known to be compatible with the following Python versions:

- 3.11
- 3.10
- 3.9

.. note::
   ClassRegistry's code is pretty simple, so it's likely to be compatible with
   versions not listed here; there's just no test coverage to prove it 😇

Installation
------------
Install the latest stable version via pip::

   pip install phx-class-registry

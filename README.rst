.. image:: https://travis-ci.org/eflglobal/class-registry.svg?branch=master
   :target: https://travis-ci.org/eflglobal/class-registry
.. image:: https://readthedocs.org/projects/class-registry/badge/?version=latest
   :target: http://class-registry.readthedocs.io/

=============
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

---------------
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

For more advanced usage, `check out the documentation on RTD`_!

------------
Requirements
------------

ClassRegistry is compatible with Python versions 3.6, 3.5 and 2.7.

------------
Installation
------------

Install the latest stable version via pip::

   pip install class-registry



.. _check out the documentation on rtd: https://class-registry.readthedocs.org/

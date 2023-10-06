Entry Points Integration
========================
A serially-underused feature of setuptools is its `entry points`_.  This feature
allows you to expose a pluggable interface in your project.  Other libraries
can then declare entry points and inject their own classes into your class
registries!

Let's see what that might look like in practice.

First, we'll create a package with its own ``pyproject.toml`` file:

.. code-block:: toml

   # generation_2/pyproject.toml
   [project]
   name="pokemon-generation-2"
   description="Extends the pokédex with generation 2 pokémon!"

   [project.entry-points.pokemon]
   grass="gen2.pokemon:Chikorita"
   fire="gen2.pokemon:Cyndaquil"
   water="gen2.pokemon:Totodile"

Note that we declared some ``pokemon`` entry points.

.. tip::

   If your project uses ``setup.py``, it will look like this instead:

   .. code-block:: python

      # generation_2/setup.py
      from setuptools import setup

      setup(
        name = 'pokemon-generation-2',
        description = 'Extends the pokédex with generation 2 pokémon!',

        entry_points = {
          'pokemon': [
            'grass=gen2.pokemon:Chikorita',
            'fire=gen2.pokemon:Cyndaquil',
            'water=gen2.pokemon:Totodile',
          ],
        },
      )

   Note that ``setup.py`` is being phased out in favour of ``pyproject.toml``.
   `Learn more about pyproject.toml.`_

Let's see what happens once the ``pokemon-generation-2`` package is installed::

   % pip install pokemon-generation-2
   % ipython

   In [1]: from class_registry import EntryPointClassRegistry

   In [2]: pokedex = EntryPointClassRegistry('pokemon')

   In [3]: list(pokedex.items())
   Out[3]:
   [('grass', <class 'gen2.pokemon.Chikorita'>),
    ('fire', <class 'gen2.pokemon.Cyndaquil'>),
    ('water', <class 'gen2.pokemon.Totodile'>)]

Simply declare an :py:class:`EntryPointClassRegistry` instance, and it will
automatically find any classes registered to that entry point group across every
single installed project in your virtualenv!

Reverse Lookups
---------------
From time to time, you may need to perform a "reverse lookup":  Given a class or
instance, you want to determine which registry key is associated with it.

For :py:class:`ClassRegistry`, performing a reverse lookup is simple because the
registry key is (usually) defined by an attribute on the class itself.

However, :py:class:`EntryPointClassRegistry` uses an external source to define
the registry keys, so it's a bit tricky to go back and find the registry key for
a given class.

If you would like to enable reverse lookups in your application, you can provide
an optional ``attr_name`` argument to the registry's initializer, which will
cause the registry to "brand" every object it returns with the corresponding
registry key.

.. code-block:: python

   In [1]: from class_registry import EntryPointClassRegistry

   In [2]: pokedex = EntryPointClassRegistry('pokemon', attr_name='element')

   In [3]: fire_pokemon = pokedex['fire']

   In [4]: fire_pokemon.element
   Out[4]: 'fire'

   In [5]: water_pokemon_class = pokedex.get_class('water')

   In [6]: water_pokemon_class.element
   Out[6]: 'water'

We set ``attr_name='element'`` when initializing the
:py:class:`EntryPointClassRegistry`, so it set the ``element`` attribute
on every class and instance that it returned.

.. caution::

   If a class already has an attribute with the same name, the registry will
   overwrite it.

.. _entry points: http://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins
.. _Learn more about pyproject.toml.: https://stackoverflow.com/q/62983756/5568265

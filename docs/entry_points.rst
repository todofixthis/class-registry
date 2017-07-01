========================
Entry Points Integration
========================
A serially-underused feature of setuptools is its `entry points`_.  This feature
allows you to expose a pluggable interface in your project.  Other libraries
can then declare entry points and inject their own classes into your class
registries!

Let's see what that might look like in practice.

First, we'll create a package with its own ``setup.py`` file:

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

Note that we declared some ``pokemon`` entry points.

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

.. _entry points: http://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins

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
~~~~~~~~~~~~~~

There's a whole lot more you can do with ClassRegistry, including:

- Provide args and kwargs to new class instances.
- Automatically register non-abstract classes.
- Integrate with setuptools's ``entry_points`` system so that 3rd-party
  libraries can add their own classes to your registries.
- Wrap your registry in an instance cache to create a service registry.
- And more!

For more advanced usage, check out the documentation on `ReadTheDocs`_!


Requirements
------------

ClassRegistry is compatible with Python versions 3.7, 3.6, 3.5 and 2.7.


Installation
------------

Install the latest stable version via pip::

   pip install class-registry


Running Unit Tests
------------------
To run unit tests after installing from source::

  python setup.py test

This project is also compatible with `tox`_, which will run the unit tests in
different virtual environments (one for each supported version of Python).

To run the unit tests, it is recommended that you use the `detox`_ library.
detox speeds up the tests by running them in parallel.

Install the package with the ``test-runner`` extra to set up the necessary
dependencies, and then you can run the tests with the ``tox`` command::

  pip install -e .[test-runner]
  tox

.. tip::
  To run tests for multiple Python versions in parallel::

    # Python 3.7 only
    tox -p all

    # Python 3.6 or earlier
    pip install detox
    detox

Documentation
-------------
Documentation is available on `ReadTheDocs`_.

If you are installing from source (see above), you can also build the
documentation locally:

#. Install extra dependencies (you only have to do this once)::

      pip install '.[docs-builder]'

#. Switch to the ``docs`` directory::

      cd docs

#. Build the documentation::

      make html


.. _ReadTheDocs: https://class-registry.readthedocs.io/
.. _detox: https://pypi.python.org/pypi/detox
.. _tox: https://tox.readthedocs.io/

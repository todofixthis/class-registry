.. image:: https://github.com/todofixthis/class-registry/actions/workflows/build.yml/badge.svg
   :target: https://github.com/todofixthis/class-registry/actions/workflows/build.yml
.. image:: https://readthedocs.org/projects/class-registry/badge/?version=latest
   :target: http://class-registry.readthedocs.io/

ClassRegistry
=============
At the intersection of the Registry and Factory patterns lies the ``ClassRegistry``:

- Define global factories that generate new class instances based on configurable keys.
- Seamlessly create powerful service registries.
- Integrate with setuptools's ``entry_points`` system to make your registries infinitely
  extensible by 3rd-party libraries!
- And more!

Upgrading from ClassRegistry v4
-------------------------------
.. important::

   ClassRegistry v5 introduces some changes that can break code that was previously
   using ClassRegistry v4.  If you are upgrading from ClassRegistry v4 to ClassRegistry
   v5, please read `Upgrading to ClassRegistry v5 <./docs/upgrading_to_v5.rst>`_.


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

.. tip::

   If a ``ClassRegistry`` always returns objects derived from a particular base class,
   you can provide a
   `type parameter <https://typing.readthedocs.io/en/latest/source/generics.html#generics>`_
   to help with type checking, autocomplete, etc.:

   .. code-block:: python

      # Add type parameter ``[Pokemon]``:
      pokedex = ClassRegistry[Pokemon]()

      # Your IDE will automatically infer that ``fighter1`` is a ``Pokemon``.
      fighter1 = pokedex['fire']


Advanced Usage
~~~~~~~~~~~~~~
There's a whole lot more you can do with ClassRegistry, including:

- Provide args and kwargs to new class instances.
- Automatically register non-abstract classes.
- Integrate with setuptools's ``entry_points`` system so that 3rd-party libraries can
  add their own classes to your registries.
- Wrap your registry in an instance cache to create a service registry.
- And more!

For more advanced usage, check out the documentation on
`ReadTheDocs <https://class-registry.readthedocs.io/>`_!


Requirements
------------
ClassRegistry is known to be compatible with the following Python versions:

- 3.12
- 3.11
- 3.10

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

Maintainers
===========
To install the distribution for local development, some additional setup is required:

#. `Install poetry <https://python-poetry.org/docs/#installation>`_ (only needs to be
   done once).

#. Run the following command to install additional dependencies::

      poetry install --with=dev

#. Activate pre-commit hook::

      poetry run autohooks activate --mode=poetry

Running Unit Tests and Type Checker
-----------------------------------
Run the tests for all supported versions of Python using
`tox <https://tox.readthedocs.io/>`_::

   poetry run tox -p

.. note::

   The first time this runs, it will take awhile, as mypy needs to build up its cache.
   Subsequent runs should be much faster.

If you just want to run unit tests in the current virtualenv (using
`pytest <https://docs.pytest.org>`_)::

   poetry run pytest

If you just want to run type checking in the current virtualenv (using
`mypy <https://mypy.readthedocs.io>`_)::

   poetry run mypy class_registry test

Documentation
-------------
To build the documentation locally:

#. Switch to the ``docs`` directory::

    cd docs

#. Build the documentation::

    make html

Releases
--------
Steps to build releases are based on
`Packaging Python Projects Tutorial <https://packaging.python.org/en/latest/tutorials/packaging-projects/>`_.

.. important::

   Make sure to build releases off of the ``main`` branch, and check that all changes
   from ``develop`` have been merged before creating the release!

1. Build the Project
~~~~~~~~~~~~~~~~~~~~
#. Delete artefacts from previous builds, if applicable::

    rm dist/*

#. Run the build::

    poetry build

#. The build artefacts will be located in the ``dist`` directory at the top
   level of the project.

2. Upload to PyPI
~~~~~~~~~~~~~~~~~
#. `Create a PyPI API token <https://pypi.org/manage/account/token/>`_ (you only have to
   do this once).
#. Increment the version number in ``pyproject.toml``.
#. Upload build artefacts to PyPI::

    poetry publish

3. Create GitHub Release
~~~~~~~~~~~~~~~~~~~~~~~~
#. Create a tag and push to GitHub::

      git tag <version>
      git push <version>

   ``<version>`` must match the updated version number in ``pyproject.toml``.

#. Go to the `Releases page for the repo`_.
#. Click ``Draft a new release``.
#. Select the tag that you created in step 1.
#. Specify the title of the release (e.g., ``ClassRegistry v1.2.3``).
#. Write a description for the release.  Make sure to include:
   - Credit for code contributed by community members.
   - Significant functionality that was added/changed/removed.
   - Any backwards-incompatible changes and/or migration instructions.
   - SHA256 hashes of the build artefacts.
#. GPG-sign the description for the release (ASCII-armoured).
#. Attach the build artefacts to the release.
#. Click ``Publish release``.

.. _Releases page for the repo: https://github.com/todofixthis/class-registry/releases

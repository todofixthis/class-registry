.. image:: https://travis-ci.org/todofixthis/class-registry.svg?branch=master
   :target: https://travis-ci.org/todofixthis/class-registry
.. image:: https://readthedocs.org/projects/class-registry/badge/?version=latest
   :target: http://class-registry.readthedocs.io/

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


.. important::
   Make sure to install `phx-class-registry`, **not** `class-registry`.  I
   created the latter at a previous job years ago, and after I left they never
   touched that project again — so in the end I had to fork it 🤷

Running Unit Tests
------------------
Install the package with the ``test-runner`` extra to set up the necessary
dependencies, and then you can run the tests with the ``tox`` command::

   pip install -e .[test-runner]
   tox -p all

Documentation
-------------
Documentation is available on `ReadTheDocs`_.

If you are installing from source (see above), you can also build the
documentation locally:

#. Install extra dependencies (you only have to do this once)::

    pip install -e '.[docs-builder]'

#. Switch to the ``docs`` directory::

    cd docs

#. Build the documentation::

    make html

Releases
--------
Steps to build releases are based on `Packaging Python Projects Tutorial`_

.. important::

   Make sure to build releases off of the ``main`` branch, and check that all
   changes from ``develop`` have been merged before creating the release!

1. Build the Project
~~~~~~~~~~~~~~~~~~~~
#. Install extra dependencies (you only have to do this once)::

    pip install -e '.[build-system]'

#. Run the build::

    python -m build

#. The build artefacts will be located in the ``dist`` directory at the top
   level of the project.

2. Upload to PyPI
~~~~~~~~~~~~~~~~~
#. `Create a PyPI API token`_ (you only have to do this once).
#. Increment the version number in ``pyproject.toml``.
#. Check that the build artefacts are valid, and fix any errors that it finds::

    python -m twine check dist/*

#. Upload build artefacts to PyPI::

    python -m twine upload dist/*


3. Create GitHub Release
~~~~~~~~~~~~~~~~~~~~~~~~
#. Create a tag and push to GitHub::

    git tag <version>
    git push

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

.. _Create a PyPI API token: https://pypi.org/manage/account/token/
.. _Packaging Python Projects Tutorial: https://packaging.python.org/en/latest/tutorials/packaging-projects/
.. _ReadTheDocs: https://class-registry.readthedocs.io/
.. _Releases page for the repo: https://github.com/todofixthis/class-registry/releases
.. _tox: https://tox.readthedocs.io/

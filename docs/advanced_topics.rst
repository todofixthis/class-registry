Advanced Topics
===============
This section covers more advanced or esoteric uses of ClassRegistry features.

Registering Classes Automatically
---------------------------------
Tired of having to add the ``register`` decorator to every class that you want
to add to a class registry?  Surely there's a better way!

ClassRegistry also provides an :py:func:`AutoRegister` metaclass that you can
apply to a base class.  Any non-abstract subclass that extends that base class
will be registered automatically.

Here's an example:

.. code-block:: python

   from abc import abstractmethod
   from class_registry import AutoRegister, ClassRegistry

   pokedex = ClassRegistry('element')

   # Note ``AutoRegister(pokedex)`` used as the metaclass here.
   class Pokemon(metaclass=AutoRegister(pokedex)):
      @abstractmethod
      def get_abilities(self):
        raise NotImplementedError()

   # Define some non-abstract subclasses.
   class Butterfree(Pokemon):
     element = 'bug'

     def get_abilities(self):
       return ['compound_eyes']

   class Spearow(Pokemon):
     element = 'flying'

     def get_abilities(self):
       return ['keen_eye']

   # Any non-abstract class that extends ``Pokemon`` will automatically
   # get registered in our Pokédex!
   assert list(pokedex.items()) == \
     [('bug', Butterfree), ('flying', Spearow)]

In the above example, note that ``Butterfree`` and ``Spearow`` were added to
``pokedex`` automatically.  However, the ``Pokemon`` base class was not added,
because it is abstract.

.. important::

   Python defines an abstract class as a class with at least one unimplemented
   abstract method.  You can't just add ``metaclass=ABCMeta``!

   .. code-block:: python

      from abc import ABCMeta

      # Declare an "abstract" class.
      class ElectricPokemon(Pokemon, metaclass=ABCMeta):
        element = 'electric'

        def get_abilities(self):
          return ['shock']

      assert list(pokedex.items()) == \
        [('bug', Butterfree), \
         ('flying', Spearow), \
         ('electric', ElectricPokemon)]

   Note in the above example that ``ElectricPokemon`` was added to ``pokedex``,
   even though its metaclass is :py:class:`ABCMeta`.

   Because ``ElectricPokemon`` doesn't have any unimplemented abstract methods,
   Python does **not** consider it to be abstract.

   We can verify this by using :py:func:`inspect.isabstract`:

   .. code-block:: python

      from inspect import isabstract
      assert not isabstract(ElectricPokemon)


Patching
--------
From time to time, you might need to register classes temporarily.  For example,
you might need to patch a global class registry in a unit test, ensuring that
the extra classes are removed when the test finishes.

ClassRegistry provides a :py:class:`RegistryPatcher` that you can use for just
such a purpose:

.. code-block:: python

   from class_registry import ClassRegistry, RegistryKeyError, \
     RegistryPatcher

   pokedex = ClassRegistry('element')

   # Create a couple of new classes, but don't register them yet!
   class Oddish(object):
     element = 'grass'

   class Meowth(object):
     element = 'normal'

   # As expected, neither of these classes are registered.
   try:
     pokedex['grass']
   except RegistryKeyError:
     pass

   # Use a patcher to temporarily register these classes.
   with RegistryPatcher(pokedex, Oddish, Meowth):
     abbot = pokedex['grass']
     assert isinstance(abbot, Oddish)

     costello = pokedex['normal']
     assert isinstance(costello, Meowth)

   # Outside the context, the classes are no longer registered!
   try:
     pokedex['grass']
   except RegistryKeyError:
     pass

If desired, you can also change the registry key, or even replace a class that
is already registered.

.. code-block:: python

   @pokedex.register
   class Squirtle(object):
     element = 'water'

   # Get your diving suit Meowth; we're going to Atlantis!
   with RegistryPatcher(pokedex, water=Meowth):
     nemo = pokedex['water']
     assert isinstance(nemo, Meowth)

   # After the context exits, the previously-registered class is
   # restored.
   ponsonby = pokedex['water']
   assert isinstance(ponsonby, Squirtle)

.. important::

   Only mutable registries can be patched (any class that extends
   :py:class:`MutableRegistry`).

   In particular, this means that :py:class:`EntryPointClassRegistry` can
   **not** be patched using :py:class:`RegistryPatcher`.

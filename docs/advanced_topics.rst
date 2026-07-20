Advanced Topics
===============
This section covers more advanced or esoteric uses of ClassRegistry features.

Registering Classes Automatically
---------------------------------
Tired of having to add the ``register`` decorator to every class that you want to add to
a class registry?  Surely there's a better way!

The answer is :py:func:`class_registry.base.AutoRegister`!

Call ``AutoRegister()`` and pass in a registry, and it returns a base class. Any
non-abstract class that extends from that base class automatically gets added to the
registry.

Here's an example:

.. code-block:: python

   from abc import ABC, abstractmethod
   from class_registry import ClassRegistry
   from class_registry.base import AutoRegister

   pokedex = ClassRegistry('element')

   # Note ``AutoRegister(pokedex)`` used as a base class here, as well as ``ABC``.
   class Pokemon(AutoRegister(pokedex), ABC):
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

   # Any non-abstract class that extends ``Pokemon`` will automatically get registered
   # in our Pokédex!
   assert list(pokedex.keys()) == ['bug', 'flying']
   assert list(pokedex.classes()) == [Butterfree, Spearow]

In the above example, note that ``Butterfree`` and ``Spearow`` were added to
``pokedex`` automatically. However, the ``Pokemon`` base class was not added,
because it is abstract.

.. important::

   Python defines an abstract class as a class with at least one unimplemented abstract
   method. You can't just add ``ABC``!

   .. code-block:: python

      from abc import ABC

      # Declare an "abstract" class.
      class ElectricPokemon(Pokemon, ABC):
          element = 'electric'

          def get_abilities(self):
              return ['shock']

      assert list(pokedex.keys()) == ['bug', 'flying', 'electric']
      assert list(pokedex.classes()) == [Butterfree, Spearow, ElectricPokemon]

   Note in the above example that ``ElectricPokemon`` was added to ``pokedex``,
   even though it extends :py:class:`abc.ABC`.

   Because ``ElectricPokemon`` doesn't have any unimplemented abstract methods,
   Python does not consider it to be abstract.

   We can verify this by using :py:func:`inspect.isabstract`:

   .. code-block:: python

      from inspect import isabstract
      assert not isabstract(ElectricPokemon)

.. note::

   In previous versions of ClassRegistry, ``AutoRegister`` returned a metaclass instead
   of a base class. The metaclass version of the function still exists at
   :py:func:`class_registry.auto_register.AutoRegister`, but
   `it is deprecated and will be removed in a future version of ClassRegistry <https://github.com/todofixthis/class-registry/issues/14>`_.

   If your code is still using the old ``AutoRegister`` function, you can change it like
   this:

   .. code-block:: python

      # Deprecated:
      from class_registry.auto_register import AutoRegister

      class MyBaseClass(metaclass=AutoRegister(my_registry)):
          ...

      # Update to this:
      from abc import ABC
      from class_registry.base import AutoRegister

      class MyBaseClass(AutoRegister(my_registry), ABC):
          ...

Patching
--------
From time to time, you might need to register classes temporarily. For example, you
might need to patch a global class registry in a unit test, ensuring that the extra
classes are removed when the test finishes.

ClassRegistry provides a :py:class:`RegistryPatcher` that you can use for just such a
purpose:

.. code-block:: python

   from class_registry import ClassRegistry, RegistryKeyError
   from class_registry.patcher import RegistryPatcher

   pokedex = ClassRegistry('element')

   # Create a couple of new classes, but don't register them yet!
   class Oddish:
       element = 'grass'

   class Meowth:
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

If desired, you can also change existing registry keys, or even replace a class that is
already registered.

.. code-block:: python

   @pokedex.register
   class Squirtle:
       element = 'water'

   # Get your diving suit Meowth; we're going to Atlantis!
   with RegistryPatcher(pokedex, water=Meowth):
       nemo = pokedex['water']
       assert isinstance(nemo, Meowth)

   # After the context exits, the previously-registered class is restored.
   ponsonby = pokedex['water']
   assert isinstance(ponsonby, Squirtle)

.. important::

   Only mutable registries can be patched (any class that extends
   :py:class:`BaseMutableRegistry`).

   In particular, this means that :py:class:`EntryPointClassRegistry` can not be patched
   using :py:class:`RegistryPatcher`.


.. _overriding-lookup-keys:

Overriding Lookup Keys
----------------------
In some cases, you may want to customise the way a ``ClassRegistry`` looks up which
class to use internally. For example, you may want to introduce aliases, translations,
or even different types of keys.

To customise this, create a subclass of ``ClassRegistry`` and override its
``gen_lookup_key`` method.

For example, to support aliases or translations:

.. code-block:: python

   from class_registry import ClassRegistry

   class Pokemon:
       element: str

   class AliasRegistry(ClassRegistry[Pokemon]):
       @staticmethod
       def gen_lookup_key(key: typing.Hashable) -> typing.Hashable:
           """
           In a previous version of the codebase, some pokémon had the 'bird'
           type, but this was later dropped in favour of 'flying'.
           """
           if key == 'bird':
               return 'flying'

           return key

   pokedex = AliasRegistry('element')

   @pokedex.register
   class MissingNo(Pokemon):
       element = 'flying'

   @pokedex.register
   class Meowth(Pokemon):
       element = 'normal'

   # MissingNo can be accessed by either key.
   assert isinstance(pokedex['bird'], MissingNo)
   assert isinstance(pokedex['flying'], MissingNo)

   # Other pokémon work as you'd expect.
   assert isinstance(pokedex['normal'], Meowth)

You can also change the lookup key to a different type (so long as it implements
:py:class:`~typing.Hashable`):

.. code-block:: python

    class PokemonWithID(Pokemon):
        pokedex_id: int

    class MigrationRegistry(ClassRegistry[PokemonWithID, str | int]):
        """
        Historically pokémon were referenced by numeric ID. We are in the
        process of refactoring the code to reference the element instead, but
        until the migration is complete we still have to support looking up by
        ID.
        """
        element_from_id: dict[int, str] = {}

        def _register(self, key: typing.Hashable, class_: typing.Type[PokemonWithID]) -> None:
            super()._register(key, class_)
            self.element_from_id[class_.pokedex_id] = typing.cast(str, key)

        def gen_lookup_key(self, key: int | str) -> str:
            """
            If the caller is providing a pokedex ID (int), look up the
            corresponding element (str) for the lookup.
            """
            if isinstance(key, int):
                return self.element_from_id[key]
            return key

    pokedex = MigrationRegistry('element')

    @pokedex.register
    class Charizard(PokemonWithID):
        element = 'fire'
        pokedex_id = 6

    # Callers can provide either the element or the legacy ID to the registry.
    assert isinstance(pokedex['fire'], Charizard)
    assert isinstance(pokedex[6], Charizard)
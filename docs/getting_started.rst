Getting Started
===============
As you saw in the :doc:`introduction </index>`, you can create a new registry using the
:py:class:`class_registry.ClassRegistry` class.

:py:class:`ClassRegistry` defines a ``register`` method that you can use as a decorator
to add classes to the registry:

.. code-block:: python

   from class_registry import ClassRegistry

   pokedex = ClassRegistry()

   @pokedex.register('fire')
   class Charizard:
       pass

Once you've registered a class, you can then create a new instance using the
corresponding registry key:

.. code-block:: python

   sparky = pokedex['fire']
   assert isinstance(sparky, Charizard)

Note in the above example that ``sparky`` is an `instance` of ``Charizard``.

If you try to access a registry key that has no classes registered, it will raise a
:py:class:`class_registry.RegistryKeyError`:

.. code-block:: python

   from class_registry import RegistryKeyError

   try:
       tex = pokedex['spicy']
   except RegistryKeyError:
       pass

Typed Registries
----------------
If a :py:class:`ClassRegistry` always returns objects derived from a particular
base class, you can provide a
`type parameter <https://typing.readthedocs.io/en/latest/source/generics.html#generics>`_
to help with type checking, autocomplete, etc.:

.. code-block:: python

   # Add type parameter ``[Pokemon]``:
   pokedex = ClassRegistry[Pokemon]()

   # Your IDE will automatically infer that ``fighter1`` is a ``Pokemon``.
   fighter1 = pokedex['fire']

Auto-Detecting Registry Keys
----------------------------
By default, you have to provide the registry key whenever you register a new class.
But, there's an easier way to do it!

When you initialise your :py:class:`ClassRegistry`, provide an ``attr_name`` parameter.
When you register new classes, your registry will automatically extract the registry key
using that attribute:

.. code-block:: python

   pokedex = ClassRegistry('element')

   @pokedex.register
   class Squirtle:
       element = 'water'

   beauregard = pokedex['water']
   assert isinstance(beauregard, Squirtle)

Note in the above example that the registry automatically extracted the registry key for
the ``Squirtle`` class using its ``element`` attribute.

Collisions
----------
What happens if two classes have the same registry key?

.. code-block:: python

   pokedex = ClassRegistry('element')

   @pokedex.register
   class Bulbasaur:
       element = 'grass'

   @pokedex.register
   class Ivysaur:
       element = 'grass'

   janet = pokedex['grass']
   assert isinstance(janet, Ivysaur)

As you can see, if two (or more) classes have the same registry key, whichever one is
registered last will override any of the other(s).

.. note::

    It is not always easy to predict the order in which classes will be registered,
    especially when they are spread across different modules, so you probably don't
    want to rely on this behaviour!

If you want to prevent collisions, you can pass ``unique=True`` to the
:py:class:`ClassRegistry` initialiser to raise an exception whenever a collision occurs:

.. code-block:: python

   from class_registry import RegistryKeyError

   pokedex = ClassRegistry('element', unique=True)

   @pokedex.register
   class Bulbasaur:
       element = 'grass'

   try:
       @pokedex.register
       class Ivysaur:
           element = 'grass'
   except RegistryKeyError:
       pass

   janet = pokedex['grass']
   assert isinstance(janet, Bulbasaur)

Because we passed ``unique=True`` to the :py:class:`ClassRegistry` initialiser,
attempting to register ``Ivysaur`` with the same registry key as ``Bulbasaur`` raised a
:py:class:`RegistryKeyError`, so it didn't override ``Bulbasaur``.

Init Params
-----------
Every time you access a registry key in a :py:class:`ClassRegistry`, it creates a new
instance:

.. code-block:: python

   marlene = pokedex['grass']
   charlene = pokedex['grass']

   assert marlene is not charlene

Since you're creating a new instance every time, you also have the option of providing
args and kwargs to the class initialiser using the registry's :py:meth:`get` method:

.. code-block:: python

   pokedex = ClassRegistry('element')

   @pokedex.register
   class Caterpie:
       element = 'bug'

       def __init__(self, level=1):
           super(Caterpie, self).__init__()
           self.level = level

   timmy = pokedex.get('bug')
   assert timmy.level == 1

   tommy = pokedex.get('bug', 16)
   assert tommy.level == 16

   tammy = pokedex.get('bug', level=42)
   assert tammy.level == 42

Any arguments that you provide to :py:meth:`get` will be passed directly to the
corresponding class' initialiser.

.. hint::

   You can create a service registry that always returns the same instance per registry
   key by wrapping it in a :py:class:`ClassRegistryInstanceCache`.  See
   :doc:`service_registries` for more information.

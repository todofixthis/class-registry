Creating Service Registries
===========================
Despite its name, :py:class:`ClassRegistry` also has aspects in common with the Factory
pattern.  Most notably, accessing a registry key automatically creates a new instance of
the corresponding class.

But, what if you want a :py:class:`ClassRegistry` to behave more strictly like a service
registry — always returning the the `same` instance each time the same key is accessed?

This is where :py:class:`ClassRegistryInstanceCache` comes into play.  It wraps a
:py:class:`ClassRegistry` and provides a caching mechanism, so that each time your code
accesses a particular key, it always returns the same instance for that key.

Let's see what this looks like in action.  First, we'll create a
:py:class:`ClassRegistry`:

.. code-block:: python

   from class_registry import ClassRegistry

   pokedex = ClassRegistry('element')

   @pokedex.register
   class Pikachu:
       element = 'electric'

   @pokedex.register
   class Alakazam:
       element = 'psychic'

   # Accessing the ClassRegistry yields a different instance every time.
   pika_1 = pokedex['electric']
   pika_2 = pokedex['electric']
   assert pika_1 is not pika_2

Next we'll wrap the registry in a :py:class:`ClassRegistryInstanceCache`:

.. code-block:: python

   from class_registry.cache import ClassRegistryInstanceCache

   fighters = ClassRegistryInstanceCache(pokedex)

   # ClassRegistryInstanceCache works just like ClassRegistry, except it returns the
   # same instance per key.
   darth_vader = fighters['psychic']
   anakin_skywalker = fighters['psychic']
   assert darth_vader is anakin_skywalker

Note in the above example that the :py:class:`ClassRegistryInstanceCache` always returns
the same instance every time its ``psychic`` key is accessed.

Typed Service Registries
------------------------
:py:class:`ClassRegistryInstanceCache` inherits the
`type parameter <https://typing.readthedocs.io/en/latest/source/generics.html#generics>`_
from the :py:class:`ClassRegistry` that it wraps in order to help with type checking,
autocompletion, etc.:

.. code-block:: python

   # Add type parameter ``[Pokemon]``:
   registry = ClassRegistry[Pokemon]()

   # The ``ClassRegistryInstanceCache`` inherits the type parameters from the
   # ``ClassRegistry`` that it wraps.
   pokedex = ClassRegistryInstanceCache(registry)

   # Your IDE will automatically infer that ``fire_fighter`` is a ``Pokemon``.
   fire_fighter = pokedex['fire']

Alternatively, you can apply the type parameter to the
:py:class:`ClassRegistryInstanceCache` directly:

.. code-block:: python

   pokedex = ClassRegistryInstanceCache[Pokemon](registry)

========================
Factories vs. Registries
========================
Despite its name, :py:class:`ClassRegistry` also has aspects in common with the
Factory pattern.

Most notably, accessing a registry key automatically creates a new instance of
the corresponding class.

But, what if you want a :py:class:`ClassRegistry` to behave more strictly like a
registry — always returning the the `same` instance each time the same key is
accessed?

This is where :py:class:`ClassRegistryInstanceCache` comes into play.  It wraps
a :py:class:`ClassRegistry` and provides a caching mechanism, so that each time
you access a particular key, it always returns the same instance for that key.

Let's see what this looks like in action:

.. code-block:: python

   from class_registry import ClassRegistry, ClassRegistryInstanceCache

   pokedex = ClassRegistry('element')

   @pokedex.register
   class Pikachu(object):
     element = 'electric'

   @pokedex.register
   class Alakazam(object):
     element = 'psychic'

   fighters = ClassRegistryInstanceCache(pokedex)

   # Accessing the ClassRegistry yields a different instance every
   # time.
   pika_1 = pokedex['electric']
   assert isinstance(pika_1, Pikachu)
   pika_2 = pokedex['electric']
   assert isinstance(pika_2, Pikachu)
   assert pika_1 is not pika_2

   # ClassRegistryInstanceCache works just like ClassRegistry, except
   # it returns the same instance per key.
   pika_3 = fighters['electric']
   assert isinstance(pika_3, Pikachu)
   pika_4 = fighters['electric']
   assert isinstance(pika_4, Pikachu)
   assert pika_3 is pika_4

   darth_vader = fighters['psychic']
   assert isinstance(darth_vader, Alakazam)
   anakin_skywalker = fighters['psychic']
   assert isinstance(anakin_skywalker, Alakazam)
   assert darth_vader is anakin_skywalker


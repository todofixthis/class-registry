Iterating Over Registries
=========================
Sometimes, you want to iterate over all of the classes registered in a
:py:class:`ClassRegistry`.  There are two methods included to help you do this:

- :py:meth:`keys` iterates over the registry keys.
- :py:meth:`classes` iterates over the registered classes.

Here's an example:

.. code-block:: python

   from class_registry import ClassRegistry

   pokedex = ClassRegistry('element')

   @pokedex.register
   class Geodude:
       element = 'rock'

   @pokedex.register
   class Machop:
       element = 'fighting'

   @pokedex.register
   class Bellsprout:
       element = 'grass'

   assert list(pokedex.keys()) == ['rock', 'fighting', 'grass']
   assert list(pokedex.classes()) == [Geodude, Machop, Bellsprout]

.. tip::

   Tired of having to add the :py:meth:`register` decorator to every class?

   You can use :py:func:`AutoRegister` to generate a base class that automatically
   registers all non-abstract subclasses of a particular base class.  See
   :doc:`advanced_topics` for more information.

Specifying the Key Type
-----------------------
By default, registry keys are typed as :py:class:`str`.  This means that
``registry.keys()`` and ``for key in registry`` both yield :py:class:`str`
values — no explicit ``str()`` coercion needed.

:py:class:`ClassRegistry` accepts an optional second type argument for the key
type.  The first argument is always the value type:

.. code-block:: python

   ClassRegistry[ValueType, KeyType]

For example, to use integer keys:

.. code-block:: python

   from abc import ABC
   from class_registry import ClassRegistry

   class Pokemon(ABC):
       pokedex_id: int
       # ...

   # Register ``Pokemon`` by their numeric IDs instead of elements.
   # Note that we pass ``int`` as the *second* type argument.
   pokedex: ClassRegistry[Pokemon, int] = ClassRegistry('pokedex_id')

   @pokedex.register
   class Geodude(Pokemon):
       pokedex_id = 74

   assert list(pokedex.keys()) == [74]

Upgrading from ClassRegistry v5 or earlier?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In ClassRegistry v6 the default key type was changed from :py:class:`~typing.Hashable`
to :py:class:`str`. This change may cause type checker failures in your project — see
:doc:`upgrading_to_v6` for migration instructions.

Changing the Sort Order
-----------------------
As you probably noticed, these functions iterate over classes in the order that they are
registered.

If you'd like to customise this ordering, use :py:class:`SortedClassRegistry`:

.. code-block:: python

   from class_registry.registry import SortedClassRegistry

   pokedex = SortedClassRegistry(attr_name='element', sort_key='weight')

   @pokedex.register
   class Geodude:
       element = 'rock'
       weight = 1000

   @pokedex.register
   class Machop:
       element = 'fighting'
       weight = 75

   @pokedex.register
   class Bellsprout:
       element = 'grass'
       weight = 15

   assert list(pokedex.keys()) == ['grass', 'fighting', 'rock']
   assert list(pokedex.classes()) == [Bellsprout, Machop, Geodude]

In the above example, the code iterates over registered classes in ascending order by
their ``weight`` attributes.

You can provide a sorting function instead if you need more control over how the items
are sorted:

.. code-block:: python

   from functools import cmp_to_key

   def sorter(a, b):
       """
       Sorts items by weight, using registry key as a tiebreaker.

       :param a: Tuple of (key, class)
       :param b: Tuple of (key, class)
       """
       # Sort descending by weight first.
       weight_cmp = (
             (a[1].weight < b[1].weight)
           - (a[1].weight > b[1].weight)
       )

       if weight_cmp != 0:
           return weight_cmp

       # Use registry key as a fallback.
       return ((a[0] > b[0]) - (a[0] < b[0]))

   pokedex =\
       SortedClassRegistry(
           attr_name = 'element',

           # Note that we pass ``sorter`` through ``cmp_to_key`` first!
           sort_key = cmp_to_key(sorter),
       )

   @pokedex.register
   class Horsea:
       element = 'water'
       weight = 5

   @pokedex.register
   class Koffing:
       element = 'poison'
       weight = 20

   @pokedex.register
   class Voltorb:
       element = 'electric'
       weight = 5

   assert list(pokedex.keys()) == ['poison', 'electric', 'water']
   assert list(pokedex.classes()) == [Koffing, Voltorb, Horsea]

This time, the :py:class:`SortedClassRegistry` used our custom sorter function, so that
the classes were sorted descending by weight, with the registry key used as a
tiebreaker.

.. important::

   Note that we had to pass the sorter function through :py:func:`functools.cmp_to_key`
   before providing it to the :py:class:`SortedClassRegistry` initialiser.

   This is necessary because of how sorting works in Python.  See
   `Sorting HOW TO <https://docs.python.org/3/howto/sorting.html#key-functions>`_ for
   more information.

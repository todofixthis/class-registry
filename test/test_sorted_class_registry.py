from functools import cmp_to_key

from class_registry.registry import SortedClassRegistry
from test import Bulbasaur, Charmander, Pokemon, Squirtle


def test_sort_key():
    """
    When iterating over a SortedClassRegistry, classes are returned in
    sorted order rather than inclusion order.
    """
    registry = SortedClassRegistry[Pokemon](
        attr_name="element",
        sort_key="weight",
    )

    @registry.register
    class Geodude(Pokemon):
        element = "rock"
        weight = 100

    @registry.register
    class Machop(Pokemon):
        element = "fighting"
        weight = 75

    @registry.register
    class Bellsprout(Pokemon):
        element = "grass"
        weight = 15

    # The registry iterates over registered classes in ascending order by
    # ``weight``.
    assert list(registry.values()) == [Bellsprout, Machop, Geodude]


def test_sort_key_reverse():
    """
    Reversing the order of a sort key.
    """
    registry = SortedClassRegistry[Pokemon](
        attr_name="element",
        sort_key="weight",
        reverse=True,
    )

    @registry.register
    class Geodude(Pokemon):
        element = "rock"
        weight = 100

    @registry.register
    class Machop(Pokemon):
        element = "fighting"
        weight = 75

    @registry.register
    class Bellsprout(Pokemon):
        element = "grass"
        weight = 15

    # The registry iterates over registered classes in descending order by ``weight``.
    assert list(registry.values()) == [Geodude, Machop, Bellsprout]


def test_cmp_to_key():
    """
    If you want to use a ``cmp`` function to define the ordering,
    you must use the :py:func:`cmp_to_key` function.
    """

    def compare_pokemon(a, b):
        """
        Sort in descending order by popularity.

        :param a: Tuple of (key, class, lookup_key)
        :param b: Tuple of (key, class, lookup_key)
        """
        return (a[1].popularity < b[1].popularity) - (a[1].popularity > b[1].popularity)

    registry = SortedClassRegistry[Pokemon](
        attr_name="element",
        sort_key=cmp_to_key(compare_pokemon),
    )

    @registry.register
    class Onix(Pokemon):
        element = "rock"
        popularity = 50

    @registry.register
    class Cubone(Pokemon):
        element = "water"
        popularity = 100

    @registry.register
    class Exeggcute(Pokemon):
        element = "grass"
        popularity = 10

    # The registry iterates over registered classes in descending order by
    # ``popularity``.
    assert list(registry.values()) == [Cubone, Onix, Exeggcute]


def test_gen_lookup_key_overridden():
    """
    When a ``SortedClassRegistry`` overrides the ``gen_lookup_key`` method,
    it can sort by lookup keys if desired.
    """

    def compare_by_lookup_key(a, b):
        """
        :param a: Tuple of (key, class, lookup_key)
        :param b: Tuple of (key, class, lookup_key)
        """
        return (a[2] > b[2]) - (a[2] < b[2])

    class TestRegistry(SortedClassRegistry[Pokemon]):
        @staticmethod
        def gen_lookup_key(key: str) -> str:
            """
            Simple override of `gen_lookup_key`, to ensure the sorting
            behaves as expected when the lookup key is different.
            """
            return "".join(reversed(key))

    registry = TestRegistry(sort_key=cmp_to_key(compare_by_lookup_key))

    registry.register("fire")(Charmander)
    registry.register("grass")(Bulbasaur)
    registry.register("water")(Squirtle)

    assert list(registry.items()) == [
        ("fire", Charmander),
        ("water", Squirtle),
        ("grass", Bulbasaur),
    ]

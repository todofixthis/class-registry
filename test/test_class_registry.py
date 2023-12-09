import pytest

from class_registry import ClassRegistry, RegistryKeyError
from test import Bulbasaur, Charmander, Charmeleon, Pokemon, Squirtle, Wartortle


def test_register_manual_keys():
    """
    Registers a few classes with manually-assigned identifiers and verifies
    that the factory returns them correctly.
    """
    registry = ClassRegistry[Pokemon]()

    @registry.register("fire")
    class Charizard(Pokemon):
        pass

    @registry.register("water")
    class Blastoise(Pokemon):
        pass

    # By default, you have to specify a registry key when registering new
    # classes.  We'll see how to assign registry keys automatically in the
    # next test.
    with pytest.raises(ValueError):
        # noinspection PyUnusedLocal
        @registry.register
        class Venusaur(Pokemon):
            pass

    assert registry.get_class("fire") is Charizard
    assert isinstance(registry["fire"], Charizard)

    assert registry.get_class("water") is Blastoise
    assert isinstance(registry["water"], Blastoise)


def test_register_detect_keys():
    """
    If an attribute name is passed to ClassRegistry's constructor, it will
    automatically check for this attribute when registering classes.
    """
    registry = ClassRegistry[Pokemon](attr_name="element")

    @registry.register
    class Charizard(Pokemon):
        element = "fire"

    @registry.register
    class Blastoise(Pokemon):
        element = "water"

    # You can still override the registry key if you want.
    @registry.register("poison")
    class Venusaur(Pokemon):
        element = "grass"

    assert isinstance(registry["fire"], Charizard)
    assert isinstance(registry["water"], Blastoise)
    assert isinstance(registry["poison"], Venusaur)

    # We overrode the registry key for this class.
    with pytest.raises(RegistryKeyError):
        # noinspection PyStatementEffect
        registry["grass"]


def test_register_error_empty_key():
    """
    Attempting to register a class with an empty key.
    """
    registry = ClassRegistry[Pokemon]("element")

    with pytest.raises(ValueError):
        # noinspection PyUnusedLocal
        @registry.register("")
        class Rapidash(Pokemon):
            element = "fire"

    with pytest.raises(ValueError):
        # noinspection PyUnusedLocal
        @registry.register
        class Mew(Pokemon):
            element = None

    with pytest.raises(ValueError):
        # noinspection PyUnusedLocal
        @registry.register
        class Mewtwo(Pokemon):
            element = ""


def test_unique_keys():
    """
    Specifying ``unique=True`` when creating the registry requires all keys
    to be unique.
    """
    registry = ClassRegistry[Pokemon](attr_name="element", unique=True)

    # We can register any class like normal...
    registry.register(Charmander)

    # ... but if we try to register a second class with the same key, we
    # get an error.
    with pytest.raises(RegistryKeyError):
        registry.register(Charmeleon)


def test_unregister():
    """
    Removing a class from the registry.

    .. note::
       This is not used that often outside unit tests (e.g., to remove
       artefacts when a test has to add a class to a global registry).
    """
    registry = ClassRegistry[Pokemon](attr_name="element")
    registry.register(Charmander)
    registry.register(Squirtle)

    assert registry.unregister("fire") is Charmander

    with pytest.raises(RegistryKeyError):
        registry.get("fire")

    # Note that you must unregister the KEY, not the CLASS.
    with pytest.raises(KeyError):
        registry.unregister(Squirtle)

    # If you try to unregister a key that isn't registered, you'll
    # get an error.
    with pytest.raises(KeyError):
        registry.unregister("fire")


def test_constructor_params():
    """
    Params can be passed to the registered class' constructor.
    """
    registry = ClassRegistry[Pokemon](attr_name="element")
    registry.register(Bulbasaur)

    # Goofus uses positional arguments, which are magical and make his code
    # more difficult to read.
    goofus = registry.get("grass", "goofus")

    # Gallant uses keyword arguments, producing self-documenting code and
    # being courteous to his fellow developers.
    # He still names his pokémon after himself, though. Narcissist.
    gallant = registry.get("grass", name="gallant")

    assert isinstance(goofus, Bulbasaur)
    assert goofus.name == "goofus"

    assert isinstance(gallant, Bulbasaur)
    assert gallant.name == "gallant"


def test_new_instance_every_time():
    """
    Every time a registered class is invoked, a new instance is returned.
    """
    registry = ClassRegistry[Pokemon](attr_name="element")
    registry.register(Wartortle)

    assert registry["water"] is not registry["water"]


def test_register_function():
    """
    Functions can be registered as well (so long as they walk and quack
    like a class).
    """
    registry = ClassRegistry[Pokemon]()

    @registry.register("fire")
    def pokemon_factory(name=None):
        return Charmeleon(name=name)

    poke = registry.get("fire", name="trogdor")

    assert isinstance(poke, Charmeleon)
    assert poke.name == "trogdor"


def test_contains_when_class_init_requires_arguments():
    """
    Special case when checking if a class is registered, and that class'
    initializer requires arguments.
    """
    registry = ClassRegistry[Pokemon](attr_name="element")

    @registry.register
    class Butterfree(Pokemon):
        element = "bug"

        def __init__(self, name):
            super(Butterfree, self).__init__(name)

    assert "bug" in registry

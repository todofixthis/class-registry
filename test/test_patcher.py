import pytest

from class_registry import ClassRegistry, RegistryKeyError
from class_registry.patcher import RegistryPatcher
from test import Bulbasaur, Charmander, Charmeleon, Ivysaur, Pokemon, Squirtle


@pytest.fixture(name="registry")
def fixture_registry() -> ClassRegistry[Pokemon]:
    return ClassRegistry(attr_name="element", unique=True)


def test_patch_detect_keys(registry: ClassRegistry[Pokemon]) -> None:
    """
    Patching a registry in a context, with registry keys detected
    automatically.
    """
    registry.register(Charmander)
    registry.register(Squirtle)

    with RegistryPatcher(registry, Charmeleon, Bulbasaur):
        assert isinstance(registry["fire"], Charmeleon)
        assert isinstance(registry["water"], Squirtle)

        # Nesting contexts?  You betcha!
        with RegistryPatcher(registry, Ivysaur):
            assert isinstance(registry["grass"], Ivysaur)

        assert isinstance(registry["grass"], Bulbasaur)

    # Save file corrupted.  Restoring previous save...
    assert isinstance(registry["fire"], Charmander)
    assert isinstance(registry["water"], Squirtle)

    with pytest.raises(RegistryKeyError):
        registry.get("grass")


def test_patch_manual_keys(registry: ClassRegistry[Pokemon]) -> None:
    """
    Patching a registry in a context, specifying registry keys manually.
    """
    registry.register("sparky")(Charmander)
    registry.register("chad")(Squirtle)

    with RegistryPatcher(registry, sparky=Charmeleon, rex=Bulbasaur):
        assert isinstance(registry["sparky"], Charmeleon)
        assert isinstance(registry["chad"], Squirtle)

        # Don't worry Chad; your day will come!
        with RegistryPatcher(registry, rex=Ivysaur):
            assert isinstance(registry["rex"], Ivysaur)

        assert isinstance(registry["rex"], Bulbasaur)

    # Save file corrupted.  Restoring previous save...
    assert isinstance(registry["sparky"], Charmander)
    assert isinstance(registry["chad"], Squirtle)

    with pytest.raises(RegistryKeyError):
        registry.get("jodie")

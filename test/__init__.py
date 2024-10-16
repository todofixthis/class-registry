import typing


class Pokemon:
    """
    A basic class with some attributes that we can use to test out class
    registries.
    """

    element: str

    def __init__(self, name: typing.Optional[str] = None):
        super().__init__()

        self.name: typing.Optional[str] = name


# Define some classes that we can register.
class Charmander(Pokemon):
    element = "fire"


class Charmeleon(Pokemon):
    element = "fire"


class Squirtle(Pokemon):
    element = "water"


class Wartortle(Pokemon):
    element = "water"


class Bulbasaur(Pokemon):
    element = "grass"


class Ivysaur(Pokemon):
    element = "grass"


class Mew(Pokemon):
    element = "psychic"


class PokemonFactory:
    """
    A factory that can produce new pokémon on demand.  Used to test how registries
    behave when a method/function is registered instead of a class.
    """

    @classmethod
    def create_psychic_pokemon(cls, name: typing.Optional[str] = None) -> Mew:
        return Mew(name)

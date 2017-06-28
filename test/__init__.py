# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals


class Pokemon(object):
    """
    A basic class with some attributes that we can use to test out
    class registries.
    """
    element = None

    def __init__(self, name=None):
        super(Pokemon, self).__init__()

        self.name = name


# Define some classes that we can register.
class Charmander(Pokemon):  element = 'fire'
class Charmeleon(Pokemon):  element = 'fire'
class Squirtle(Pokemon):    element = 'water'
class Wartortle(Pokemon):   element = 'water'
class Bulbasaur(Pokemon):   element = 'grass'
class Ivysaur(Pokemon):     element = 'grass'
class Mew(Pokemon):         element = 'psychic'


class PokemonFactory(object):
    """
    A factory that can produce new pokémon on demand.  Used to test how
    registries behave when a function is registered instead of a class.
    """
    @classmethod
    def create_psychic_pokemon(cls, name=None):
        return Mew(name)

import pygame

from .graphics import Graphics

from .player import Player
from .family import Mommy, Daddy, Mikey
from .grunt import Grunt
from .electrode import Electrode
from .hulk import Hulk


class Sprites:
    def __init__(self, engine):
        self.engine = engine

        self.sprites = Graphics().load()

    def Player(self):
        return Player(self.sprites, self.engine)

    def Mommy(self):
        return Mommy(self.sprites, self.engine)

    def Daddy(self):
        return Daddy(self.sprites, self.engine)

    def Mikey(self):
        return Mikey(self.sprites, self.engine)

    def Grunt(self):
        return Grunt(self.sprites, self.engine)

    def Electrode(self):
        return Electrode(self.sprites, self.engine)

    def Hulk(self):
        return Hulk(self.sprites, self.engine)

import pygame

from .graphics import Graphics

from .player import Player
from .grunt import Grunt
from .electrode import Electrode


class Sprites:
    def __init__(self, engine):
        self.engine = engine

        self.sprites = Graphics().load()

    def Player(self):
        return Player(self.sprites, self.engine)

    def Grunt(self):
        return Grunt(self.sprites, self.engine)

    def Electrode(self):
        return Electrode(self.sprites, self.engine)

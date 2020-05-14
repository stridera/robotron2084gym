import pygame

from .graphics import Graphics

from .player import Player
from .grunt import Grunt


class Sprites:
    def __init__(self, engine):
        self.engine = engine

        self.sprites = Graphics().load()

    def Player(self):
        return Player(self.sprites, self.engine)

    def Grunt(self):
        return Grunt(self.sprites, self.engine)

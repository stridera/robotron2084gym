import pygame
import random

from .base import Base


class Grunt(Base):
    """
    Grunt Enemy

    Behavior:
        Grunts are simple.  They plot the nearest path to the player and move.  
        They move fairly slow but speed up as the level progresses.

    """
    SCORE = 100

    def get_animations(self):
        engine = self.get_engine()
        return engine.get_sprites(['grunt1', 'grunt2', 'grunt1', 'grunt3'])

    def reset(self):
        self.moveSpeed = 7
        self.moveDelayMax = 25
        self.moveDelayMin = 5
        self.moveDelayRemaining = random.randrange(self.moveDelayMin, self.moveDelayMax)

        self.update_animation()
        self.random_location()

    def move(self):
        """ Grunts move toward the player """
        self.update_animation()
        self.move_toward_player(self.moveSpeed)

    def update(self):
        if self.moveDelayRemaining <= 0:
            self.move()
            self.moveDelayRemaining = random.randrange(self.moveDelayMin, self.moveDelayMax)
        else:
            self.moveDelayRemaining -= 1

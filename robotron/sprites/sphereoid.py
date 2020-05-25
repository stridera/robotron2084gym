import pygame
import random

from .sprite_base import Base


class Sphereoid(Base):

    def __init__(self, sprites, engine):
        self.type = 'sphereoid'
        self.animations = [
            sprites['sphereoid1'],
            sprites['sphereoid2'],
            sprites['sphereoid3'],
            sprites['sphereoid4'],
            sprites['sphereoid5'],
            sprites['sphereoid6'],
            sprites['sphereoid7'],
            sprites['sphereoid8'],
        ]
        self.deathSprite = sprites['1000']

        super().__init__(sprites, engine)

        self.score = 1000

        self.moveSpeed = 7
        self.moveDelay = 5
        self.moveDelayRemaining = self.moveDelay

        self.deathDelay = 15

        self.direction = random.choice(self.moveDirections)
        self.animationDirection = self.get_direction_string(self.direction)
        self.update_animation()

        self.random_location()

    def move(self):
        """ Sphereoids """
        self.update_animation()

    def update(self):
        """
        Sphereoids cycle through the first 4 frames for the first 8~30 cycles I guess.
        Then they move to phase 2 and start going through all 8 sprites.
        At 4~8 frames of the full cycle, they 'birth' an enforcer.

        """

        if self.alive:
            if self.moveDelayRemaining <= 0:
                self.move()
                self.moveDelayRemaining = self.moveDelay
            else:
                self.moveDelayRemaining -= 1

        else:
            self.deathDelay -= 1
            if self.deathDelay <= 0:
                self.kill()

    def die(self, sprite):
        if self.alive:
            self.image = self.deathSprite
            self.alive = False

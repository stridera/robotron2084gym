import pygame
import random

from .sprite_base import Base


class Hulk(Base):

    def __init__(self, sprites, engine):
        self.type = 'hulk'
        self.animations = {
            'left': [
                sprites['hulk1'],
                sprites['hulk2'],
                sprites['hulk1'],
                sprites['hulk3'],
            ],
            'right': [
                sprites['hulk7'],
                sprites['hulk8'],
                sprites['hulk7'],
                sprites['hulk9'],
            ],
            'down': [
                sprites['hulk4'],
                sprites['hulk5'],
                sprites['hulk4'],
                sprites['hulk6'],
            ],
            'up': [
                sprites['hulk4'],
                sprites['hulk5'],
                sprites['hulk4'],
                sprites['hulk6'],
            ]
        }

        super().__init__(sprites, engine)

        self.moveSpeed = 7
        self.turnPercentage = 20
        self.moveDelayMax = 25
        self.moveDelayMin = 5
        self.moveDelayRemaining = random.randrange(self.moveDelayMin, self.moveDelayMax)

        self.moveDirections = [self.UP, self.RIGHT, self.DOWN, self.LEFT]
        self.direction = random.choice(self.moveDirections)
        self.animationDirection = self.get_direction_string(self.direction)
        self.update_animation()

        self.random_location()

    def turn(self):
        idx = self.moveDirections.index(self.direction)
        if random.randrange(0, 1) == 0:  # Turn Right
            idx += 1
            if idx >= len(self.moveDirections):
                idx = 0
        else:  # Turn Left
            idx -= 1
            if idx < 0:
                idx = len(self.moveDirections) - 1

        self.direction = self.moveDirections[idx]

    def move(self):
        """ Hulks move in 4 directions, up down left right.  They randomly do 90deg turns left or right. """
        if random.randrange(1, 100) < self.turnPercentage:
            self.turn()

        while not self.valid_move(self.direction):
            self.turn()

        self.rect.center += self.get_vector(self.direction)
        self.animationDirection = self.get_direction_string(self.direction)
        self.update_animation()

    def update(self):
        if self.moveDelayRemaining <= 0:
            self.move()
            self.moveDelayRemaining = random.randrange(self.moveDelayMin, self.moveDelayMax)
        else:
            self.moveDelayRemaining -= 1

        for sprite in pygame.sprite.spritecollide(self, self.engine.get_family_group(), False):
            sprite.die()

    def die(self, sprite):
        """ Hulks never die, but they can be pushed back """
        self.rect.center += self.get_vector(sprite.direction, 3)
        self.rect.clamp_ip(self.playRect)

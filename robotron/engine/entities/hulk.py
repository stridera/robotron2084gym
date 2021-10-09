import pygame
import random

from .base import Base


class Hulk(Base):
    """
    Hulk Enemy Class

    Behavior:
        Hulks are immortal enemies that exist only to kill all in their path.
        They move slow and randomly turn left or right on their path to mayhem.
        While they can't die, they can be knocked back slightly by shooting them.
    """

    def get_animations(self):
        engine = self.get_engine()
        return {
            'left': engine.get_sprites(['hulk1', 'hulk2', 'hulk1', 'hulk3']),
            'right': engine.get_sprites(['hulk7', 'hulk8', 'hulk7', 'hulk9']),
            'down': engine.get_sprites(['hulk4', 'hulk5', 'hulk4', 'hulk6']),
            'up': engine.get_sprites(['hulk4', 'hulk5', 'hulk4', 'hulk6'])
        }

    def reset(self):
        self.update_animation()
        self.random_location()

        self.moveSpeed = 7
        self.turnPercentage = 20
        self.moveDelayMax = 25
        self.moveDelayMin = 5
        self.moveDelayRemaining = random.randrange(self.moveDelayMin, self.moveDelayMax)

        self.moveDirections = [self.UP, self.RIGHT, self.DOWN, self.LEFT]
        self.direction = random.choice(self.moveDirections)
        self.animationDirection = self.get_direction_string(self.direction)

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
            sprite.die(self)

    def die(self, killer):
        """ Hulks never die, but they can be pushed back """
        self.rect.center += self.get_vector(killer.direction, 3)
        self.rect.clamp_ip(self.playRect)

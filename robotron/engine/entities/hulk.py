""" Huld Monster Module"""
import random

import pygame

from .base import Base, Direction


class Hulk(Base):
    """
    Hulk Enemy Class

    Behavior:
        Hulks are immortal enemies that exist only to kill all in their path.
        They move slow and randomly turn left or right on their path to mayhem.
        While they can't die, they can be knocked back slightly by shooting them.
    """
    # pylint: disable=attribute-defined-outside-init

    def get_animations(self):
        """Returns the images used to animate the sprite."""

        return {
            'left': self.engine.get_sprites(['hulk1', 'hulk2', 'hulk1', 'hulk3']),
            'right': self.engine.get_sprites(['hulk7', 'hulk8', 'hulk7', 'hulk9']),
            'down': self.engine.get_sprites(['hulk4', 'hulk5', 'hulk4', 'hulk6']),
            'up': self.engine.get_sprites(['hulk4', 'hulk5', 'hulk4', 'hulk6'])
        }

    def reset(self):
        self.update_animation()
        self.random_location()

        self.speed = 7
        self.turn_percentage = 20
        self.move_delay = (5, 25)
        self.move_countdown = random.randrange(*self.move_delay)

        self.move_directions = [self.UP, self.RIGHT, self.DOWN, self.LEFT]
        self.direction = random.choice(self.move_directions)
        self.animation_direction = self.get_direction_string(self.direction)

    def get_direction_string(self, direction: Direction):
        """
        Translate the integer direction to the text based equiv.

        Args:
            direction (Direction): The direction integer

        Returns:
            str: The direction string
        """
        if direction == self.Direction.UP:
            return 'up'
        if direction == self.Direction.DOWN:
            return 'down'
        if direction in [self.Direction.LEFT, self.Direction.UP_LEFT, self.Direction.DOWN_LEFT]:
            return 'left'
        if direction in [self.Direction.RIGHT, self.Direction.UP_RIGHT, self.Direction.DOWN_RIGHT]:
            return 'right'

    def turn(self):
        """ Find a new direction to move. """
        idx = self.move_directions.index(self.direction)
        if random.randrange(0, 1) == 0:  # Turn Right
            idx += 1
            if idx >= len(self.move_directions):
                idx = 0
        else:  # Turn Left
            idx -= 1
            if idx < 0:
                idx = len(self.move_directions) - 1

        self.direction = self.move_directions[idx]

    def move(self):
        """ Hulks move in 4 directions, up down left right.  They randomly do 90deg turns left or right. """
        if random.randrange(1, 100) < self.turn_percentage:
            self.turn()

        while not self.valid_move(self.direction):
            self.turn()

        self.rect.center += self.get_vector(self.direction)
        self.animation_direction = self.get_direction_string(self.direction)
        self.update_animation()

    def update(self):
        if self.move_countdown <= 0:
            self.move()
            self.move_countdown = random.randrange(*self.move_delay)
        else:
            self.move_countdown -= 1

        for sprite in pygame.sprite.spritecollide(self, self.engine.family_group, False):
            sprite.die(self)

    def die(self, killer):
        """ Hulks never die, but they can be pushed back """
        self.rect.center += self.get_vector(killer.direction, 3)
        self.rect.clamp_ip(self.play_rect)

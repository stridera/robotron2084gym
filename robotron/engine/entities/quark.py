""" Quark Enemy Module"""
import random

import pygame

from .generator import Generator
from .tank import Tank


class Quark(Generator):
    """
    Quark Enemy Class

    Behavior:
        Quarks just move around diagnally, randomly choosing new directions.  They are generators like sphereoids
        and drop tanks periodically.
    """
    SPEED = 1
    MAX_MOVE_DELAY = [5, 30]

    def setup(self):
        super().setup()
        self.speed = self.config('speed', self.SPEED)
        self.move_delays = self.config('move_delays', self.MAX_MOVE_DELAY)
        self.vector = pygame.Vector2(0)
        self.turn_delay = 0

    def get_animations(self):
        """Returns the images used to animate the sprite."""

        return self.engine._get_sprites([
            'quark1', 'quark2', 'quark3', 'quark4', 'quark5', 'quark6', 'quark7', 'quark8', 'quark9'
        ])

    def move(self):
        if self.turn_delay == 0:
            self.turn_delay += random.randint(*self.move_delays)
            self.vector = pygame.Vector2(random.choice([-self.speed, self.speed]),
                                         random.choice([-self.speed, self.speed]))*5
        else:
            self.turn_delay -= 1

        self.rect.center += self.vector
        self.rect.clamp_ip(self.play_rect)

    def get_spawn(self):
        return Tank(self.engine, center=self.rect.center)

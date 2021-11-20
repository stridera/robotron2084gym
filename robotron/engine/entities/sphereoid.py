"""Sphereoid Enemy Module"""
import random

from .enforcer import Enforcer
from .generator import Generator


class Sphereoid(Generator):
    """
    Shereoid Enemy Class.

    Behavior:
        - They move oblivious to the player.
        - Their direction changes randomly and it can make them appear to weave.
        - Since they just choose a direction and go, they can end up in the corners.
        - Their purpose is spawn enforcers.
    """

    def reset(self):
        super().reset()
        self.update_curvature_and_countdowns()

    def get_animations(self):
        """Returns the images used to animate the sprite."""

        return self.engine.get_sprites([
            'sphereoid1', 'sphereoid2', 'sphereoid3', 'sphereoid4',
            'sphereoid5', 'sphereoid6', 'sphereoid7', 'sphereoid8'
        ])

    def get_spawn(self):
        """ Make some babies. """
        return Enforcer(self.engine, center=self.rect.center)

    def update_curvature_and_countdowns(self):
        """ Generate new values to move along. """
        self.move_curvature.x = random.randint(-50, 50) / 1000
        self.move_curvature.y = random.randint(-50, 50) / 1000
        self.move_delay = random.randrange(10, 32)

    def move(self):
        """ Sphereoids """
        if not self.alive:
            return

        self.move_delay -= 1
        if self.move_delay == 0:
            self.update_curvature_and_countdowns()

        self.move_deltas.x = min(self.SPEED, max(-self.SPEED, self.move_deltas.x + self.SPEED * self.move_curvature.x))
        self.move_deltas.y = min(self.SPEED, max(-self.SPEED, self.move_deltas.y + self.SPEED * self.move_curvature.y))
        self.rect.center += self.move_deltas
        self.rect.clamp_ip(self.play_rect)

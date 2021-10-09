import pygame
import random

from .base import Base
from .generator import Generator
from .tank import Tank


class Quark(Generator):
    """
    Quark Enemy Class

    Behavior:
        Quarks just move around diagnally, randomly choosing new directions.  They are generators like sphereoids
        and drop tanks periodically.
_

    """
    MAX_MOVE_DELAY = 30

    def get_animations(self):
        return self.get_engine().get_sprites([
            'quark1', 'quark2', 'quark3', 'quark4', 'quark5', 'quark6', 'quark7', 'quark8', 'quark9'
        ])

    def setup(self):
        super().setup()
        self.vector = pygame.Vector2(0)
        self.turnDelay = 0

    def move(self):
        if self.turnDelay == 0:
            self.turnDelay += random.randint(5, self.MAX_MOVE_DELAY)
            self.vector = pygame.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))*5
        self.rect.center += self.vector
        self.rect.clamp_ip(self.playRect)

    def get_spawn(self):
        return Tank(self.engine, self.rect.center)

""" Generator Enemy Subclass Module """
import random

import pygame

from .base import Base
from .floater import Floater


class Generator(Base):
    """
    Generator Base Enemy Class

    Behavior:
        Sphereoids and Quarks behave generally the same way.  While the move differently, they
        do the same cycle though sprites and eventually spawn either enforcers or tanks.  Both
        will revive on player death unless all spawns are dead.
    """
    SCORE = 1000
    PRE_SPAWN_CYCLE_LIMIT = 6  # Until we start spawning, we only show the first 6 images.
    SPEED = 5
    SPAWN_DELAY = 64

    def reset(self):
        self.cycle = self.PRE_SPAWN_CYCLE_LIMIT
        self.spawn_delay = random.randrange(self.SPAWN_DELAY / 8, self.SPAWN_DELAY)
        self.spawn_count = random.randrange(1, 6)
        self.spawning = False
        self.alive = True
        self.move_curvature = pygame.Vector2(0)
        self.move_deltas = pygame.Vector2(0)
        self.spawns = pygame.sprite.Group()

    def move(self):
        """ Moves the sprite.  Must be overridden. """
        raise NotImplementedError()

    def update(self):
        """ Update the sprite. """
        if self.alive:
            self.spawn_delay -= 1
            if self.spawn_delay <= 0:
                self.spawn()
            self.update_animation()
            self.move()
        else:
            if not self.spawns:
                self.kill()

    def get_spawn(self):
        """
        Return the class spawn type
        """
        raise NotImplementedError()

    def spawn(self):
        """ Spawn the babies. """
        self.cycle = len(self.animations)
        self.spawning = True
        self.spawn_delay = random.randrange(self.SPAWN_DELAY // 8, self.SPAWN_DELAY // 4)
        self.spawn_count -= 1

        spawn = self.get_spawn()
        self.engine.add_enemy(spawn)
        self.spawns.add(spawn)
        if self.spawn_count == 0:
            self.vanish()

    def die(self, killer):
        del killer
        self.engine.add_sprite(Floater(self.engine, center=self.rect.center, sprite_name='1000'))
        self.vanish()

    def vanish(self):
        """
        Generators don't die for good until their spawns are completely gone.  You could shoot a generator and
        then die to their spawn, and the original generator will appear, not the spawns.  Thus, we need to keep
        track of this and only kill them once all their spawns are gone.
        """
        self.rect.center = -100, -100
        self.alive = False

import pygame
import random

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

    def move(self):
        raise NotImplementedError()

    def update(self):
        if self.alive:
            self.spawnDelay -= 1
            if self.spawnDelay <= 0:
                self.spawn()
            self.update_animation()
            self.move()
        else:
            self.zero()
            if not self.spawns:
                self.kill()

    def get_spawn(self):
        """
        Return the class spawn type
        """
        raise NotImplementedError()

    def spawn(self):
        self.cycle = len(self.animations)
        self.spawning = True
        self.spawnDelay = random.randrange(self.SPAWN_DELAY // 8, self.SPAWN_DELAY // 4)
        self.spawnCount -= 1

        spawn = self.get_spawn()
        self.engine.add_enemy(spawn)
        self.spawns.add(spawn)
        if self.spawnCount == 0:
            self.vanish()

    def die(self, killer):
        deathSprite = Floater(self.engine, xy=self.rect.center, sprite_name='1000')
        self.engine.add_sprite(deathSprite)
        self.vanish()

    def vanish(self):
        """
        Generators don't die for good until their spawns are completely gone.  You could shoot a generator and
        then die to their spawn, and the original generator will appear, not the spawns.  Thus, we need to keep
        track of this and only kill them once all their spawns are gone.
        """
        self.rect.center = -100, -100
        self.alive = False

    def reset(self):
        self.cycle = self.PRE_SPAWN_CYCLE_LIMIT
        self.spawnDelay = random.randrange(self.SPAWN_DELAY / 8, self.SPAWN_DELAY)
        self.spawnCount = random.randrange(1, 6)
        self.spawning = False
        self.alive = True
        self.moveCurvature = pygame.Vector2(0)
        self.moveDeltas = pygame.Vector2(0)
        self.spawns = pygame.sprite.Group()

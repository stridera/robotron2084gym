""" Generator Enemy Subclass Module """
import pygame

from .base import Base
from .floater import Floater


class Generator(Base):
    """
    Generator Base Enemy Class

    Behavior:
        Sphereoids and Quarks behave generally the same way.  While they move differently, they
        do the same cycle through sprites and eventually spawn either enforcers or tanks.  Both
        will revive on player death unless all spawns are dead.

        Known exploit: There's a max number of active spawns allowed on screen (default 8).
        If all slots are full, the generator won't spawn more.  Players can exploit this by
        keeping spawns alive to prevent new ones from appearing.

        On player death: spawns are killed, and the generator reappears with a fresh spawn count.
    """
    PRE_SPAWN_CYCLE_LIMIT = 6  # Until we start spawning, we only show the first 6 images.
    SPAWN_DELAY = [8, 64]
    MAX_SPAWN_COUNT = [1, 6]
    MAX_ACTIVE_SPAWNS = 8  # Max spawns allowed on screen at once (across all generators of this type)

    def reset(self):
        self.cycle = self.PRE_SPAWN_CYCLE_LIMIT
        self.spawn_delays = self.config('spawn_delays', self.SPAWN_DELAY)
        self.spawn_delay = self.random_int(self.spawn_delays[0], self.spawn_delays[1])
        spawn_counts = self.config('spawn_counts', self.MAX_SPAWN_COUNT)
        self.spawn_count = self.random_int(spawn_counts[0], spawn_counts[1])
        self.max_active_spawns = self.config('max_active_spawns', self.MAX_ACTIVE_SPAWNS)
        self.alive = True
        self.move_curvature = pygame.Vector2(0)
        self.move_deltas = pygame.Vector2(0)
        self.spawns = pygame.sprite.Group()
        self.update_animation()
        self.random_location()

    def move(self):
        """ Moves the sprite.  Must be overridden. """
        raise NotImplementedError()

    def _count_active_spawns(self) -> int:
        """Count how many spawns of our type are currently alive on screen."""
        spawn_type = self.get_spawn_type()
        return sum(1 for s in self.engine.enemy_group if s.__class__.__name__ == spawn_type)

    def get_spawn_type(self) -> str:
        """Return the class name of the spawn type. Must be overridden."""
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
        Return a new spawn instance.
        """
        raise NotImplementedError()

    def spawn(self):
        """Spawn if under the active limit, otherwise wait."""
        if self._count_active_spawns() >= self.max_active_spawns:
            # Slots full - reset delay but don't decrement count
            self.spawn_delay = self.random_int(self.spawn_delays[0], self.spawn_delays[1])
            return

        self.cycle = len(self.animations)
        self.spawn_delay = self.random_int(self.spawn_delays[0], self.spawn_delays[1])
        self.spawn_count -= 1

        spawn = self.get_spawn()
        self.engine._add_enemy(spawn)
        self.spawns.add(spawn)
        if self.spawn_count == 0:
            self.vanish()

    def die(self, killer):
        del killer
        self.engine._add_sprite(Floater(self.engine, center=self.rect.center, sprite_name='1000'))
        self.vanish()

    def vanish(self):
        """
        Generators don't die for good until their spawns are completely gone.  You could shoot a generator and
        then die to their spawn, and the original generator will appear, not the spawns.  Thus, we need to keep
        track of this and only kill them once all their spawns are gone.
        """
        self.rect.center = -100, -100
        self.alive = False

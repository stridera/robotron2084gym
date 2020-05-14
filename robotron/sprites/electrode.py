import pygame
import random

from .enemy_base import Enemy


class Electrode(Enemy):

    def __init__(self, sprites, engine):
        self.alive = True

        level = engine.get_level() % 10
        if level > 7:
            level -= 1
        level *= 3

        # Electrode animations are for level 1-10.  7 doesn't have any
        # The first image is static until the die.
        # Then the electrode 'fades away' by going through cycles of the rest of the sprites.
        self.animations = []
        self.animations.append(sprites['electrode' + str(level + 1)])
        self.animations.append(sprites['electrode' + str(level + 2)])
        self.animations.append(sprites['electrode' + str(level + 3)])
        super().__init__(sprites, engine)

    def update(self):
        """
        The Enrichment Center reminds you that the Weighted Companion Cube will never threaten to stab you and,
        in fact, cannot speak. In the event that the Weighted Companion Cube does speak, the Enrichment Center
        urges you to disregard its advice.

        Electrodes, however, will stab you and thus you are recommended to keep your distance.

        They don't move...
        They kill grunts and die.  Hulks kill them.  Sphereoids and enforcers fly over them.
        """
        if self.alive:
            if any(self.rect.colliderect(sprite.rect)
                   for sprite in self.engine.get_enemy_group() if self != sprite):
                self.alive = False
        else:
            self.animationStep += 1

            if self.animationStep >= len(self.animations):
                self.kill()
            else:
                self.image = self.animations[self.animationStep]

    def die(self):
        self.alive = False

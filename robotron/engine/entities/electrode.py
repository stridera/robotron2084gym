# -*- coding: utf-8 -*-
import pygame
import random

from .base import Base


class Electrode(Base):
    """
    Electrode Enemy Class.

    Behavior:
        The Enrichment Center reminds you that the Weighted Companion Cube will never threaten to stab you and,
        in fact, cannot speak. In the event that the Weighted Companion Cube does speak, the Enrichment Center
        urges you to disregard its advice.

        Electrodes, however, will stab you and thus you are recommended to keep your distance.

        They don't move...
        They kill grunts and die.  Hulks kill them.  Sphereoids and enforcers fly over them.
    """

    def reset(self):
        self.alive = True

    def get_animations(self):
        engine = self.get_engine()

        # Electrodes use different images for level 1-10, skipping 7 and 9.  They repeat afterwards.
        # The first image is static until they die.
        # Then the electrode 'fades away' by going through cycles of the rest of the sprites.
        animationLevels = [
            engine.get_sprites(['electrode1', 'electrode2', 'electrode3']),  # 1, 11, 21, etc
            engine.get_sprites(['electrode4', 'electrode5', 'electrode6']),  # 2
            engine.get_sprites(['electrode7', 'electrode8', 'electrode9']),  # 3
            engine.get_sprites(['electrode10', 'electrode11', 'electrode12']),  # 4
            engine.get_sprites(['electrode13', 'electrode14', 'electrode15']),  # 5
            engine.get_sprites(['electrode16', 'electrode17', 'electrode18']),  # 6
            [],  # 7
            engine.get_sprites(['electrode25', 'electrode26', 'electrode27']),  # 8
            [],  # 9
            engine.get_sprites(['electrode19', 'electrode20', 'electrode21']),  # 10, 20, ect
        ]
        return animationLevels[(engine.get_level() % 10)]

    def update(self):
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

    def die(self, killer):
        self.alive = False

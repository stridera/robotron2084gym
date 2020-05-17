import pygame
import random

from .sprite_base import Base


class Electrode(Base):

    def __init__(self, sprites, engine):
        self.alive = True

        level = (engine.get_level() + 1) % 10

        # Electrode animations are for level 1-10.  We skip some for some levels.. mostly 7 and 9's
        # The first image is static until the die.
        # Then the electrode 'fades away' by going through cycles of the rest of the sprites.

        animationLevels = [
            [sprites['electrode19'], sprites['electrode20'], sprites['electrode21']],  # 0
            [sprites['electrode1'], sprites['electrode2'], sprites['electrode3']],  # 1
            [sprites['electrode4'], sprites['electrode5'], sprites['electrode6']],  # 2
            [sprites['electrode7'], sprites['electrode8'], sprites['electrode9']],  # 3
            [sprites['electrode10'], sprites['electrode11'], sprites['electrode12']],  # 4
            [sprites['electrode13'], sprites['electrode14'], sprites['electrode15']],  # 5
            [sprites['electrode16'], sprites['electrode17'], sprites['electrode18']],  # 6
            [],  # 7
            [sprites['electrode25'], sprites['electrode26'], sprites['electrode27']],  # 8
            [],  # 9
        ]

        self.animations = animationLevels[level]
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

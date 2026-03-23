"""Electrode Module"""
# -*- coding: utf-8 -*-
# pylint: disable=attribute-defined-outside-init

from .base import Base


# Enemy types that electrodes interact with
# Grunts die on contact (electrode also dies)
# Hulks crush electrodes
# All other enemies (Sphereoids, Enforcers, Brains, etc.) fly over them
GROUND_ENEMY_TYPES = ('Grunt', 'Hulk')


class Electrode(Base):
    """
    Electrode Enemy Class.

    Behavior:
        Electrodes are stationary obstacles.
        They kill grunts on contact (both die).
        Hulks crush them.
        Flying enemies (Sphereoids, Enforcers, Brains, cruise missiles) pass over them.
        The player dies on contact.
    """

    def reset(self):
        self.alive = True

    def get_animations(self):
        """Returns the images used to animate the sprite."""

        # The first image is static until they die.
        # Then the electrode 'fades away' by going through cycles of the rest of the sprites.
        animation_levels = [
            self.engine._get_sprites(['electrode1', 'electrode2', 'electrode3']),  # 1, 11, 21, etc
            self.engine._get_sprites(['electrode4', 'electrode5', 'electrode6']),  # 2
            self.engine._get_sprites(['electrode7', 'electrode8', 'electrode9']),  # 3
            self.engine._get_sprites(['electrode10', 'electrode11', 'electrode12']),  # 4
            self.engine._get_sprites(['electrode13', 'electrode14', 'electrode15']),  # 5
            self.engine._get_sprites(['electrode16', 'electrode17', 'electrode18']),  # 6
            [],  # 7
            self.engine._get_sprites(['electrode25', 'electrode26', 'electrode27']),  # 8
            [],  # 9
            self.engine._get_sprites(['electrode19', 'electrode20', 'electrode21']),  # 10, 20, ect
        ]
        return animation_levels[(self.engine.level % 10)]

    def update(self):
        if self.alive:
            for sprite in self.engine._get_enemy_group():
                if sprite is self:
                    continue
                sprite_type = sprite.__class__.__name__
                if sprite_type not in GROUND_ENEMY_TYPES:
                    continue
                if self.rect.colliderect(sprite.rect):
                    if sprite_type == 'Grunt':
                        # Grunts die on electrode contact, electrode also dies
                        self.engine.score += sprite.score()
                        sprite.die(self)
                    # Both grunts and hulks destroy the electrode
                    self.alive = False
                    break
        else:
            self.animation_step += 1
            if self.animation_step >= len(self.animations):
                self.kill()
            else:
                self.image = self.animations[self.animation_step]

    def die(self, killer):
        self.alive = False

"""Brain Enemy and Cruise Missile Module"""
from random import choice, randint

import pygame

from .base import Base
from .floater import Floater
from .prog import Prog

# pylint: disable=attribute-defined-outside-init


class CruiseMissile(Base):
    """
    Brains shoot snake-like cruise missiles at the player.

    Behavior:
    - The missiles zig zag toward the player.
    """
    SCORE = 25
    SPEED = 5
    DEFAULT_TIME_TO_LIVE = 50
    WIDTH = HEIGHT = 4

    def setup(self):
        """Setup"""
        self.time_to_live = self.DEFAULT_TIME_TO_LIVE
        self.vector = None
        self.trail_image = pygame.Surface([self.WIDTH, self.HEIGHT]).convert()
        pygame.draw.circle(self.trail_image, (255, 255, 255), (self.WIDTH//2, self.HEIGHT//2), 8, 0)

    def get_animations(self):
        """Returns the images used to animate the sprite."""
        images = []
        for color in ((255, 0, 0), (0, 255, 0), (0, 255, 0)):
            image = pygame.Surface([self.WIDTH, self.HEIGHT]).convert()
            pygame.draw.circle(image, color, (self.WIDTH//2, self.HEIGHT//2), 8, 0)
            images.append(image)
        return images

    def move(self):
        """Move the sprite."""
        self.engine.add_sprite(Floater(self.engine, center=self.rect.center, sprite=self.trail_image, delay=20))
        self.vector = self.get_vector_to_player()
        self.rect.center += self.vector * self.SPEED

    def update(self):
        """Sprite update method."""
        self.time_to_live -= 1
        if self.time_to_live == 0:
            self.kill()
        else:
            self.move()


class Brain(Base):
    """
    Brain Enemy

    Behavior:
        Brains fly around, brainwash humans, and shoot missiles.
    """

    def get_animations(self):
        """Returns the images used to animate the sprite."""

        return {
            'left': self.engine.get_sprites(['brain1', 'brain2', 'brain1', 'brain3']),
            'right': self.engine.get_sprites(['brain4', 'brain5', 'brain4', 'brain6']),
            'up': self.engine.get_sprites(['brain7', 'brain8', 'brain7', 'brain9']),
            'down': self.engine.get_sprites(['brain10', 'brain11', 'brain10', 'brain12']),
        }

    def reset(self):
        self.update_animation()
        self.random_location()

        use_mikey_bug = True
        family_sprites = self.engine.family_group.sprites()
        self.target = family_sprites[0] if family_sprites and use_mikey_bug else None
        self.speed = 1
        self.vector = pygame.Vector2(0)
        self.shoot_delay = randint(30, 70)

        self.programming = False
        self.programming_time = 60
        self.programming_offset = 5
        self.countdown = 0

    def update(self):
        self.shoot_delay -= 1
        if self.engine.frame % 3 == 0:
            self.update_animation()
        if self.programming:
            self.program()
            self.countdown -= 1
            if self.countdown == 0:
                self.programming = False
        elif self.shoot_delay <= 0:
            self.shoot()
        else:
            self.move()

    def move(self):
        """ Move the Brain. """
        if self.target is None or not self.engine.family_group.has(self.target):
            family_group = self.engine.family_group.sprites()
            if family_group:
                self.target = choice(family_group)
            else:
                self.target = self.engine.player

        if self.engine.frame % 5 == 0:
            self.vector = self.get_vector_to_point(self.target.rect.center, True)
            x, y = self.vector
            if x > 0:
                self.animation_direction = 'right'
            elif x < 0:
                self.animation_direction = 'left'
            elif y > 0:
                self.animation_direction = 'up'
            elif y < 0:
                self.animation_direction = 'down'

        self.rect.center += self.vector * self.speed
        self.rect.clamp_ip(self.play_rect)

        if self.target != self.engine.player:
            if pygame.sprite.spritecollide(self, [self.target], False):
                self.create_prog()

    def create_prog(self):
        """ Convert a human into a Prog (Programmed Human) """
        self.programming = True
        self.countdown = self.programming_time

        srect = self.rect  # Self Rect
        trect = self.target.rect  # Target Rect
        # If the target is to the left and not too close to the left wall, program on the left
        if trect.x < srect.x and trect.left > self.play_rect.left + trect.width:
            self.animation_direction = 'left'
            center = srect.left - self.programming_offset - (trect.width // 2), srect.centery
        else:
            self.animation_direction = 'right'
            center = srect.right + self.programming_offset + (trect.width // 2), srect.centery
        self.engine.add_enemy(Prog(self.engine, center=center, family=self.target.PREFIX))
        self.target.kill()

    def program(self):
        """ Animate the brain with flashing colors during programming. """
        image = self.animations[self.animation_direction][0]
        image.set_colorkey((0, 0, 0))
        color = ((255, 0, 0), (0, 255, 0), (0, 255, 0))[self.engine.frame % 3]
        inv = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        inv.fill(color)
        inv.blit(image, (0, 0), None, pygame.BLEND_RGB_SUB)
        self.image = inv

    def shoot(self):
        """ Fire the guns. """
        self.shoot_delay = randint(30, 70)
        self.engine.add_enemy(CruiseMissile(self.engine, center=self.rect.center))

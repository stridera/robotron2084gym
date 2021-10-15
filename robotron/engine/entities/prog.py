""" Programmed Human Enemy Module"""
import random

import pygame

from .floater import Floater
from .family import Family


class Prog(Family):
    """
    Programmed Family Class

    Behavior:
        Family members wander around, randomly choosing a new direction.
        Programmed family rush mostly toward the player.  They do not return if the player dies.
    """

    def setup(self):
        self.speed = 4
        self.move_delay = 5
        self.vector = None
        self.score = 100
        self.programming_time = 60
        self.offset = 0
        self.speed = 3

        self.reset()

    def get_animations(self):
        """Returns the images used to animate the sprite."""

        prefix = self.args['family']
        return {
            'left': self.engine.get_sprites([prefix + '1', prefix + '2', prefix + '1', prefix + '3']),
            'right': self.engine.get_sprites([prefix + '4', prefix + '5', prefix + '4', prefix + '6']),
            'down': self.engine.get_sprites([prefix + '7', prefix + '8', prefix + '7', prefix + '9']),
            'up': self.engine.get_sprites([prefix + '10', prefix + '11', prefix + '10', prefix + '12']),
        }

    def update_animation(self):
        animations = self.animations[self.animation_direction or 'down']
        self.animation_step += 1
        if self.animation_step >= (self.cycle or len(animations)):
            self.animation_step = 0

        image = animations[self.animation_step]
        color = ((255, 0, 0), (0, 255, 0), (0, 255, 0))[self.engine.frame % 3]
        inv = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        inv.fill(color)
        inv.blit(image, (0, 0), None, pygame.BLEND_RGB_SUB)
        self.image = inv

    def reset(self):
        return self.kill()

    def move(self):
        """
        Programmed humans move only in the carindal directions.  They re-evaluate every little bit.
        It appears they mostly attempt to move toward the player.
        """
        if self.vector is None or self.engine.frame % self.move_delay == 0:
            prect = self.engine.player.rect
            x = 1 if prect.x > self.rect.x else -1
            y = 1 if prect.y > self.rect.y else -1
            # Needs to be tweeked.  Mostly move toward the player.
            if random.random() < 0.25:
                x = -x
            if random.random() < 0.25:
                y = -y
            self.vector = pygame.Vector2(x, y)
        self.engine.add_sprite(Floater(self.engine, center=self.rect.center, sprite=self.image, delay=5))
        self.rect.center += self.vector * self.speed
        self.rect.clamp_ip(self.play_rect)

    def get_score(self):
        return self.score

    def collected(self):
        pass

    def die(self, killer):
        self.kill()

    def update(self):
        """
        Family members just keep walking continuously
        """
        self.update_animation()

        if self.programming_time > 0:
            if self.engine.frame % 2 == 0:
                self.rect.y -= self.offset
                self.offset = random.randint(0, self.rect.height) - (self.rect.height // 2)
                self.rect.y += self.offset
            self.programming_time -= 1
        else:
            self.move()

        # self.program(self.rect.center)

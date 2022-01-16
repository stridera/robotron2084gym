""" Module for the Player and their bullets. """
from typing import TYPE_CHECKING
import pygame
from .base import Base

if TYPE_CHECKING:
    from ..engine import Engine


class Bullet(Base):
    """
    Bullets shot from the player.
    """
    WIDTH = 16
    HEIGHT = 16

    def __init__(self, engine: 'Engine', x, y, direction):
        self.direction = direction
        super().__init__(engine)
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.speed = 15

    def get_animations(self):
        """Returns the images used to animate the sprite."""

        weight = 2

        image = pygame.Surface([self.WIDTH, self.HEIGHT]).convert()

        if self.direction in [self.UP, self.DOWN]:
            pygame.draw.line(image, (255, 255, 255), (self.WIDTH // 2, 0), (self.WIDTH // 2, self.HEIGHT), weight)
        elif self.direction in [self.RIGHT, self.LEFT]:
            pygame.draw.line(image, (255, 255, 255), (0, self.HEIGHT // 2), (self.WIDTH, self.HEIGHT // 2), weight)
        elif self.direction in [self.UP_RIGHT, self.DOWN_LEFT]:
            pygame.draw.line(image, (255, 255, 255), (self.WIDTH, 0), (0, self.HEIGHT), weight)
        else:
            pygame.draw.line(image, (255, 255, 255), (0, 0), (self.WIDTH, self.HEIGHT), weight)

        return [image]

    def update(self):
        vector = self.get_vector(self.direction)
        self.rect.center += vector

        hits = pygame.sprite.spritecollide(self, self.engine._get_enemy_group(), False)
        for sprite in hits:
            self.engine.score += sprite.score()
            sprite.die(self)
            self.kill()

        if not self.play_rect.contains(self.rect):
            self.kill()

    def reset(self):
        self.kill()


class Player(pygame.sprite.Sprite):
    """
    The savior of humanity.
    """
    UP = 1
    UP_RIGHT = 2
    RIGHT = 3
    DOWN_RIGHT = 4
    DOWN = 5
    DOWN_LEFT = 6
    LEFT = 7
    UP_LEFT = 8

    def __init__(self, engine: 'Engine'):
        super().__init__()
        self.image = None

        self.animations = {
            'left': engine._get_sprites(['player1', 'player2', 'player1', 'player3']),
            'right': engine._get_sprites(['player4', 'player5', 'player4', 'player6']),
            'down': engine._get_sprites(['player7', 'player8', 'player7', 'player9']),
            'up': engine._get_sprites(['player10', 'player11', 'player10', 'player12']),
        }

        self.play_rect = engine.play_rect
        self.engine = engine
        self.speed = 5
        self.shoot_delay = 5
        self.shoot_delay_remaining = 0
        self.animation_step = 0
        self.animation_direction = 'down'

        self.reset()

    def reset(self):
        """ Reset the sprite. """
        self.shoot_delay_remaining = 0
        self.animation_step = 0
        self.animation_direction = 'down'

        self.image = self.animations[self.animation_direction][self.animation_step]

        self.rect = self.image.get_rect()
        self.rect.x = self.play_rect.x + (self.play_rect.width // 2)
        self.rect.y = self.play_rect.y + (self.play_rect.height // 2)

    def move(self, move):
        """ Move the player. """
        if move:
            direction = 'down'
            if move in [self.UP, self.UP_LEFT, self.UP_RIGHT]:
                self.rect.y -= self.speed
                direction = 'up'
            if move in [self.DOWN, self.DOWN_LEFT, self.DOWN_RIGHT]:
                self.rect.y += self.speed
                direction = 'down'
            if move in [self.LEFT, self.UP_LEFT, self.DOWN_LEFT]:
                self.rect.x -= self.speed
                direction = 'left'
            if move in [self.RIGHT, self.UP_RIGHT, self.DOWN_RIGHT]:
                self.rect.x += self.speed
                direction = 'right'

            self._set_animation_direction(direction)
            self.image = self.animations[self.animation_direction][self.animation_step]
            self.rect.clamp_ip(self.play_rect)

    def shoot(self, shoot):
        """ Shoot the guns. """
        if shoot:
            if self.shoot_delay_remaining <= 0:
                bullet = Bullet(self.engine, self.rect.x, self.rect.y, shoot)
                self.engine._add_sprite(bullet)
                self.shoot_delay_remaining = self.shoot_delay

    def update(self):
        """ Update Loop """
        self.shoot_delay_remaining -= 1

        for sprite in pygame.sprite.spritecollide(self, self.engine.family_group, False):
            sprite.collected()

    def _set_animation_direction(self, direction):
        """ Get the direction the sprite faces based on the passed direction. """
        if self.animation_direction == direction:
            self.animation_step += 1
            if self.animation_step >= len(self.animations[self.animation_direction]):
                self.animation_step = 0
        else:
            self.animation_direction = direction
            self.animation_step = 0

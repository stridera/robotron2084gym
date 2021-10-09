from typing import Type
import pygame
from .base import Base

from typing import TYPE_CHECKING
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
        self.moveSpeed = 15

    def get_animations(self):
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

        hit = pygame.sprite.spritecollide(self, self.engine.get_enemy_group(), False)
        if hit:
            sprite = hit[0]
            self.engine.add_score(sprite.get_score())
            sprite.die(self)
            self.kill()

        if not self.playRect.contains(self.rect):
            self.kill()

    def zero(self):
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

        self.animations = {
            'left': engine.get_sprites(['player1', 'player2', 'player1', 'player3']),
            'right': engine.get_sprites(['player4', 'player5', 'player4', 'player6']),
            'down': engine.get_sprites(['player7', 'player8', 'player7', 'player9']),
            'up': engine.get_sprites(['player10', 'player11', 'player10', 'player12']),
        }

        self.playRect = engine.get_play_area()
        self.engine = engine
        self.moveSpeed = 5
        self.shootDelay = 5
        self.shootDelayRemaining = 0
        self.animationStep = 0
        self.animationDirection = 'down'

        self.reset()

    def move(self, move):
        if move:
            dir = 'down'
            if move in [self.UP, self.UP_LEFT, self.UP_RIGHT]:
                self.rect.y -= self.moveSpeed
                dir = 'up'
            if move in [self.DOWN, self.DOWN_LEFT, self.DOWN_RIGHT]:
                self.rect.y += self.moveSpeed
                dir = 'down'
            if move in [self.LEFT, self.UP_LEFT, self.DOWN_LEFT]:
                self.rect.x -= self.moveSpeed
                dir = 'left'
            if move in [self.RIGHT, self.UP_RIGHT, self.DOWN_RIGHT]:
                self.rect.x += self.moveSpeed
                dir = 'right'

            self._setAnimationDirection(dir)
            self.image = self.animations[self.animationDirection][self.animationStep]
            self.rect.clamp_ip(self.playRect)

    def shoot(self, shoot):
        if shoot:
            if self.shootDelayRemaining <= 0:
                bullet = Bullet(self.engine, self.rect.x, self.rect.y, shoot)
                self.engine.add_sprite(bullet)
                self.shootDelayRemaining = self.shootDelay

    def update(self):
        self.shootDelayRemaining -= 1

        for sprite in pygame.sprite.spritecollide(self, self.engine.get_family_group(), False):
            sprite.collected()

    def zero(self):
        pass

    def reset(self):
        self.shootDelayRemaining = 0
        self.animationStep = 0
        self.animationDirection = 'down'

        self.image = self.animations[self.animationDirection][self.animationStep]

        self.rect = self.image.get_rect()
        self.rect.x = self.playRect.x + (self.playRect.width // 2)
        self.rect.y = self.playRect.y + (self.playRect.height // 2)

    def _setAnimationDirection(self, dir):
        if self.animationDirection == dir:
            self.animationStep += 1
            if self.animationStep >= len(self.animations[self.animationDirection]):
                self.animationStep = 0
        else:
            self.animationDirection = dir
            self.animationStep = 0

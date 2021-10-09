from random import randint, randrange
from robotron.engine.entities.player import Bullet
import pygame

from .base import Base


class TankBullet(Base):
    """
    Tank Bullets.  They're bouncy boys.
    """

    MIN_SPEED = 10
    MAX_SPEED = 20
    DEFAULT_TIME_TO_LIVE = 80

    def get_animations(self):
        width = height = 16
        weight = 2
        image = pygame.Surface([width, height]).convert()
        pygame.draw.circle(image, (255, 0, 0), (width//2, height//2), 8, weight)
        return [image]

    def setup(self):
        self.timeToLive = self.DEFAULT_TIME_TO_LIVE
        self.vector = None

    def get_trajectory(self):
        if not self.vector:
            distanceToPlayer = self.get_distance_to_player()
            max_distance = self.get_engine().get_play_area_distance()
            self.speed = ((distanceToPlayer * self.MAX_SPEED) / max_distance) + self.MIN_SPEED
            x, y = self.rect.center
            px, py = self.get_engine().get_player().rect.center
            attack = randrange(10)
            if attack < 2:
                # reflect off top wall
                self.vector = self.get_vector_to_point((x + (px - x) // 2, self.playRect.top))
            elif attack < 4:
                # reflect off bottom wall
                self.vector = self.get_vector_to_point((x + (px - x) // 2, self.playRect.bottom))
            elif attack < 6:
                # reflect off right
                self.vector = self.get_vector_to_point((self.playRect.right, y + (py - y) // 2))
            elif attack < 8:
                # reflect off left
                self.vector = self.get_vector_to_point((self.playRect.left, y + (py - y) // 2))
            else:
                self.vector = self.get_vector_to_player()
        return self.vector * self.speed

    def move(self):
        self.rect.center += self.get_trajectory()

        if self.rect.top <= self.playRect.top:
            self.vector = self.vector.reflect(pygame.Vector2([0, 1]))
        if self.rect.bottom >= self.playRect.bottom:
            self.vector = self.vector.reflect(pygame.Vector2([0, -1]))
        if self.rect.left >= self.playRect.left:
            self.vector = self.vector.reflect(pygame.Vector2([1, 0]))
        if self.rect.right <= self.playRect.right:
            self.vector = self.vector.reflect(pygame.Vector2([-1, 0]))

        self.rect.clamp_ip(self.playRect)

    def update(self):
        self.timeToLive -= 1
        if self.timeToLive == 0:
            self.kill()
        else:
            self.move()

    def reset(self):
        self.kill()


class Tank(Base):
    """
    Tank Enemy

    Behavior:
        Tanks drive around and shoot bullets that bounce around the scene.
    """
    BULLETS = 20

    def get_animations(self):
        return self.get_engine().get_sprites(['tank1', 'tank2', 'tank3', 'tank4'])

    def setup(self):
        self.bullets = 20
        self.active = 0
        self.shootDelay = randint(10, 30)

    def move(self):
        self.move_toward_player(2)

    def update(self):
        self.move()
        self.shoot()
        self.update_animation()

    def shoot(self):
        if self.bullets > 0:
            self.shootDelay -= 1
            if self.shootDelay == 0:
                self.bullets -= 1
                self.shootDelay = randint(5, 30)
                bullet = TankBullet(self.engine, self.rect.center)
                self.engine.add_sprite(bullet)

    def reset(self):
        super().reset()
        self.bullets = self.BULLETS

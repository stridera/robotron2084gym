"""Tank Enemy and Tank Shell Class"""
from random import randint, randrange

import pygame

from .base import Base


class TankShell(Base):
    """
    Tank Bullets.  They're bouncy boys.
    """

    MIN_SPEED = 10
    MAX_SPEED = 20
    TIME_TO_LIVE = 80

    WIDTH = HEIGHT = 16
    WEIGHT = 2

    def setup(self):
        self.min_speed = self.config('min_speed', self.MIN_SPEED)
        self.max_speed = self.config('max_speed', self.MAX_SPEED)
        self.time_to_live = self.config('time_to_live', self.TIME_TO_LIVE)
        self.vector = None

    def get_animations(self):
        """Returns the images used to animate the sprite."""
        image = pygame.Surface([self.WIDTH, self.HEIGHT]).convert()
        pygame.draw.circle(image, (255, 0, 0), (self.WIDTH//2, self.HEIGHT//2), 8, self.WEIGHT)
        return [image]

    def get_trajectory(self):
        """ Calculate the new trajectory. """
        if not self.vector:
            distance_to_player = self.get_distance_to_player()
            max_distance = self.engine._get_play_area_distance()
            self.speed = ((distance_to_player * self.max_speed) / max_distance) + self.min_speed
            x, y = self.rect.center
            player_x, player_y = self.engine.player.rect.center
            attack = randrange(10)
            if attack < 2:
                # reflect off top wall
                self.vector = self.get_vector_to_point((x + (player_x - x) // 2, self.play_rect.top))
            elif attack < 4:
                # reflect off bottom wall
                self.vector = self.get_vector_to_point((x + (player_x - x) // 2, self.play_rect.bottom))
            elif attack < 6:
                # reflect off right
                self.vector = self.get_vector_to_point((self.play_rect.right, y + (player_y - y) // 2))
            elif attack < 8:
                # reflect off left
                self.vector = self.get_vector_to_point((self.play_rect.left, y + (player_y - y) // 2))
            else:
                self.vector = self.get_vector_to_player()
        return self.vector * self.speed

    def move(self):
        """ Move toward the player. """
        self.rect.center += self.get_trajectory()

        if self.rect.top <= self.play_rect.top:
            self.vector = self.vector.reflect(pygame.Vector2([0, 1]))
        if self.rect.bottom >= self.play_rect.bottom:
            self.vector = self.vector.reflect(pygame.Vector2([0, -1]))
        if self.rect.left >= self.play_rect.left:
            self.vector = self.vector.reflect(pygame.Vector2([1, 0]))
        if self.rect.right <= self.play_rect.right:
            self.vector = self.vector.reflect(pygame.Vector2([-1, 0]))

        self.rect.clamp_ip(self.play_rect)

    def update(self):
        self.time_to_live -= 1
        if self.time_to_live == 0:
            self.kill()
        else:
            self.move()

    def reset(self):
        self.kill()


class Tank(Base):
    """
    Tank Enemy

    Spwaned by Quarks.

    Behavior:
        Tanks drive around and shoot bullets that bounce around the scene.
    """
    BULLETS = 20
    SHOOT_DELAYS = (15, 60)

    def setup(self):
        """Setup the sprite."""
        self.bullets = self.config('bullets', self.BULLETS)
        self.shoot_delays = self.config('shoot_delays', self.SHOOT_DELAYS)
        self.shoot_delay = randint(*self.shoot_delays)
        self.active = 0

    def get_animations(self):
        """Returns the images used to animate the sprite."""
        return self.engine._get_sprites(['tank1', 'tank2', 'tank3', 'tank4'])

    def move(self):
        """Move the sprite."""
        self.move_toward_player(2)

    def update(self):
        """Sprite Update method"""
        self.move()
        self.shoot()
        self.update_animation()

    def shoot(self):
        """Fire the guns!"""
        if self.bullets > 0:
            self.shoot_delay -= 1
            if self.shoot_delay == 0:
                self.bullets -= 1
                self.shoot_delay = randint(*self.shoot_delays)
                bullet = TankShell(self.engine, center=self.rect.center)
                self.engine._add_sprite(bullet)

    def reset(self):
        """Reset the sprite after the player dies."""
        super().reset()
        self.bullets = self.BULLETS

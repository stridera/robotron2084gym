from random import choice, randint
import pygame
from robotron.engine.entities.floater import Floater

from robotron.engine.entities.prog import Prog

from .base import Base


class CruzMissile(Base):
    SCORE = 25
    SPEED = 5
    DEFAULT_TIME_TO_LIVE = 50
    WIDTH = HEIGHT = 4

    def setup(self):
        self.timeToLive = self.DEFAULT_TIME_TO_LIVE
        self.vector = None
        self.trail_image = pygame.Surface([self.WIDTH, self.HEIGHT]).convert()
        pygame.draw.circle(self.trail_image, (255, 255, 255), (self.WIDTH//2, self.HEIGHT//2), 8, 0)

    def get_image(self):
        color = ((255, 0, 0), (0, 255, 0), (0, 255, 0))[self.engine.frame % 3]
        image = pygame.Surface([self.WIDTH, self.HEIGHT]).convert()
        pygame.draw.circle(image, color, (self.WIDTH//2, self.HEIGHT//2), 8, 0)
        return image

    def get_animations(self):
        return [self.get_image()]

    def move(self):
        self.engine.add_sprite(Floater(self.engine, xy=self.rect.center, sprite=self.trail_image, delay=20))
        self.image = self.get_image()
        self.vector = self.get_vector_to_player()
        self.rect.center += self.vector * self.SPEED

    def update(self):
        self.timeToLive -= 1
        if self.timeToLive == 0:
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
        engine = self.get_engine()
        return {
            'left': engine.get_sprites(['brain1', 'brain2', 'brain1', 'brain3']),
            'right': engine.get_sprites(['brain4', 'brain5', 'brain4', 'brain6']),
            'up': engine.get_sprites(['brain7', 'brain8', 'brain7', 'brain9']),
            'down': engine.get_sprites(['brain10', 'brain11', 'brain10', 'brain12']),
        }

    def reset(self):
        self.update_animation()
        self.random_location()

        use_mikey_bug = True
        family_sprites = self.get_engine().get_family_group().sprites()
        self.target = family_sprites[0] if family_sprites and use_mikey_bug else None
        self.speed = 1
        self.vector = pygame.Vector2(0)
        self.shootDelay = randint(30, 70)

        self.programming = False
        self.programmingTime = 60
        self.programmingOffset = 5
        self.countdown = 0

    def update(self):
        self.shootDelay -= 1
        if self.engine.frame % 3 == 0:
            self.update_animation()
        if self.programming:
            self.program()
            self.countdown -= 1
            if self.countdown == 0:
                self.programming = False
        elif self.shootDelay <= 0:
            self.shoot()
        else:
            self.move()

    def move(self):
        if self.target is None or not self.engine.get_family_group().has(self.target):
            familyGroup = self.engine.get_family_group().sprites()
            if familyGroup:
                self.target = choice(familyGroup)
            else:
                self.target = self.engine.player

        if self.engine.frame % 5 == 0:
            self.vector = self.get_vector_to_point(self.target.rect.center, True)
            x, y = self.vector
            if x > 0:
                self.animationDirection = 'right'
            elif x < 0:
                self.animationDirection = 'left'
            elif y > 0:
                self.animationDirection = 'up'
            elif y < 0:
                self.animationDirection = 'down'

        self.rect.center += self.vector * self.speed
        self.rect.clamp_ip(self.playRect)

        if self.target != self.engine.player:
            if pygame.sprite.spritecollide(self, [self.target], False):
                self.create_prog()

    def create_prog(self):
        self.programming = True
        self.countdown = self.programmingTime

        srect = self.rect  # Self Rect
        trect = self.target.rect  # Target Rect
        # If the target is to the left and not too close to the left wall, program on the left
        if trect.x < srect.x and trect.left > self.playRect.left + trect.width:
            self.animationDirection = 'left'
            xy = srect.left - self.programmingOffset - (trect.width // 2), srect.centery
        else:
            self.animationDirection = 'right'
            xy = srect.right + self.programmingOffset + (trect.width // 2), srect.centery
        self.engine.add_enemy(Prog(self.engine, xy=xy, family=self.target.PREFIX))
        self.target.kill()

    def program(self):
        image = self.animations[self.animationDirection][0]
        image.set_colorkey((0, 0, 0))
        color = ((255, 0, 0), (0, 255, 0), (0, 255, 0))[self.engine.frame % 3]
        inv = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        inv.fill(color)
        inv.blit(image, (0, 0), None, pygame.BLEND_RGB_SUB)
        self.image = inv

    def shoot(self):
        self.shootDelay = randint(30, 70)
        self.engine.add_enemy(CruzMissile(self.engine, xy=self.rect.center))

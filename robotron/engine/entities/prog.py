import pygame
import random

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
        self.moveSpeed = 4
        self.moveDelay = 5
        self.deathDelay = 15
        self.moveVector = None
        self.progScore = 100
        self.programmingTime = 60
        self.offset = 0
        self.progSpeed = 3
        self.moveTrail = []
        self.reset()

    def get_animations(self):
        engine = self.get_engine()
        prefix = self.args['family']
        return {
            'left': engine.get_sprites([prefix + '1', prefix + '2', prefix + '1', prefix + '3']),
            'right': engine.get_sprites([prefix + '4', prefix + '5', prefix + '4', prefix + '6']),
            'down': engine.get_sprites([prefix + '7', prefix + '8', prefix + '7', prefix + '9']),
            'up': engine.get_sprites([prefix + '10', prefix + '11', prefix + '10', prefix + '12']),
        }

    def update_animation(self):
        animations = self.animations[self.animationDirection or 'down']
        self.animationStep += 1
        if self.animationStep >= (self.cycle or len(animations)):
            self.animationStep = 0

        image = animations[self.animationStep]
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
        if self.moveVector is None or self.engine.frame % self.moveDelay == 0:
            prect = self.engine.player.rect
            x = 1 if prect.x > self.rect.x else -1
            y = 1 if prect.y > self.rect.y else -1
            # Needs to be tweeked.  Mostly move toward the player.
            if random.random() < 0.25:
                x = -x
            if random.random() < 0.25:
                y = -y
            self.moveVector = pygame.Vector2(x, y)
        self.engine.add_sprite(Floater(self.engine, xy=self.rect.center, sprite=self.image, delay=5))
        self.rect.center += self.moveVector * self.progSpeed
        self.rect.clamp_ip(self.playRect)

    def get_score(self):
        return self.progScore

    def collected(self):
        pass

    def die(self, killer):
        self.kill()

    def update(self):
        """
        Family members just keep walking continuously
        """
        self.update_animation()

        if self.programmingTime > 0:
            if self.engine.frame % 2 == 0:
                self.rect.y -= self.offset
                self.offset = random.randint(0, self.rect.height) - (self.rect.height // 2)
                self.rect.y += self.offset
            self.programmingTime -= 1
        else:
            self.move()

        # self.program(self.rect.center)

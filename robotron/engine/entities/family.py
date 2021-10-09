import pygame
import random

from .base import Base
from .floater import Floater


class Family(Base):
    """
    Family Class

    Behavior:
        Family members wander around, randomly choosing a new direction.
        Programmed family rush mostly toward the player.  They do not return if the player dies.
    """

    def setup(self):
        self.isAlive = True
        self.isProg = False
        self.moveSpeed = 4
        self.moveDelay = 5
        self.deathDelay = 15

        self.progScore = 100
        self.programmingTime = 60
        self.offset = 0
        self.progSpeed = 3
        self.moveTrail = []
        self.reset()

    def get_animations(self):
        engine = self.get_engine()
        prefix = self.PREFIX
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

        self.image = animations[self.animationStep]

    def reset(self):
        self.moveDirection = random.randrange(1, 8)
        self.update_animation()
        self.random_location()

    def move(self):
        """
        Family Members just choose a direction and go.  They change randomly or when they hit a wall.

        """
        if self.engine.frame % self.moveDelay == 0:
            validDirs = list(range(1, 8))

            # If we move into a wall or quark, we need to choose a new direction
            direction = self.moveDirection
            while not self.valid_move(direction):
                if direction in validDirs:
                    validDirs.remove(direction)
                if len(validDirs) == 0:
                    direction = 0
                    break
                else:
                    direction = random.choice(validDirs)

            self.moveVector = self.get_vector(direction)
            self.rect.center += self.moveVector
            self.moveDirection = direction

    def get_score(self):
        """ Happens in the engine """
        pass

    def collected(self):
        level = self.engine.family_collected()
        level = min(level, 5)
        self.engine.add_sprite(Floater(self.engine, xy=self.rect.center, sprite_name=str(level*1000)))
        self.kill()

    def die(self, killer):
        self.engine.add_sprite(Floater(self.engine, xy=self.rect.center, sprite_name='familydeath'))
        self.kill()

    def update(self):
        """
        Family members just keep walking continuously
        """
        self.update_animation()

        if self.isAlive:
            if self.engine.frame % self.moveDelay == 0:
                self.move()

            for sprite in pygame.sprite.spritecollide(self, self.engine.get_enemy_group(), False):
                if sprite.__class__.__name__ == 'Hulk':
                    self.die(sprite)
        else:
            self.deathDelay -= 1
            if self.deathDelay <= 0:
                self.kill()

        # self.program(self.rect.center)


class Mommy(Family):
    PREFIX = 'mommy'


class Daddy(Family):
    PREFIX = 'daddy'


class Mikey(Family):
    PREFIX = 'mikey'

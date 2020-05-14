import pygame
import random

from .enemy_base import Enemy


class Grunt(Enemy):

    def __init__(self, sprites, engine):
        self.animations = [
            sprites['grunt1'],
            sprites['grunt2'],
            sprites['grunt1'],
            sprites['grunt3'],
        ]
        super().__init__(sprites, engine)

        self.score = 100

        self.moveSpeed = 7
        self.moveDelayMax = 25
        self.moveDelayMin = 5
        self.moveDelayRemaining = random.randrange(self.moveDelayMin, self.moveDelayMax)

    def move(self):
        """ Grunts move toward the player """
        super().move()
        player_vec = pygame.Vector2(self.engine.player.rect.center)
        my_vec = pygame.Vector2(self.rect.center)

        _, angle = (my_vec - player_vec).as_polar()  # returns angle with 0 as to the right

        if abs(angle) <= 45:  # Right
            self.rect.x -= self.moveSpeed

        if abs(angle) >= 135:  # Left
            self.rect.x += self.moveSpeed

        if angle >= 45 and angle <= 135:
            self.rect.y -= self.moveSpeed

        if angle <= -45 and angle >= -135:
            self.rect.y += self.moveSpeed

    def update(self):

        if self.moveDelayRemaining <= 0:
            self.move()
            self.moveDelayRemaining = random.randrange(self.moveDelayMin, self.moveDelayMax)
        else:
            self.moveDelayRemaining -= 1

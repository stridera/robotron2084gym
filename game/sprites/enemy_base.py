import pygame
import random


class Enemy(pygame.sprite.Sprite):

    def __init__(self, sprites, engine):
        super().__init__()

        self.playRect = engine.get_play_area()
        self.engine = engine
        self.score = 0
        self.moveSpeed = 5

        self.animationStep = 0
        self.image = self.animations[self.animationStep]

        self.random_location()

    def update(self):
        self.animationStep += 1
        if self.animationStep >= len(self.animations):
            self.animationStep = 0

    def zero(self):
        self.rect.x = -100
        self.rect.y = -100

    def reset(self):
        self.animationStep = 0
        self.image = self.animations[self.animationStep]
        self.random_location()

    def get_score(self):
        return self.score

    def random_location(self):
        (sprite_width, sprite_height) = self.image.get_rect().size

        self.rect = self.image.get_rect()
        playerBox = self.engine.get_player_box()

        validLocation = False
        tries = 0
        while not validLocation:
            tries += 1
            self.rect.x = self.playRect.x + random.randrange(self.playRect.width - sprite_width)
            self.rect.y = self.playRect.y + random.randrange(self.playRect.height - sprite_height)

            if tries > 25:
                print("Warning!  Enemy Placement Overflow.")
                break

            # Prevent from being too close to the player:
            if playerBox.contains(self.rect):
                continue

            # Prevent sprites from overlapping
            if any(self.rect.colliderect(sprite.rect)
                   for sprite in self.engine.get_all_group() if self != sprite):
                continue

            validLocation = True

import pygame
import random


class Base(pygame.sprite.Sprite):

    def __init__(self, sprites, engine):
        super().__init__()

        self.type = None
        self.playRect = engine.get_play_area()
        self.engine = engine
        self.score = 0

        self.moveSpeed = 0  # Distance to move per step
        self.moveDelay = 0  # Time between steps
        self.moveDelayRemaining = self.moveDelay  # Time remaining until next step

        self.animationStep = 0
        self.animationDirection = None
        self.image = self.get_animations()[self.animationStep]

        self.random_location()

    def update(self):
        pass

    def get_vector(self, dir):
        if dir == 0:
            return pygame.math.Vector2(0)
        elif dir == 1:
            return pygame.math.Vector2(0, -self.moveDelay)
        elif dir == 2:
            return pygame.math.Vector2(self.moveDelay, -self.moveDelay)
        elif dir == 3:
            return pygame.math.Vector2(self.moveDelay, 0)
        elif dir == 4:
            return pygame.math.Vector2(self.moveDelay, self.moveDelay)
        elif dir == 5:
            return pygame.math.Vector2(0, self.moveDelay)
        elif dir == 6:
            return pygame.math.Vector2(-self.moveDelay, self.moveDelay)
        elif dir == 7:
            return pygame.math.Vector2(-self.moveDelay, 0)
        elif dir == 8:
            return pygame.math.Vector2(-self.moveDelay, -self.moveDelay)
        raise UnboundLocalError

    def inside(self, rect):
        if rect.top <= self.playRect.top or rect.left <= self.playRect.left:
            return False

        if rect.bottom >= self.playRect.bottom or rect.right >= self.playRect.right:
            return False

        return True

    def update_animation(self):
        animations = self.get_animations()
        self.animationStep += 1
        if self.animationStep >= len(animations):
            self.animationStep = 0

        self.image = animations[self.animationStep]

    def die(self):
        self.kill()

    def zero(self):
        self.rect.x = -100
        self.rect.y = -100

    def reset(self):
        self.animationStep = 0
        self.image = self.get_animations()[self.animationStep]
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

    def get_animations(self):
        if isinstance(self.animations, list):
            return self.animations
        else:
            if not self.animationDirection:
                self.animationDirection = 'down'
            return self.animations[self.animationDirection]

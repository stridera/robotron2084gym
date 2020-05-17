import pygame
import random


class Base(pygame.sprite.Sprite):
    UP = 1
    UP_RIGHT = 2
    RIGHT = 3
    DOWN_RIGHT = 4
    DOWN = 5
    DOWN_LEFT = 6
    LEFT = 7
    UP_LEFT = 8

    REVERSE_DIR = [
        0,
        DOWN,
        DOWN_LEFT,
        LEFT,
        UP_LEFT,
        UP,
        UP_RIGHT,
        RIGHT,
        DOWN_RIGHT
    ]

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

        if sprites:
            self.image = self.get_animations()[self.animationStep]

    def update(self):
        pass

    def get_vector(self, direction, speed=None):
        speed = speed or self.moveSpeed
        if direction == 0:
            return pygame.math.Vector2(0)
        elif direction == self.UP:
            return pygame.math.Vector2(0, -speed)
        elif direction == self.UP_RIGHT:
            return pygame.math.Vector2(speed, -speed)
        elif direction == self.RIGHT:
            return pygame.math.Vector2(speed, 0)
        elif direction == self.DOWN_RIGHT:
            return pygame.math.Vector2(speed, speed)
        elif direction == self.DOWN:
            return pygame.math.Vector2(0, speed)
        elif direction == self.DOWN_LEFT:
            return pygame.math.Vector2(-speed, speed)
        elif direction == self.LEFT:
            return pygame.math.Vector2(-speed, 0)
        elif direction == self.UP_LEFT:
            return pygame.math.Vector2(-speed, -speed)
        raise UnboundLocalError

    def get_direction_string(self, direction):
        direction_string = 'down'
        if direction in [self.UP, self.UP_LEFT, self.UP_RIGHT]:
            direction_string = 'up'
        if direction in [self.DOWN, self.DOWN_LEFT, self.DOWN_RIGHT]:
            direction_string = 'down'
        if direction in [self.LEFT, self.UP_LEFT, self.DOWN_LEFT]:
            direction_string = 'left'
        if direction in [self.RIGHT, self.UP_RIGHT, self.DOWN_RIGHT]:
            direction_string = 'right'
        return direction_string

    def valid_move(self, direction):
        vector = self.get_vector(direction)
        test = self.rect.copy()
        test.center += vector

        if not self.inside(test):
            return False

        return True

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

    def die(self, sprite):
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

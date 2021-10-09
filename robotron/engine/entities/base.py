import pygame
import random
import math

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..engine import Engine


class Base(pygame.sprite.Sprite):
    """
    Base class for all sprites.
    """

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

    CARDINAL_DIRECTIONS = [UP, RIGHT, DOWN, LEFT]

    SCORE = 0

    def __init__(self, engine: 'Engine', **kwargs):
        super().__init__()
        self.engine = engine
        self.args = kwargs
        self.playRect = engine.get_play_area()

        self.cycle = None
        self.animations = self.get_animations()
        self.animationStep = 0
        self.animationDirection = None

        self.moveSpeed = 0  # Distance to move per step
        self.moveDelay = 0  # Time between steps
        self.moveDelayRemaining = self.moveDelay  # Time remaining until next step

        self.setup()

        self.update_animation()

        if 'xy' in kwargs.keys():
            self.rect = self.image.get_rect()
            self.rect.center = kwargs['xy']
        else:
            self.random_location()

    def get_animations(self):
        raise NotImplementedError()

    def get_engine(self):
        return self.engine

    def get_play_rect(self):
        return self.playRect

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
        if direction == self.UP:
            return 'up'
        if direction == self.DOWN:
            return 'down'
        if direction in [self.LEFT, self.UP_LEFT, self.DOWN_LEFT]:
            return 'left'
        if direction in [self.RIGHT, self.UP_RIGHT, self.DOWN_RIGHT]:
            return 'right'

    def valid_move(self, direction):
        vector = self.get_vector(direction)
        test = self.rect.copy()
        test.center += vector

        if not self.inside(test):
            return False

        return True

    def inside(self, rect):
        """
        Determine if the rect is inside the play area.

        args:
            rect (pygame.Rect): The rect to test

        returns:
            bool: True if the rect is inside the play area
        """
        if rect.top <= self.playRect.top or rect.left <= self.playRect.left:
            return False

        if rect.bottom >= self.playRect.bottom or rect.right >= self.playRect.right:
            return False

        return True

    def update_animation(self):
        if isinstance(self.animations, list):
            animations = self.animations
        else:
            animations = self.animations[self.animationDirection or 'down']

        self.animationStep += 1
        if self.animationStep >= (self.cycle or len(animations)):
            self.animationStep = 0

        self.image = animations[self.animationStep]

    def die(self, killer):
        """
        Kill the sprite.  Allows for overriding for different enemies.

        args:
            killer (pygame.Sprite): The sprite that did the killing.
        """
        self.kill()

    def zero(self):
        """
        Throw the sprite off screen.  Allows initialization out of view of the player.
        """
        self.rect.x = -100
        self.rect.y = -100

    def setup(self):
        """
        Setup the sprite.   Called at initialization.
        """
        self.reset()

    def reset(self):
        """
        Reset the sprite.  Called when the player dies.
        """
        self.animationStep = 0
        self.update_animation()
        self.random_location()

    def get_score(self):
        """
        Get the score for the player

        Returns:
            int: The score value of the sprite
        """
        return self.SCORE

    def random_direction(self):
        """
        Return a random integer representing one of the 8 cardinal directions.

        Returns:
            int: The directional value.
        """
        return random.randrange(1, 8)

    def random_location(self):
        """
        Place the sprite at a random location in the play area (ignoring the space right around the player).
        """
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

            # Prevent spawning too close to the player
            if playerBox.contains(self.rect):
                continue

            # Prevent sprites from overlapping
            if any(self.rect.colliderect(sprite.rect)
                    for sprite in self.engine.get_all_group() if self != sprite):
                continue

            validLocation = True

    def get_distance_to_sprite(self, sprite):
        x1, y1 = self.rect.center
        x2, y2 = sprite.rect.center
        return math.hypot(x1-x2, y1-y2)

    def get_distance_to_player(self):
        return self.get_distance_to_sprite(self.engine.get_player())

    def get_vector_to_point(self, xy, roundResult=False):
        x, y = xy
        dx, dy = x - self.rect.x, y - self.rect.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx, dy = dx / dist, dy / dist
        if roundResult:
            dx = round(dx)
            dy = round(dy)
        return pygame.Vector2(dx, dy)

    def move_toward_point(self, target, speed):
        vector = self.get_vector_to_point(target)
        self.rect.center += vector * speed

    def get_vector_to_player(self):
        return self.get_vector_to_point(self.engine.player.rect.center)

    def move_toward_player(self, speed):
        vector = self.get_vector_to_player()
        self.rect.center += vector * speed

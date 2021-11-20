"""Sprite Base Module"""
import math
import random
from typing import TYPE_CHECKING, Tuple

import pygame

if TYPE_CHECKING:
    from ..engine import Engine


class Base(pygame.sprite.Sprite):
    """
    Base class for all sprites.
    """
    # There are a lot of attributes.  That's fine.
    # pylint: disable=too-many-instance-attributes
    # Each subclass will setup it's own params in the setup() method, and since pylint doesn't like that,
    # I'm ignoring defining attributes outside of init.
    # pylint: disable=attribute-defined-outside-init

    SCORE = 0

    # Directions
    NONE = 0
    UP = 1
    UP_RIGHT = 2
    RIGHT = 3
    DOWN_RIGHT = 4
    DOWN = 5
    DOWN_LEFT = 6
    LEFT = 7
    UP_LEFT = 8

    def __init__(self, engine: 'Engine', **kwargs):
        super().__init__()
        self.engine = engine
        self.play_rect = self.engine.play_rect
        self.args = kwargs

        self.cycle = None
        self.animations = self.get_animations()
        self.animation_step = 0
        self.animation_direction = None

        self.speed = 0  # Distance to move per step
        self.move_delay = 0  # Time between steps
        self.move_countdown = self.move_delay  # Time remaining until next step

        self.setup()
        self.update_animation()

        if 'center' in kwargs:
            self.rect = self.image.get_rect()
            self.rect.center = kwargs['center']
        else:
            self.random_location()

    def get_animations(self):
        """
        Returns the images used to animate the sprite.

        Raises:
            NotImplementedError: Base class called directly or subclass didn't override.
        """
        raise NotImplementedError()

    def update(self):
        """ Called once per tick to update the sprites state. """

    def get_vector(self, direction: int, speed: float = None):
        """
        Return a vector for the given direction

        Args:
            direction (int): The direction we want the vector to move.
            speed (float, optional): The speed to assign to the vector. Defaults to `self.speed`.

        Returns:
            pygame.Vector2: The vector for the direction and speed given.
        """
        speed = speed or self.speed
        if direction == 0:
            return pygame.Vector2(0)
        elif direction == self.UP:
            return pygame.Vector2(0, -speed)
        elif direction == self.UP_RIGHT:
            return pygame.Vector2(speed, -speed)
        elif direction == self.RIGHT:
            return pygame.Vector2(speed, 0)
        elif direction == self.DOWN_RIGHT:
            return pygame.Vector2(speed, speed)
        elif direction == self.DOWN:
            return pygame.Vector2(0, speed)
        elif direction == self.DOWN_LEFT:
            return pygame.Vector2(-speed, speed)
        elif direction == self.LEFT:
            return pygame.Vector2(-speed, 0)
        elif direction == self.UP_LEFT:
            return pygame.Vector2(-speed, -speed)

        raise ValueError(f'Invalid direction: {direction}')

    def valid_move(self, direction: int):
        """
        Check to see if moving in the given direction is a valid move.  This is used to notify when
        we should turn for mobs that don't just try to walk into the wall.

        Args:
            direction (int): The direction the sprite wants to move.

        Returns:
            bool: Does moving in the direction result in a valid move or not?
        """
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
        if (rect.top <= self.play_rect.top or
                rect.left <= self.play_rect.left or
                rect.bottom >= self.play_rect.bottom or
                rect.right >= self.play_rect.right):
            return False

        return True

    def update_animation(self):
        """ Base class for updating the animation with the next one in the list. """
        if isinstance(self.animations, list):
            animations = self.animations
        else:
            animations = self.animations[self.animation_direction or 'down']

        if self.animation_step >= (self.cycle or len(animations)):
            self.animation_step = 0

        self.image = animations[self.animation_step]
        self.animation_step += 1

    def die(self, killer):
        """
        Kill the sprite.  Can be overridden for enemies that don't just vinish when hit.

        args:
            killer (pygame.Sprite): The sprite that did the killing.
        """
        del killer
        self.kill()

    def setup(self):
        """
        Setup the sprite.   Called at sprite initialization.  Default to calling reset.
        """
        self.reset()

    def reset(self):
        """
        Reset the sprite.  Called when the player dies.
        """
        self.animation_step = 0
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
        player_box = self.engine.get_player_box()

        valid_location = False
        tries = 0
        while not valid_location:
            tries += 1
            self.rect.x = self.play_rect.x + random.randrange(self.play_rect.width - sprite_width)
            self.rect.y = self.play_rect.y + random.randrange(self.play_rect.height - sprite_height)

            if tries > 25:
                print("Warning!  Enemy Placement Overflow.")
                break

            # Prevent spawning too close to the player
            if player_box.contains(self.rect):
                continue

            # Prevent sprites from overlapping
            if any(self.rect.colliderect(sprite.rect)
                    for sprite in self.engine.all_group if self != sprite):
                continue

            valid_location = True

    def get_distance_to_sprite(self, sprite: 'Base'):
        """
        Return the distance to a target sprite.

        Args:
            sprite (Base): The target sprite.

        Returns:
            float: The distance to the sprite.
        """
        my_x, my_y = self.rect.center
        their_x, their_y = sprite.rect.center
        return math.hypot(my_x-their_x, my_y-their_y)

    def get_distance_to_player(self):
        """
        Returns the distance to the player.

        Returns:
            float: Distance to to the player sprite.
        """
        return self.get_distance_to_sprite(self.engine.player)

    def get_vector_to_point(self, point: Tuple[int, int], round_results: bool = False):
        """
        Returns the distance to a point

        Args:
            point (Tuple[int, int]): The X, Y coords of our target point
            round_results (bool, optional): Should we round the results. Defaults to False.

        Returns:
            [type]: [description]
        """
        x, y = point
        dx, dy = x - self.rect.x, y - self.rect.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx, dy = dx / dist, dy / dist
        if round_results:
            dx = round(dx)
            dy = round(dy)
        return pygame.Vector2(dx, dy)

    def move_toward_point(self, point: Tuple[int, int], speed: float):
        """
        Move toward a given point at the given speed.

        Args:
            point (Tuple[int, int]): An x, y tuple specifying our target point.
            speed (float): The magnitude of the vector.
        """
        vector = self.get_vector_to_point(point)
        self.rect.center += vector * speed

    def get_vector_to_player(self):
        """
        Return a vector that points toward the player.

        Returns:
            pygame.Vector2: The vector pointing toward the player.
        """
        return self.get_vector_to_point(self.engine.player.rect.center)

    def move_toward_player(self, speed):
        """
        Move the sprite on a vector toward the player at the given speed.add()

        Args:
            speed (float): The magnitude of the vector.
        """
        vector = self.get_vector_to_player()
        self.rect.center += vector * speed

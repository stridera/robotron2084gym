""" Grunt Enemy Module """
import random

from .base import Base


class Grunt(Base):
    """
    Grunt Enemy

    Behavior:
        Grunts are simple.  They plot the nearest path to the player and move.
        They move fairly slow but speed up as the level progresses.

    """

    def get_animations(self):
        """Returns the images used to animate the sprite."""

        return self.engine.get_sprites(['grunt1', 'grunt2', 'grunt1', 'grunt3'])

    def reset(self):
        self.speed = 7
        self.move_delay = (5, 25)
        self.move_countdown = random.randrange(*self.move_delay)

    def move(self):
        """ Grunts move toward the player """
        self.update_animation()
        self.move_toward_player(self.speed)

    def update(self):
        if self.move_countdown <= 0:
            self.move()
            self.move_countdown = random.randrange(*self.move_delay)
        else:
            self.move_countdown -= 1

""" Grunt Enemy Module """
from .base import Base


class Grunt(Base):
    """
    Grunt Enemy

    Behavior:
        Grunts are simple.  They plot the nearest path to the player and move.
        They move fairly slow but speed up as the wave progresses.
        In the arcade, grunts accelerate over time - their delay between moves
        decreases the longer you stay on a wave.
    """
    SPEED_UP_INTERVAL = 300  # Frames between speed increases
    MIN_MOVE_DELAY = 1  # Fastest they can get

    def get_animations(self):
        """Returns the images used to animate the sprite."""

        return self.engine._get_sprites(['grunt1', 'grunt2', 'grunt1', 'grunt3'])

    def reset(self):
        self.speed = self.config('speed', 7)
        self.move_delay = self.config('move_delay', [5, 25])
        self.speed_up_interval = self.config('speed_up_interval', self.SPEED_UP_INTERVAL)
        self.min_move_delay = self.config('min_move_delay', self.MIN_MOVE_DELAY)
        self.move_countdown = self.random_int(self.move_delay[0], self.move_delay[1])
        self.speed_up_timer = self.speed_up_interval
        self.update_animation()
        self.random_location()

    def move(self):
        """ Grunts move toward the player """
        self.update_animation()
        self.move_toward_player(self.speed)

    def update(self):
        # Speed up over time within a wave
        self.speed_up_timer -= 1
        if self.speed_up_timer <= 0:
            self.speed_up_timer = self.speed_up_interval
            if self.move_delay[0] > self.min_move_delay:
                self.move_delay = (max(self.min_move_delay, self.move_delay[0] - 1),
                                   max(self.min_move_delay, self.move_delay[1] - 2))

        if self.move_countdown <= 0:
            self.move()
            self.move_countdown = self.random_int(self.move_delay[0], self.move_delay[1] + 1)
        else:
            self.move_countdown -= 1

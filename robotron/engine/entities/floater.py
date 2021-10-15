from .base import Base


class Floater(Base):
    """
    Displays a floating sprite for a short time.  Doesn't interact, just vanishes after the delay is done.
    """

    def setup(self):
        self.delay = self.args['delay'] if 'delay' in self.args.keys() else 15

    def get_animations(self):
        """Returns the images used to animate the sprite."""

        keys = self.args.keys()

        if 'sprite' in keys:
            sprite = self.args['sprite']
        elif 'sprite_name' in keys:
            sprite = self.engine.get_sprite(str(self.args['sprite_name']))
        else:
            raise ValueError("Invalid sprite passed.")

        return [sprite]

    def update(self):
        self.delay -= 1
        if self.delay == 0:
            self.kill()

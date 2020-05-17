import pygame
from . import config

from .engine import Engine


class Robotron:

    def __init__(self, level=1, fps=30):
        (top, left, bottom, right) = config.PLAY_AREA
        self.playArea = pygame.Rect(left, top, right - left, bottom - top)
        self.engine = Engine(config.SCREEN_SIZE, self.playArea, config.WAVES, level, fps)

    def reset(self):
        self.engine.reset()
        return self.engine.get_image()

    def step(self, action):
        move = action // 9
        shoot = action % 9
        self.engine.handle_input(move, shoot)
        (score, lives, dead) = self.engine.update()
        # print(score, lives, dead)
        image = self.draw()
        return image, score, dead, None

    def draw(self):
        self.engine.draw()
        return self.engine.get_image()

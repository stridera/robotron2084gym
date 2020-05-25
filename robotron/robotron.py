import pygame
import numpy as np
import cv2
from . import config

from .engine import Engine


class Robotron:

    def __init__(self, level=1, fps=30):
        (top, left, bottom, right) = config.PLAY_AREA
        self.playArea = pygame.Rect(left, top, right - left, bottom - top)
        self.engine = Engine(config.SCREEN_SIZE, self.playArea, config.WAVES, level, fps)

        self.level = 0
        self.lives = 3
        self.dead = False

    def crop(self, image, coords):
        (left, top, right, bottom) = coords
        return image[left:right, top:bottom]

    def reset(self):
        self.engine.reset()

    def step(self, action):
        move = action // 9
        shoot = action % 9
        self.engine.handle_input(move, shoot)
        (image, reward, score, lives, level, dead) = self.engine.update()

        self.lives = lives
        self.level = level
        self.dead = dead

        return image, reward, dead or level > 1, {'score': score, 'level': level, 'lives': lives}

    def get_state(self):
        image = self.engine.get_image()
        image = self.crop(image, config.PLAY_AREA)
        image = np.transpose(image, (1, 0, 2))
        image = cv2.resize(image, (84, 84), interpolation=cv2.INTER_LINEAR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) / 255.
        return image

    def render(self):
        self.engine.render()

    def level(self):
        return self.level

    def lives(self):
        return self.lives

    def game_over(self):
        return self.dead
